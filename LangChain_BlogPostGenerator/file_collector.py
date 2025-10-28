"""
File collection and processing utilities
"""

import os
from pathlib import Path
from typing import List, Optional
import logging

from models import PythonFile


logger = logging.getLogger(__name__)


class PythonFileCollector:
    """Collects and processes Python files from a directory"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        
    def collect_files(self, exclude_patterns: Optional[List[str]] = None) -> List[PythonFile]:
        """
        Recursively collect all Python files from the directory
        
        Args:
            exclude_patterns: List of patterns to exclude (e.g., ['test_*', '__pycache__'])
            
        Returns:
            List of PythonFile objects
        """
        if exclude_patterns is None:
            exclude_patterns = ['__pycache__', 'test_*', '*_test.py']
            
        python_files = []
        
        try:
            for py_file in self.root_dir.rglob("*.py"):
                # Skip excluded patterns
                if self._should_exclude(py_file, exclude_patterns):
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    relative_path = py_file.relative_to(self.root_dir)
                    python_file = PythonFile(
                        path=str(py_file),
                        content=content,
                        relative_path=str(relative_path)
                    )
                    python_files.append(python_file)
                    logger.info(f"✓ Collected: {relative_path}")
                    
                except Exception as e:
                    logger.error(f"✗ Error reading {py_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error scanning directory {self.root_dir}: {e}")
            raise
            
        return python_files
    
    def _should_exclude(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded based on patterns"""
        file_str = str(file_path)
        for pattern in exclude_patterns:
            if pattern in file_str:
                return True
        return False
    
    def get_file_stats(self, files: List[PythonFile]) -> dict:
        """Get statistics about collected files"""
        if not files:
            return {"total_files": 0, "total_lines": 0, "total_size": 0}
            
        total_lines = sum(f.lines for f in files)
        total_size = sum(f.size for f in files)
        
        return {
            "total_files": len(files),
            "total_lines": total_lines,
            "total_size": total_size,
            "avg_lines_per_file": total_lines / len(files) if files else 0
        }
