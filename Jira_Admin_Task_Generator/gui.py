"""
GUI implementation for the Jira Admin Task Generator using CustomTkinter.
"""

import customtkinter as ctk
from tkinter import scrolledtext
import threading
from typing import Dict, Any, Optional

from history_manager import QuestionHistory
from task_generator import TaskGenerator


class JiraTaskGeneratorGUI:
    """Main GUI class for the Jira Admin Task Generator."""
    
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("light")  # "light" or "dark"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Jira Admin Task Generator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Initialize components
        self.history_manager = QuestionHistory()
        self.task_generator = TaskGenerator(self.history_manager)
        
        # State variables
        self.hint_visible = False
        self.solution_visible = False
        self.history_visible = False
        self.current_task: Optional[Dict[str, Any]] = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create and arrange all GUI widgets."""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Jira Admin Task Generator", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Generate button (centered)
        self.generate_button = ctk.CTkButton(
            main_frame,
            text="Generate New Task",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            command=self.generate_task
        )
        self.generate_button.pack(pady=(0, 20), fill="x")
        
        # Question section
        question_label = ctk.CTkLabel(
            main_frame, 
            text="User Request:", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        question_label.pack(anchor="w", pady=(0, 5))
        
        self.question_text = scrolledtext.ScrolledText(
            main_frame,
            height=4,
            font=("Arial", 20),
            wrap="word",
            state="disabled"
        )
        self.question_text.pack(fill="x", pady=(0, 20))
        
        # Hint section
        hint_frame = ctk.CTkFrame(main_frame)
        hint_frame.pack(fill="x", pady=(0, 10))
        
        hint_button_frame = ctk.CTkFrame(hint_frame)
        hint_button_frame.pack(fill="x", padx=10, pady=10)
        
        self.hint_button = ctk.CTkButton(
            hint_button_frame,
            text="Show Hint",
            command=self.toggle_hint,
            width=140,
            font=ctk.CTkFont(size=20)
        )
        self.hint_button.pack(side="left", padx=(0, 10))
        
        self.hint_status = ctk.CTkLabel(
            hint_button_frame,
            text="",
            font=ctk.CTkFont(size=20)
        )
        self.hint_status.pack(side="left")
        
        self.hint_text = scrolledtext.ScrolledText(
            hint_frame,
            height=3,
            font=("Arial", 20),
            wrap="word",
            state="disabled"
        )
        # Don't pack initially - will be packed when shown
        
        # Solution section
        solution_frame = ctk.CTkFrame(main_frame)
        solution_frame.pack(fill="x", pady=(0, 20))
        
        solution_button_frame = ctk.CTkFrame(solution_frame)
        solution_button_frame.pack(fill="x", padx=10, pady=10)
        
        self.solution_button = ctk.CTkButton(
            solution_button_frame,
            text="Show Solution",
            command=self.toggle_solution,
            width=140,
            font=ctk.CTkFont(size=20)
        )
        self.solution_button.pack(side="left", padx=(0, 10))
        
        self.solution_status = ctk.CTkLabel(
            solution_button_frame,
            text="",
            font=ctk.CTkFont(size=20)
        )
        self.solution_status.pack(side="left")
        
        self.solution_text = scrolledtext.ScrolledText(
            solution_frame,
            height=6,
            font=("Arial", 20),
            wrap="word",
            state="disabled"
        )
        # Don't pack initially - will be packed when shown
        
        # History section
        history_frame = ctk.CTkFrame(main_frame)
        history_frame.pack(fill="x", pady=(10, 10))
        
        history_header_frame = ctk.CTkFrame(history_frame)
        history_header_frame.pack(fill="x", padx=10, pady=10)
        
        history_label = ctk.CTkLabel(
            history_header_frame,
            text="Question History",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        history_label.pack(side="left")
        
        self.history_button = ctk.CTkButton(
            history_header_frame,
            text="Show History",
            command=self.toggle_history,
            width=140,
            font=ctk.CTkFont(size=14)
        )
        self.history_button.pack(side="right")
        
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            height=4,
            font=("Arial", 12),
            wrap="word",
            state="disabled"
        )
        # Don't pack initially - will be packed when shown
        
        # Exit button
        self.exit_button = ctk.CTkButton(
            main_frame,
            text="Exit",
            command=self.root.quit,
            width=120,
            font=ctk.CTkFont(size=20)
        )
        self.exit_button.pack(pady=(10, 0))
        
    def generate_task(self):
        """Generate a new task in a separate thread to prevent GUI freezing."""
        def task_generation():
            # Update UI to show loading
            self.question_text.config(state="normal")
            self.question_text.delete(1.0, "end")
            self.question_text.insert(1.0, "Generating task... Please wait.")
            self.question_text.config(state="disabled")
            
            # Generate the task
            self.current_task = self.task_generator.generate_task()
            
            # Update UI with results
            self.root.after(0, self.update_task_display)
        
        # Start task generation in a separate thread
        thread = threading.Thread(target=task_generation)
        thread.daemon = True
        thread.start()
        
    def update_task_display(self):
        """Update the GUI with the generated task."""
        if self.current_task:
            # Update question
            self.question_text.config(state="normal")
            self.question_text.delete(1.0, "end")
            self.question_text.insert(1.0, self.current_task['question'])
            self.question_text.config(state="disabled")
            
            # Update hint and solution text
            self.hint_text.config(state="normal")
            self.hint_text.delete(1.0, "end")
            self.hint_text.insert(1.0, self.current_task['hint'])
            self.hint_text.config(state="disabled")
            
            self.solution_text.config(state="normal")
            self.solution_text.delete(1.0, "end")
            self.solution_text.insert(1.0, self.current_task['solution'])
            self.solution_text.config(state="disabled")
            
            # Reset visibility states
            self.hint_visible = False
            self.solution_visible = False
            self.hint_text.pack_forget()
            self.solution_text.pack_forget()
            self.hint_status.configure(text="")
            self.solution_status.configure(text="")
            
            # Update history display
            self.update_history_display()
            
    def toggle_hint(self):
        """Toggle hint visibility."""
        if self.current_task:
            self.hint_visible = not self.hint_visible
            if self.hint_visible:
                self.hint_text.pack(fill="x", padx=10, pady=(0, 10))
                self.hint_status.configure(text="✓ Hint shown")
            else:
                self.hint_text.pack_forget()
                self.hint_status.configure(text="")
                
    def toggle_solution(self):
        """Toggle solution visibility."""
        if self.current_task:
            self.solution_visible = not self.solution_visible
            if self.solution_visible:
                self.solution_text.pack(fill="x", padx=10, pady=(0, 10))
                self.solution_status.configure(text="✓ Solution shown")
            else:
                self.solution_text.pack_forget()
                self.solution_status.configure(text="")
                
    def update_history_display(self):
        """Update the history display with recent questions."""
        history_text = self.history_manager.get_history_for_display()
        
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, "end")
        self.history_text.insert(1.0, history_text)
        self.history_text.config(state="disabled")
                
    def toggle_history(self):
        """Toggle history visibility."""
        self.history_visible = not self.history_visible
        if self.history_visible:
            self.history_text.pack(fill="x", padx=10, pady=(0, 10))
            self.history_button.configure(text="Hide History")
        else:
            self.history_text.pack_forget()
            self.history_button.configure(text="Show History")
                
    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()
