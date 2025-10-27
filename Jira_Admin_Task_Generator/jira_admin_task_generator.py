import json
from pydantic import BaseModel, Field
from typing import List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

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
llm = ChatOllama(model="llama3.2", temperature=0.5, format="json")

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

# --- 4. Run the chain and print the results ---
def generate_jira_task():
    """Executes the LangChain process to generate the structured Jira admin task."""
    print("--- Simulating Jira Admin Support Request ---")
    print("Generating task using Ollama (llama3)...")
    
    try:
        # Invoke the chain, which now returns the processed dictionary
        response_dict = jira_chain.invoke({})
        
        # Pretty print the final output
        print("\n" + "="*50)
        print("SIMULATED SUPPORT TICKET")
        print("="*50)
        
        # Use the dict keys, falling back to N/A if the custom parser returned an empty dict
        # due to an error.
        question = response_dict.get('question', 'N/A')
        hint = response_dict.get('hint', 'N/A')
        solution = response_dict.get('solution', [])
        
        print(f"End-User Question:\n{question}\n")
        print(f"Admin Hint:\n{hint}\n")
        print(f"Admin Solution:")
        if solution:
            for i, step in enumerate(solution):
                print(f"  {i+1}. {step}")
        else:
            print("  N/A")
            
        print("="*50)

    except Exception as e:
        print(f"\nAn UNHANDLED error occurred while running the chain: {e}")
        print("Please ensure Ollama is running and the 'llama3' model is available.")


if __name__ == "__main__":
    generate_jira_task()
