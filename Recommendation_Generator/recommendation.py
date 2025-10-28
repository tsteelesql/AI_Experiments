"""
Blog Post Generator with Multi-Agent Review System
Analyzes Python files and generates technical blog posts using Ollama and LangChain
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import threading
from tkinter import filedialog
import pyperclip

import customtkinter as ctk
from langchain_ollama import ChatOllama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA


@dataclass
class PythonFile:
    """Represents a Python file with its metadata"""
    path: str
    content: str
    relative_path: str


class PythonFileCollector:
    """Collects and processes Python files from a directory"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        
    def collect_files(self) -> List[PythonFile]:
        """Recursively collect all Python files from the directory"""
        python_files = []
        
        for py_file in self.root_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                relative_path = py_file.relative_to(self.root_dir)
                python_files.append(PythonFile(
                    path=str(py_file),
                    content=content,
                    relative_path=str(relative_path)
                ))
                print(f"✓ Collected: {relative_path}")
            except Exception as e:
                print(f"✗ Error reading {py_file}: {e}")
                
        return python_files


class RAGContextBuilder:
    """Builds RAG context from Python files using LangChain and Chroma"""
    
    def __init__(self, model_name: str = "llama3.2"):
        self.embeddings = OllamaEmbeddings(model=model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\nclass ", "\ndef ", "\n", " ", ""]
        )
        
    def build_vectorstore(self, files: List[PythonFile]) -> Chroma:
        """Create a vector store from Python files"""
        documents = []
        metadatas = []
        
        for file in files:
            chunks = self.text_splitter.split_text(file.content)
            for chunk in chunks:
                documents.append(chunk)
                metadatas.append({
                    "source": file.relative_path,
                    "full_path": file.path
                })
        
        print(f"\n📚 Creating vector store with {len(documents)} chunks...")
        vectorstore = Chroma.from_texts(
            texts=documents,
            embedding=self.embeddings,
            metadatas=metadatas
        )
        
        return vectorstore


class BlogPostGenerator:
    """Generates blog posts using Ollama and RAG context"""
    
    def __init__(self, model_name: str = "llama3.2", temperature: float = 0.7):
        self.llm = ChatOllama(model=model_name, temperature=temperature)
        
    def generate_post(self, vectorstore: Chroma, files: List[PythonFile]) -> str:
        """Generate initial blog post from Python files context"""
        
        # Create retrieval chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
        )
        
        # Build context summary
        file_list = "\n".join([f"- {f.relative_path}" for f in files])
        
        prompt = f"""You are a technical blog writer. Analyze the following Python codebase and create an engaging blog post.

Files in the codebase:
{file_list}

Your task:
1. Identify the main purpose and functionality of the code
2. Highlight interesting Python use cases, patterns, and techniques used
3. Extract key learning opportunities for readers
4. Include relevant code snippets with explanations
5. Write in an engaging, educational tone

Create a comprehensive blog post (800-1200 words) that would help developers learn from this code.

Focus on:
- What problems does this code solve?
- What Python features/libraries are used effectively?
- What can developers learn from this implementation?
- Include 2-3 code examples with explanations

Generate the blog post:"""

        print("\n✍️  Generating initial blog post...")
        response = qa_chain.invoke(prompt)
        
        # Extract the result from the response dictionary
        if isinstance(response, dict):
            return response.get('result', str(response))
        return str(response)


class GrammarEditorAgent:
    """AI agent that reviews and corrects grammar"""
    
    def __init__(self, model_name: str = "llama3.2"):
        self.llm = ChatOllama(model=model_name, temperature=0.3)
        
    def edit(self, content: str) -> str:
        """Review and fix grammatical errors"""
        
        prompt = f"""You are a professional editor specializing in technical writing. 
Review the following blog post for grammatical errors, clarity, and readability.

Instructions:
- Fix any grammatical errors
- Improve sentence structure where needed
- Ensure consistent tone and style
- Keep all technical content and code examples intact
- Maintain the original meaning and structure
- Do not add or remove sections

Blog post to edit:

{content}

Provide the edited version:"""

        print("\n📝 Running grammar and style review...")
        return self.llm.invoke(prompt)


