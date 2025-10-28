"""
History management for the Jira Admin Task Generator.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from models import HISTORY_FILE, MAX_HISTORY_ENTRIES


class QuestionHistory:
    """Manages the history of generated questions to avoid repetition."""
    
    def __init__(self, history_file: str = HISTORY_FILE):
        self.history_file = history_file
        self.history = self.load_history()
    
    def load_history(self) -> List[Dict[str, Any]]:
        """Load question history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_history(self) -> None:
        """Save question history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def add_question(self, question_data: Dict[str, Any]) -> None:
        """Add a new question to history."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question_data['question'],
            'hint': question_data['hint'],
            'solution': question_data['solution']
        }
        self.history.append(entry)
        # Keep only last N entries to prevent file from growing too large
        if len(self.history) > MAX_HISTORY_ENTRIES:
            self.history = self.history[-MAX_HISTORY_ENTRIES:]
        self.save_history()
    
    def get_recent_questions(self, count: int = 5) -> List[str]:
        """Get recent questions to avoid repetition."""
        return [entry['question'] for entry in self.history[-count:]]
    
    def get_all_questions(self) -> List[str]:
        """Get all questions from history."""
        return [entry['question'] for entry in self.history]
    
    def analyze_task_categories(self, count: int = 5) -> List[str]:
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
    
    def get_history_for_display(self, count: int = 10) -> str:
        """Get formatted history for GUI display."""
        history_entries = self.history[-count:] if len(self.history) >= count else self.history
        history_text = ""
        
        if history_entries:
            for i, entry in enumerate(reversed(history_entries), 1):
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%m/%d %H:%M")
                history_text += f"{i}. [{timestamp}] {entry['question'][:80]}...\n"
        else:
            history_text = "No questions generated yet."
            
        return history_text
