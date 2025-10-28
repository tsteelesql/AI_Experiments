import json
from pydantic import BaseModel, Field
from typing import List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import customtkinter as ctk
from tkinter import scrolledtext
import threading

# --- 1. Define the desired structured output using Pydantic ---
class JiraSupportTask(BaseModel):
    """Structured output for a simulated Jira Support Request."""
    question: str = Field(description="The support question written from the perspective of an end-user facing a configuration problem.")
    hint: str = Field(description="A concise technical hint for the Jira administrator to guide their investigation (e.g., 'Check the Screen Scheme').")
    solution: List[str] = Field(description="The step-by-step solution for a Jira Administrator, referencing the provided Jira documentation context.")

# --- 2. Define the context based on Jira documentation (Snippets focus on Custom Fields) ---
JIRA_ADMIN_CONTEXT = """
The core daily admin task involves configuring custom fields.
1. Custom fields must be associated with a Screen to be visible when creating, editing, or viewing an issue. If no screen is associated, the field is created but is not used.
2. To add a field to a screen: Navigate to Fields > Field configurations, select the field configuration, find the custom field, and select 'Screens' to change the associations.
3. Field configurations group fields together and are assigned to issue types using Field configuration schemes.
4. A common end-user issue is: 'I created a new custom field, but I cannot see it when I create an issue in Project X.'
5. The solution involves ensuring the custom field is added to the Screen that is currently being used by the relevant Issue Type and Project.

Sample other user requests to use as inspiration:
1. Create a new bug ticket for the checkout page error and assign it to the frontend team.  
2. Update the priority of all open issues in the Mobile App project to High.  
3. Add a comment to ticket JIRA-1023 asking for a status update from the assignee.  
4. Generate a list of all unresolved issues tagged with security created in the last 30 days.  
5. Move all tasks in the Sprint 12 board from To Do to In Progress.  
6. Link ticket JIRA-2045 to the epic User Authentication Revamp.  
7. Search for tickets assigned to me that are due this week and have no comments.  
8. Close all subtasks under JIRA-3001 and mark the parent task as Ready for QA.  
9. Create a recurring reminder to review tickets in the Blocked column every Monday morning.  
10. Export all completed issues from the Website Redesign project into a CSV file for reporting.  
"""

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
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a specialized AI designed to simulate Jira support requests. "
            "Your task is to generate a support question from an end-user, "
            "and then provide a technical hint and a detailed solution for a Jira Admin. "
            "Base the scenario on the following Jira administration context about custom fields: \n\n"
            "{context}\n\n"
            "The output MUST be a JSON object that strictly adheres to the following schema:\n"
            "{{'question': '...', 'hint': '...', 'solution': ['step 1', 'step 2']}}",
        ),
        (
            "human",
            "Generate a support request simulating a daily admin task related to Jira custom fields, "
            "as requested by an frustrated end-user.",
        ),
    ]
).partial(
    # Insert context into the system prompt
    context=JIRA_ADMIN_CONTEXT,
)


# Create the chain using LCEL: Prompt -> LLM (raw string) -> StrOutputParser -> Custom robust_json_parser
jira_chain = prompt | llm | StrOutputParser() | robust_json_parser

# --- 4. Run the chain and return the results ---
def generate_jira_task():
    """Executes the LangChain process to generate the structured Jira admin task."""
    print("--- Simulating Jira Admin Support Request ---")
    print(f"Generating task using Ollama ({model})...")
    
    try:
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
            
        return {
            'question': question,
            'hint': hint,
            'solution': solution_text
        }

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
                
    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()

def main_gui():
    """Main GUI function."""
    app = JiraTaskGeneratorGUI()
    app.run()

if __name__ == "__main__":
    main_gui()