class TechnicalEditorAgent:
    """AI agent that reviews technical accuracy and code examples"""
    
    def __init__(self, model_name: str = "llama3.2"):
        self.llm = ChatOllama(model=model_name, temperature=0.2)
        
    def edit(self, content: str) -> str:
        """Review technical accuracy and validate code examples"""
        
        prompt = f"""You are a senior Python developer and technical editor.
Review this blog post for technical accuracy and code correctness.

Instructions:
- Verify all code examples are syntactically correct
- Check that technical explanations are accurate
- Ensure code examples follow Python best practices
- Validate that imports and usage are correct
- Flag any potential bugs or issues in code snippets
- Fix any technical inaccuracies
- Keep the writing style and structure intact

Blog post to review:

{content}

Provide the technically reviewed version:"""

        print("\n🔍 Running technical review...")
        return self.llm.invoke(prompt)


class FinalPolishAgent:
    """AI agent that creates the final concise version"""
    
    def __init__(self, model_name: str = "llama3.2"):
        self.llm = ChatOllama(model=model_name, temperature=0.4)
        
    def polish(self, content: str) -> str:
        """Create final polished and concise version"""
        
        prompt = f"""You are a content strategist finalizing a technical blog post.
Create the final, polished version that is concise yet comprehensive.

Instructions:
- Remove any redundancy or repetition
- Ensure the post flows logically
- Keep it engaging and readable
- Maintain all key technical insights
- Preserve all code examples
- Aim for clarity and impact
- Add a compelling title and brief introduction if missing

Blog post to polish:

{content}

Provide the final polished version:"""

        print("\n✨ Creating final polished version...")
        return self.llm.invoke(prompt)


