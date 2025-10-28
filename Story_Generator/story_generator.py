"""
Story Generator using LangChain, Ollama (Llama3.2), and ChromaDB

This script generates stories from a list of words using a multi-agent approach:
1. Word vectorization using ChromaDB
2. Writer agent that creates a story from the words
3. Editor agent that checks for grammatical errors
4. Publication step with GUI for final output

Requirements:
- langchain
- langchain-community
- langchain-core
- langsmith
- chromadb
- ollama
- tkinter
- pyperclip
"""

import os
import sys
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import chromadb
from chromadb import Client
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import VectorStore
import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyperclip

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("story_generator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class StoryGenerationConfig:
    """Configuration for story generation"""
    ollama_model: str = "llama3.2"
    chroma_collection_name: str = "story_words"
    chroma_persist_directory: str = "./chroma_db"
    max_tokens: int = 2048
    temperature: float = 0.7

class WordVectorizer:
    """Handles vectorization of words using ChromaDB"""
    
    def __init__(self, config: StoryGenerationConfig):
        self.config = config
        self.client = chromadb.PersistentClient(path=config.chroma_persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=config.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Word vectorizer initialized")
    
    def add_words(self, words: List[str]) -> None:
        """Add words to the vector store"""
        try:
            # Create documents from words
            documents = [Document(page_content=word) for word in words]
            
            # Add to ChromaDB
            self.collection.add(
                documents=words,
                ids=[str(i) for i in range(len(words))]
            )
            logger.info(f"Added {len(words)} words to vector store")
        except Exception as e:
            logger.error(f"Error adding words to vector store: {e}")
            raise
    
    def search_words(self, query: str, n_results: int = 5) -> List[str]:
        """Search for similar words"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            logger.error(f"Error searching words: {e}")
            return []

class WriterAgent:
    """Agent that generates stories from a list of words"""
    
    def __init__(self, config: StoryGenerationConfig):
        self.config = config
        self.llm = ChatOllama(
            model=config.ollama_model,
            temperature=config.temperature,
            num_predict=config.max_tokens
        )
        
        # Prompt template for story generation
        self.prompt_template = PromptTemplate.from_template(
            """You are a creative writer. Create a compelling story using the following words:
            Words: {words}
            
            Instructions:
            {instructions}
            
            Story:
            """
        )
        
        self.chain = RunnableSequence(
            steps=[
                self.prompt_template,
                self.llm,
                StrOutputParser()
            ]
        )
        logger.info("Writer agent initialized")
    
    def generate_story(self, words: List[str], instructions: str = "") -> str:
        """Generate a story from the given words"""
        try:
            words_str = ", ".join(words)
            result = self.chain.invoke({
                "words": words_str,
                "instructions": instructions
            })
            logger.info("Story generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            raise

class EditorAgent:
    """Agent that checks for grammatical errors in stories"""
    
    def __init__(self, config: StoryGenerationConfig):
        self.config = config
        self.llm = ChatOllama(
            model=config.ollama_model,
            temperature=config.temperature,
            num_predict=config.max_tokens
        )
        
        # Prompt template for grammar checking
        self.prompt_template = PromptTemplate.from_template(
            """You are a grammar and style editor. Review the following story for grammatical errors and style improvements.
            If you find errors, provide a corrected version. If there are no errors, just say "No errors found".
            
            Story:
            {story}
            
            Your response:
            """
        )
        
        self.chain = RunnableSequence(
            steps=[
                self.prompt_template,
                self.llm,
                StrOutputParser()
            ]
        )
        logger.info("Editor agent initialized")
    
    def check_story(self, story: str) -> Dict[str, Any]:
        """Check story for errors and return corrections"""
        try:
            result = self.chain.invoke({"story": story})
            logger.info("Story checked for errors")
            
            # Determine if there were errors
            if "No errors found" in result.lower():
                return {"has_errors": False, "correction": story}
            else:
                return {"has_errors": True, "correction": result}
        except Exception as e:
            logger.error(f"Error checking story: {e}")
            raise

class StoryGenerator:
    """Main story generation workflow"""
    
    def __init__(self, config: StoryGenerationConfig = None):
        self.config = config or StoryGenerationConfig()
        self.vectorizer = WordVectorizer(self.config)
        self.writer = WriterAgent(self.config)
        self.editor = EditorAgent(self.config)
        self.history = []
        logger.info("Story generator initialized")
    
    def process_words(self, words: List[str]) -> None:
        """Process a list of words for story generation"""
        try:
            self.vectorizer.add_words(words)
            logger.info(f"Processed {len(words)} words")
        except Exception as e:
            logger.error(f"Error processing words: {e}")
            raise
    
    def generate_story(self, words: List[str], instructions: str = "") -> str:
        """Generate a story from words with optional instructions"""
        try:
            # Generate initial story
            story = self.writer.generate_story(words, instructions)
            
            # Add to history
            self.history.append({
                "step": "initial",
                "story": story,
                "timestamp": datetime.now()
            })
            
            # Check for errors
            check_result = self.editor.check_story(story)
            
            # If errors found, apply correction
            if check_result["has_errors"]:
                corrected_story = check_result["correction"]
                self.history.append({
                    "step": "corrected",
                    "story": corrected_story,
                    "timestamp": datetime.now()
                })
                return corrected_story
            else:
                return story
        except Exception as e:
            logger.error(f"Error in story generation: {e}")
            raise

class StoryPublisher:
    """Handles publishing the final story to a GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Story Generator")
        self.root.geometry("800x600")
        
        # Create GUI elements
        self.create_widgets()
        logger.info("Story publisher GUI initialized")
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Title label
        title_label = tk.Label(self.root, text="Generated Story", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Story text area
        self.story_text = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            width=80, 
            height=25,
            font=("Arial", 12)
        )
        self.story_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Copy button
        copy_button = tk.Button(
            self.root, 
            text="Copy to Clipboard", 
            command=self.copy_to_clipboard,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white"
        )
        copy_button.pack(pady=5)
        
        # Exit button
        exit_button = tk.Button(
            self.root, 
            text="Exit", 
            command=self.root.destroy,
            font=("Arial", 12),
            bg="#f44336",
            fg="white"
        )
        exit_button.pack(pady=5)
    
    def display_story(self, story: str):
        """Display the story in the GUI"""
        self.story_text.delete(1.0, tk.END)
        self.story_text.insert(tk.END, story)
        self.story_text.config(state=tk.DISABLED)
        logger.info("Story displayed in GUI")
    
    def copy_to_clipboard(self):
        """Copy the story to clipboard"""
        story = self.story_text.get(1.0, tk.END)
        pyperclip.copy(story)
        messagebox.showinfo("Copied", "Story copied to clipboard!")
        logger.info("Story copied to clipboard")
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def main():
    """Main function to demonstrate the story generation workflow"""
    # Initialize the story generator
    config = StoryGenerationConfig()
    generator = StoryGenerator(config)
    
    # Example words for story generation
    words = ["dragon", "castle", "knight", "magic", "quest", "treasure", "princess"]
    
    # Process words
    generator.process_words(words)
    
    # Generate story with instructions
    instructions = "Create a fantasy story about a brave knight on a quest to save a princess from a dragon."
    story = generator.generate_story(words, instructions)
    
    # Display in GUI
    publisher = StoryPublisher()
    publisher.display_story(story)
    publisher.run()

if __name__ == "__main__":
    main()
