"""
Data models for the Blog Post Generator
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class PythonFile:
    """Represents a Python file with its metadata"""
    path: str
    content: str
    relative_path: str
    size: int = 0
    lines: int = 0
    
    def __post_init__(self):
        self.size = len(self.content)
        self.lines = len(self.content.splitlines())


@dataclass
class GenerationResult:
    """Result of blog post generation"""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    steps_completed: List[str] = None
    files_processed: int = 0
    
    def __post_init__(self):
        if self.steps_completed is None:
            self.steps_completed = []


@dataclass
class AgentResponse:
    """Response from an AI agent"""
    content: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