class BlogPostPipeline:
    """Complete pipeline for generating blog posts from Python code"""
    
    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name
        self.collector = None
        self.rag_builder = RAGContextBuilder(model_name)
        self.generator = BlogPostGenerator(model_name)
        self.grammar_editor = GrammarEditorAgent(model_name)
        self.technical_editor = TechnicalEditorAgent(model_name)
        self.polisher = FinalPolishAgent(model_name)
        
    def generate(self, directory: str, output_file: str = "blog_post.md", progress_callback=None) -> str:
        """Run the complete pipeline"""
        
        def log(message: str):
            print(message)
            if progress_callback:
                progress_callback(message)
        
        log("=" * 70)
        log("🚀 BLOG POST GENERATOR PIPELINE")
        log("=" * 70)
        
        # Step 1: Collect Python files
        log(f"\n📂 Step 1: Collecting Python files from {directory}")
        self.collector = PythonFileCollector(directory)
        files = self.collector.collect_files()
        
        if not files:
            raise ValueError(f"No Python files found in {directory}")
            
        log(f"\n✓ Found {len(files)} Python files")
        
        # Step 2: Build RAG context
        log("\n🔧 Step 2: Building RAG context")
        vectorstore = self.rag_builder.build_vectorstore(files)
        
        # Step 3: Generate initial post
        log("\n📖 Step 3: Generating blog post")
        initial_post = self.generator.generate_post(vectorstore, files)
        
        # Step 4: Grammar review
        log("\n📋 Step 4: Grammar and style editing")
        grammar_edited = self.grammar_editor.edit(initial_post)
        
        # Step 5: Technical review
        log("\n🔬 Step 5: Technical review")
        tech_edited = self.technical_editor.edit(grammar_edited)
        
        # Step 6: Final polish
        log("\n💎 Step 6: Final polish")
        final_post = self.polisher.polish(tech_edited)
        
        # Save output
        log(f"\n💾 Saving to {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_post)
            
        log("\n" + "=" * 70)
        log("✅ BLOG POST GENERATION COMPLETE!")
        log("=" * 70)
        log(f"\n📄 Output saved to: {output_file}")
        
        return final_post


class BlogPostViewerWindow:
    """Separate window to display the generated blog post"""
    
    def __init__(self, blog_content: str):
        self.blog_content = blog_content
        
        # Create new window
        self.window = ctk.CTkToplevel()
        self.window.title("Generated Blog Post")
        self.window.geometry("1000x800")
        
        # Make window modal
        self.window.grab_set()
        self.window.focus_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the viewer UI"""
        
        # Main container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="📄 Your Generated Blog Post",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Blog post content in scrollable textbox
        self.content_text = ctk.CTkTextbox(
            main_frame,
            font=ctk.CTkFont(size=20),
            wrap="word"
        )
        self.content_text.pack(fill="both", expand=True, pady=(0, 20))
        self.content_text.insert("1.0", self.blog_content)
        self.content_text.configure(state="disabled")  # Make read-only
        
        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 10))
        
        # Copy button
        copy_btn = ctk.CTkButton(
            button_frame,
            text="📋 Copy to Clipboard",
            command=self.copy_to_clipboard,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2B7A0B",
            hover_color="#1F5708"
        )
        copy_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # Close button
        close_btn = ctk.CTkButton(
            button_frame,
            text="✖ Close",
            command=self.window.destroy,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#7A0B0B",
            hover_color="#5C0808"
        )
        close_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
        
    def copy_to_clipboard(self):
        """Copy blog post content to clipboard"""
        try:
            pyperclip.copy(self.blog_content)
            self.status_label.configure(
                text="✅ Copied to clipboard!",
                text_color="green"
            )
            # Clear status after 3 seconds
            self.window.after(3000, lambda: self.status_label.configure(text=""))
        except Exception as e:
            self.status_label.configure(
                text=f"❌ Failed to copy: {str(e)}",
                text_color="red"
            )


class BlogGeneratorGUI:
    """CustomTkinter GUI for Blog Post Generator"""
    
    def __init__(self):
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Blog Post Generator")
        self.root.geometry("800x700")
        
        # Variables
        self.directory_path = None
        self.output_file = "generated_blog_post.md"
        self.model_name = "llama3.2"
        
        # Initialize pipeline (will be created when needed)
        self.pipeline = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🚀 Blog Post Generator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Directory Selection Section
        dir_frame = ctk.CTkFrame(main_frame)
        dir_frame.pack(fill="x", pady=10)
        
        dir_label = ctk.CTkLabel(
            dir_frame,
            text="Source Directory:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        dir_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.dir_display = ctk.CTkLabel(
            dir_frame,
            text="No directory selected",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.dir_display.pack(anchor="w", padx=10, pady=(0, 10))
        
        browse_btn = ctk.CTkButton(
            dir_frame,
            text="📂 Browse Directory",
            command=self.browse_directory,
            height=35
        )
        browse_btn.pack(pady=(0, 10), padx=10)
        
        # Configuration Section
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill="x", pady=10)
        
        config_label = ctk.CTkLabel(
            config_frame,
            text="Configuration:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        config_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Model selection
        model_frame = ctk.CTkFrame(config_frame)
        model_frame.pack(fill="x", padx=10, pady=5)
        
        model_label = ctk.CTkLabel(model_frame, text="Model:")
        model_label.pack(side="left", padx=5)
        
        self.model_dropdown = ctk.CTkComboBox(
            model_frame,
            values=["llama3.2", "llama3.1", "llama3", "mistral", "codellama"],
            command=self.on_model_change
        )
        self.model_dropdown.set("llama3.2")
        self.model_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        
        # Output file
        output_frame = ctk.CTkFrame(config_frame)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        output_label = ctk.CTkLabel(output_frame, text="Output File:")
        output_label.pack(side="left", padx=5)
        
        self.output_entry = ctk.CTkEntry(output_frame)
        self.output_entry.insert(0, "generated_blog_post.md")
        self.output_entry.pack(side="left", padx=5, fill="x", expand=True, pady=10)
        
        # Generate Button
        self.generate_btn = ctk.CTkButton(
            main_frame,
            text="✨ Generate Blog Post",
            command=self.start_generation,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2B7A0B",
            hover_color="#1F5708"
        )
        self.generate_btn.pack(pady=20)
        
        # Progress Section
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="both", expand=True, pady=10)
        
        progress_label = ctk.CTkLabel(
            progress_frame,
            text="Progress:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        progress_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Progress text box
        self.progress_text = ctk.CTkTextbox(
            progress_frame,
            height=300,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.progress_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Ready to generate",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.pack(pady=5)
        
    def browse_directory(self):
        """Open file dialog to select directory"""
        # Create a temporary Toplevel window for the file dialog
        dialog_window = ctk.CTkToplevel(self.root)
        dialog_window.withdraw()  # Hide the window
        
        directory = filedialog.askdirectory(
            parent=dialog_window,
            title="Select Python Project Directory",
            initialdir=os.path.expanduser("~")
        )
        
        # Destroy the dialog window immediately after selection
        dialog_window.destroy()
        
        if directory:
            self.directory_path = directory
            self.dir_display.configure(
                text=directory,
                text_color="white"
            )
            self.log_progress(f"Selected directory: {directory}")
            
    def on_model_change(self, choice):
        """Handle model selection change"""
        self.model_name = choice
        self.log_progress(f"Model changed to: {choice}")
        
    def log_progress(self, message: str):
        """Add message to progress text box"""
        self.progress_text.insert("end", message + "\n")
        self.progress_text.see("end")
        self.root.update_idletasks()
        
    def update_status(self, message: str, color: str = "gray"):
        """Update status label"""
        self.status_label.configure(text=message, text_color=color)
        self.root.update_idletasks()
        
    def start_generation(self):
        """Start the blog post generation process"""
        if not self.directory_path:
            self.update_status("⚠️ Please select a directory first", "orange")
            self.log_progress("ERROR: No directory selected")
            return
            
        self.output_file = self.output_entry.get()
        
        if not self.output_file:
            self.update_status("⚠️ Please enter an output filename", "orange")
            self.log_progress("ERROR: No output filename specified")
            return
        
        # Disable generate button
        self.generate_btn.configure(state="disabled", text="⏳ Generating...")
        self.update_status("🔄 Generation in progress...", "yellow")
        
        # Clear progress
        self.progress_text.delete("1.0", "end")
        
        # Run generation in separate thread to prevent UI freezing
        thread = threading.Thread(target=self.run_generation)
        thread.daemon = True
        thread.start()
        
    def run_generation(self):
        """Run the generation pipeline in a separate thread"""
        try:
            # Create pipeline
            self.pipeline = BlogPostPipeline(model_name=self.model_name)
            
            # Generate blog post
            final_post = self.pipeline.generate(
                directory=self.directory_path,
                output_file=self.output_file,
                progress_callback=self.log_progress
            )
            
            # Update UI on success
            self.root.after(0, lambda: self.update_status(
                f"✅ Blog post generated successfully! Saved to {self.output_file}",
                "green"
            ))
            
            self.root.after(0, lambda: self.log_progress(
                f"\n{'='*70}\n✅ SUCCESS!\n{'='*70}"
            ))
            
            # Open viewer window with the blog post
            self.root.after(0, lambda: self.show_blog_post(final_post))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.update_status(
                f"❌ Generation failed: {str(e)}",
                "red"
            ))
            self.root.after(0, lambda: self.log_progress(f"\n❌ ERROR: {error_msg}"))
            
        finally:
            # Re-enable generate button
            self.root.after(0, lambda: self.generate_btn.configure(
                state="normal",
                text="✨ Generate Blog Post"
            ))
    
    def show_blog_post(self, blog_content: str):
        """Display the blog post in a new window"""
        BlogPostViewerWindow(blog_content)
            
    def run(self):
        """Start the GUI"""
        self.root.mainloop()


def main():
    """Main entry point with GUI"""
    app = BlogGeneratorGUI()
    app.run()


if __name__ == "__main__":
    main()