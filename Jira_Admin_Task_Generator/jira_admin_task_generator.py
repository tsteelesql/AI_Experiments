import json
from pydantic import BaseModel, Field
from typing import List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import customtkinter as ctk
from tkinter import scrolledtext
import threading
import os
from datetime import datetime

# --- 1. Define the desired structured output using Pydantic ---
class JiraSupportTask(BaseModel):
    """Structured output for a simulated Jira Support Request."""
    question: str = Field(description="The support question written from the perspective of an end-user facing a configuration problem.")
    hint: str = Field(description="A concise technical hint for the Jira administrator to guide their investigation (e.g., 'Check the Screen Scheme').")
    solution: List[str] = Field(description="The step-by-step solution for a Jira Administrator, referencing the provided Jira documentation context.")

# --- 2. Define the context based on Jira documentation (Snippets focus on Custom Fields) ---
JIRA_ADMIN_CONTEXT = """
You are a language model assisting a Jira administrator by generating realistic sample tasks that mimic requests from end users. These tasks should reflect common Jira interactions across bug tracking, project management, and workflow maintenance.

Your goal is to produce actionable, varied, and natural-sounding Jira tickets that an admin could use for practice, automation testing, or training purposes. These tasks should simulate real-world scenarios without referencing actual users or projects.

Here are examples of the types of sample tasks you may generate:

    Create a new bug ticket for the checkout page error and assign it to the frontend team.

    Update the priority of all open issues in the Mobile App project to High.

    Add a comment to ticket JIRA-1023 asking for a status update from the assignee.

    Generate a list of all unresolved issues tagged with security created in the last 30 days.

    Move all tasks in the Sprint 12 board from To Do to In Progress.

    Link ticket JIRA-2045 to the epic User Authentication Revamp.

    Search for tickets assigned to me that are due this week and have no comments.

    Close all subtasks under JIRA-3001 and mark the parent task as Ready for QA.

    Create a recurring reminder to review tickets in the Blocked column every Monday morning.

    Export all completed issues from the Website Redesign project into a CSV file for reporting.

You should be able to:

    Generate tasks that reflect realistic Jira usage across different roles and teams.

    Vary the structure and phrasing to simulate natural user input.

    Include references to common Jira entities like boards, epics, priorities, statuses, and labels.

    Ensure tasks are clear, relevant, and executable by a Jira admin.

Your tone should be practical, efficient, and aligned with how users typically communicate in a work environment.
"""

# --- History Management ---
class QuestionHistory:
    def __init__(self, history_file="question_history.json"):
        self.history_file = history_file
        self.history = self.load_history()
    
    def load_history(self):
        """Load question history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_history(self):
        """Save question history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def add_question(self, question_data):
        """Add a new question to history."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question_data['question'],
            'hint': question_data['hint'],
            'solution': question_data['solution']
        }
        self.history.append(entry)
        # Keep only last 50 entries to prevent file from growing too large
        if len(self.history) > 50:
            self.history = self.history[-50:]
        self.save_history()
    
    def get_recent_questions(self, count=10):
        """Get recent questions to avoid repetition."""
        return [entry['question'] for entry in self.history[-count:]]
    
    def get_all_questions(self):
        """Get all questions from history."""
        return [entry['question'] for entry in self.history]
    
    def analyze_task_categories(self, count=5):
        """Analyze recent tasks to identify categories and patterns."""
        recent_entries = self.history[-count:] if len(self.history) >= count else self.history
        categories = []
        
        for entry in recent_entries:
            question = entry['question'].lower()
            if any(word in question for word in ['create', 'new', 'add']):
                categories.append('creation')
            elif any(word in question for word in ['update', 'change', 'modify']):
                categories.append('update')
            elif any(word in question for word in ['assign', 'move', 'transfer']):
                categories.append('assignment')
            elif any(word in question for word in ['search', 'find', 'list', 'generate']):
                categories.append('search')
            elif any(word in question for word in ['close', 'complete', 'finish']):
                categories.append('closure')
            elif any(word in question for word in ['link', 'connect', 'associate']):
                categories.append('linking')
            elif any(word in question for word in ['export', 'download', 'report']):
                categories.append('reporting')
            else:
                categories.append('other')
        
        return categories

# Initialize global history
question_history = QuestionHistory()

# --- Custom Parser for Robust JSON Handling ---

def robust_json_parser(raw_response_text: str) -> dict:
    """
    Attempts to parse the raw string response into a dictionary,
    handling common issues like markdown code fences (```json) used by Chat models.
    """
    print(f"\n--- DEBUG: RAW LLM OUTPUT ---\n{raw_response_text}\n---------------------------\n")

    cleaned_text = raw_response_text.strip()
    
    # Attempt to strip common markdown wrappers
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    elif cleaned_text.startswith("```"):
        # Handle generic markdown block
        cleaned_text = cleaned_text[3:]

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
        
    cleaned_text = cleaned_text.strip()
    
    try:
        # Use a standard JSON parser
        data = json.loads(cleaned_text)
        
        # Validate keys against the Pydantic model's fields
        #required_keys = ['question', 'hint', 'solution']
        required_keys = ['question', 'hint']
        if not all(key in data for key in required_keys):
             print("DEBUG: JSON parsed but missing required keys.")
             return {} # Return empty dict to trigger N/A fallback

        return data
        
    except json.JSONDecodeError as e:
        print(f"DEBUG: FINAL JSON DECODING ERROR: {e}")
        # Return an empty dict so the main function uses the 'N/A' fallback
        return {}

# --- 3. Set up the LangChain Components ---

# Initialize the Ollama model. We keep format="json" and temperature=0.0.
model = "llama3.2"
llm = ChatOllama(model=model, temperature=0.5, format="json")

# Create the prompt template. We manually specify the expected schema in the system prompt.
def create_prompt_with_history():
    """Create prompt template with history to avoid repetition."""
    recent_questions = question_history.get_recent_questions(5)
    recent_categories = question_history.analyze_task_categories(5)
    
    history_text = ""
    if recent_questions:
        history_text = "\n\nIMPORTANT: Avoid generating questions similar to these recent ones:\n"
        for i, q in enumerate(recent_questions, 1):
            history_text += f"{i}. {q}\n"
        
        # Add category analysis
        if recent_categories:
            unique_categories = list(set(recent_categories))
            history_text += f"\nRecent task categories: {', '.join(unique_categories)}\n"
            history_text += "Generate a completely different type of task and avoid repeating the same category or pattern.\n"
            history_text += "Focus on generating tasks from categories not recently used.\n"
    
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a specialized AI designed to simulate realistic Jira administrative tasks. "
                "Your task is to generate a practical request that a Jira administrator might receive from end users, "
                "and then provide a technical hint and a detailed step-by-step solution for completing the task. "
                "\n\n"
                "Context and Guidelines:\n"
                "{context}\n\n"
                "{history_context}\n\n"
                "Requirements:\n"
                "- Generate varied task types (bug creation, priority updates, workflow management, reporting, etc.)\n"
                "- Use realistic project names, ticket IDs, and team references\n"
                "- Make each request sound natural and practical\n"
                "- Vary the complexity and scope of tasks\n"
                "- Avoid repeating the same category of task consecutively\n"
                "- Include specific details like project names, ticket references, or team assignments\n"
                "\n"
                "The output MUST be a JSON object that strictly adheres to the following schema:\n"
                "{{'question': '...', 'hint': '...', 'solution': ['step 1', 'step 2']}}",
            ),
            (
                "human",
                "Generate a realistic Jira administrative task request that an end user might submit. "
                "Make it practical, varied, and different from recent tasks. Include specific details like project names, "
                "ticket references, or team assignments to make it sound authentic. Ensure it's a different category "
                "from recent tasks.",
            ),
        ]
    ).partial(
        # Insert context into the system prompt
        context=JIRA_ADMIN_CONTEXT,
        history_context=history_text,
    )


