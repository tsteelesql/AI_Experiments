"""
Models and constants for the Jira Admin Task Generator.
"""

from pydantic import BaseModel, Field
from typing import List

# --- Pydantic Models ---
class JiraSupportTask(BaseModel):
    """Structured output for a simulated Jira Support Request."""
    question: str = Field(description="The support question written from the perspective of an end-user facing a configuration problem.")
    hint: str = Field(description="A concise technical hint for the Jira administrator to guide their investigation (e.g., 'Check the Screen Scheme').")
    solution: List[str] = Field(description="The step-by-step solution for a Jira Administrator, referencing the provided Jira documentation context.")

# --- Constants ---
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

# Model configuration
MODEL_NAME = "llama3.2"
MODEL_TEMPERATURE = 0.5
HISTORY_FILE = "question_history.json"
MAX_HISTORY_ENTRIES = 50
HISTORY_DISPLAY_COUNT = 10
