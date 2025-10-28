"""
Blog Post Generator with Multi-Agent Review System
Analyzes Python files and generates technical blog posts using Ollama and LangChain

This is the main entry point for the application.
"""

import logging
import sys
from pathlib import Path

from gui import BlogGeneratorGUI
from config import config


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('blog_generator.log')
        ]
    )


def main():
    """Main entry point with GUI"""
    try:
        # Setup logging
        setup_logging()
        
        # Create and run the GUI application
        app = BlogGeneratorGUI()
        app.run()
        
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