# Create the chain using LCEL: Prompt -> LLM (raw string) -> StrOutputParser -> Custom robust_json_parser
# Note: Chain will be created dynamically with history

# --- 4. Run the chain and return the results ---
def generate_jira_task():
    """Executes the LangChain process to generate the structured Jira admin task."""
    print("--- Simulating Jira Admin Support Request ---")
    print(f"Generating task using Ollama ({model})...")
    
    try:
        # Create chain with current history
        prompt = create_prompt_with_history()
        jira_chain = prompt | llm | StrOutputParser() | robust_json_parser
        
        # Invoke the chain, which now returns the processed dictionary
        response_dict = jira_chain.invoke({})
        
        # Use the dict keys, falling back to N/A if the custom parser returned an empty dict
        # due to an error.
        question = response_dict.get('question', 'N/A')
        hint = response_dict.get('hint', 'N/A')
        solution = response_dict.get('solution', [])
        
        # Format solution as a single string for display
        solution_text = ""
        if solution:
            solution_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(solution)])
        else:
            solution_text = "N/A"
            
        task_data = {
            'question': question,
            'hint': hint,
            'solution': solution_text
        }
        
        # Add to history
        question_history.add_question(task_data)
        
        return task_data

    except Exception as e:
        print(f"\nAn UNHANDLED error occurred while running the chain: {e}")
        print(f"Please ensure Ollama is running and the '{model}' model is available.")
        return {
            'question': f"Error: {str(e)}",
            'hint': "Please ensure Ollama is running and the model is available.",
            'solution': "Check your Ollama installation and model availability."
        }


# --- 5. CustomTkinter GUI Implementation ---
class JiraTaskGeneratorGUI:
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("light")  # "light" or "dark"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Jira Admin Task Generator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # State variables
        self.hint_visible = False
        self.solution_visible = False
        self.history_visible = False
        self.current_task = None
        
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
            self.current_task = generate_jira_task()
            
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
        history_entries = question_history.history[-10:]  # Show last 10 entries
        history_text = ""
        
        if history_entries:
            for i, entry in enumerate(reversed(history_entries), 1):
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%m/%d %H:%M")
                history_text += f"{i}. [{timestamp}] {entry['question'][:80]}...\n"
        else:
            history_text = "No questions generated yet."
            
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

def main_gui():
    """Main GUI function."""
    app = JiraTaskGeneratorGUI()
    app.run()

if __name__ == "__main__":
    main_gui()
