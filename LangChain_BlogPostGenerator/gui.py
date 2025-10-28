"""
GUI components for the Blog Post Generator
"""

import os
import threading
import logging
from pathlib import Path
from typing import Optional

import customtkinter as ctk
from tkinter import filedialog
import pyperclip

from pipeline import BlogPostPipeline
from models import GenerationResult
from config import config


logger = logging.getLogger(__name__)


class BlogPostViewerWindow:
    """Separate window to display the generated blog post"""
    
    def __init__(self, blog_content: str):
        self.blog_content = blog_content
        
        # Create new window
        self.window = ctk.CTkToplevel()
        self.window.title("Generated Blog Post")
        self.window.geometry(config.viewer_size)
        
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
            logger.error(f"Failed to copy to clipboard: {e}")
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
        self.root.title(config.window_title)
        self.root.geometry(config.window_size)
        
        # Variables
        self.directory_path: Optional[str] = None
        self.output_file = config.default_output_file
        self.model_name = config.model.name
        
        # Initialize pipeline (will be created when needed)
        self.pipeline: Optional[BlogPostPipeline] = None
        
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
        self._setup_directory_section(main_frame)
        
        # Configuration Section
        self._setup_configuration_section(main_frame)
        
        # Generate Button
        self._setup_generate_button(main_frame)
        
        # Progress Section
        self._setup_progress_section(main_frame)
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Ready to generate",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.pack(pady=5)
        
    def _setup_directory_section(self, parent):
        """Setup directory selection section"""
        dir_frame = ctk.CTkFrame(parent)
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
        
    def _setup_configuration_section(self, parent):
        """Setup configuration section"""
        config_frame = ctk.CTkFrame(parent)
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
            values=config.model.available_models,
            command=self.on_model_change
        )
        self.model_dropdown.set(config.model.name)
        self.model_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        
        # Output file
        output_frame = ctk.CTkFrame(config_frame)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        output_label = ctk.CTkLabel(output_frame, text="Output File:")
        output_label.pack(side="left", padx=5)
        
        self.output_entry = ctk.CTkEntry(output_frame)
        self.output_entry.insert(0, config.default_output_file)
        self.output_entry.pack(side="left", padx=5, fill="x", expand=True, pady=10)
        
    def _setup_generate_button(self, parent):
        """Setup generate button"""
        self.generate_btn = ctk.CTkButton(
            parent,
            text="✨ Generate Blog Post",
            command=self.start_generation,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2B7A0B",
            hover_color="#1F5708"
        )
        self.generate_btn.pack(pady=20)
        
    def _setup_progress_section(self, parent):
        """Setup progress section"""
        progress_frame = ctk.CTkFrame(parent)
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
        
    def browse_directory(self):
        """Open file dialog to select directory"""
        try:
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
                
        except Exception as e:
            logger.error(f"Error browsing directory: {e}")
            self.update_status(f"❌ Error selecting directory: {str(e)}", "red")
            
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
            result = self.pipeline.generate(
                directory=self.directory_path,
                output_file=self.output_file,
                progress_callback=self.log_progress
            )
            
            # Update UI based on result
            if result.success:
                self.root.after(0, lambda: self.update_status(
                    f"✅ Blog post generated successfully! Saved to {self.output_file}",
                    "green"
                ))
                
                self.root.after(0, lambda: self.log_progress(
                    f"\n{'='*70}\n✅ SUCCESS!\n{'='*70}"
                ))
                
                # Open viewer window with the blog post
                if result.content:
                    self.root.after(0, lambda: self.show_blog_post(result.content))
            else:
                error_msg = result.error or "Unknown error occurred"
                self.root.after(0, lambda: self.update_status(
                    f"❌ Generation failed: {error_msg}",
                    "red"
                ))
                self.root.after(0, lambda: self.log_progress(f"\n❌ ERROR: {error_msg}"))
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
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
