"""
Task generation logic for the Jira Admin Task Generator.
"""

import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any

from models import JIRA_ADMIN_CONTEXT, MODEL_NAME, MODEL_TEMPERATURE
from history_manager import QuestionHistory


def robust_json_parser(raw_response_text: str) -> Dict[str, Any]:
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
        required_keys = ['question', 'hint']
        if not all(key in data for key in required_keys):
             print("DEBUG: JSON parsed but missing required keys.")
             return {} # Return empty dict to trigger N/A fallback

        return data
        
    except json.JSONDecodeError as e:
        print(f"DEBUG: FINAL JSON DECODING ERROR: {e}")
        # Return an empty dict so the main function uses the 'N/A' fallback
        return {}


class TaskGenerator:
    """Handles the generation of Jira admin tasks using LangChain and Ollama."""
    
    def __init__(self, history_manager: QuestionHistory):
        self.history_manager = history_manager
        self.llm = ChatOllama(model=MODEL_NAME, temperature=MODEL_TEMPERATURE, format="json")
    
    def create_prompt_with_history(self) -> ChatPromptTemplate:
        """Create prompt template with history to avoid repetition."""
        recent_questions = self.history_manager.get_recent_questions(5)
        recent_categories = self.history_manager.analyze_task_categories(5)
        
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
    
    def generate_task(self) -> Dict[str, Any]:
        """Executes the LangChain process to generate the structured Jira admin task."""
        print("--- Simulating Jira Admin Support Request ---")
        print(f"Generating task using Ollama ({MODEL_NAME})...")
        
        try:
            # Create chain with current history
            prompt = self.create_prompt_with_history()
            jira_chain = prompt | self.llm | StrOutputParser() | robust_json_parser
            
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
            self.history_manager.add_question(task_data)
            
            return task_data

        except Exception as e:
            print(f"\nAn UNHANDLED error occurred while running the chain: {e}")
            print(f"Please ensure Ollama is running and the '{MODEL_NAME}' model is available.")
            return {
                'question': f"Error: {str(e)}",
                'hint': "Please ensure Ollama is running and the model is available.",
                'solution': "Check your Ollama installation and model availability."
            }
