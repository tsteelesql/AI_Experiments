"""
Configuration settings for the Blog Post Generator
"""

from dataclasses import dataclass
from typing import List


@dataclass
class ModelConfig:
    """Configuration for AI models"""
    name: str = "llama3.2"
    temperature: float = 0.7
    available_models: List[str] = None
    
    def __post_init__(self):
        if self.available_models is None:
            self.available_models = [
                "llama3.2", "llama3.1", "llama3", 
                "mistral", "codellama", "qwen2.5"
            ]


@dataclass
class RAGConfig:
    """Configuration for RAG (Retrieval Augmented Generation)"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_k: int = 5
    separators: List[str] = None
    
    def __post_init__(self):
        if self.separators is None:
            self.separators = ["\n\n", "\nclass ", "\ndef ", "\n", " ", ""]


@dataclass
class AppConfig:
    """Main application configuration"""
    model: ModelConfig = None
    rag: RAGConfig = None
    default_output_file: str = "generated_blog_post.md"
    window_title: str = "Blog Post Generator"
    window_size: str = "800x700"
    viewer_size: str = "1000x800"
    
    def __post_init__(self):
        if self.model is None:
            self.model = ModelConfig()
        if self.rag is None:
            self.rag = RAGConfig()


# Global configuration instance
config = AppConfig()
