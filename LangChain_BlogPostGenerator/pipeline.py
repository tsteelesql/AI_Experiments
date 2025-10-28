"""
Main pipeline for blog post generation
"""

import logging
from pathlib import Path
from typing import Optional, Callable

from models import PythonFile, GenerationResult
from file_collector import PythonFileCollector
from rag_builder import RAGContextBuilder
from agents import BlogPostGenerator, GrammarEditorAgent, TechnicalEditorAgent, FinalPolishAgent
from config import config


logger = logging.getLogger(__name__)


class BlogPostPipeline:
    """Complete pipeline for generating blog posts from Python code"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.model.name
        self.collector = None
        self.rag_builder = RAGContextBuilder(model_name)
        self.generator = BlogPostGenerator(model_name)
        self.grammar_editor = GrammarEditorAgent(model_name)
        self.technical_editor = TechnicalEditorAgent(model_name)
        self.polisher = FinalPolishAgent(model_name)
        
    def generate(
        self, 
        directory: str, 
        output_file: str = None, 
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> GenerationResult:
        """
        Run the complete pipeline
        
        Args:
            directory: Path to Python project directory
            output_file: Output file path (optional)
            progress_callback: Function to call with progress updates
            
        Returns:
            GenerationResult with success status and content
        """
        output_file = output_file or config.default_output_file
        result = GenerationResult(success=False)
        
        def log(message: str):
            logger.info(message)
            if progress_callback:
                progress_callback(message)
        
        try:
            log("=" * 70)
            log("🚀 BLOG POST GENERATOR PIPELINE")
            log("=" * 70)
            
            # Step 1: Collect Python files
            log(f"\n📂 Step 1: Collecting Python files from {directory}")
            self.collector = PythonFileCollector(directory)
            files = self.collector.collect_files()
            
            if not files:
                error_msg = f"No Python files found in {directory}"
                log(f"❌ {error_msg}")
                result.error = error_msg
                return result
                
            stats = self.collector.get_file_stats(files)
            log(f"\n✓ Found {stats['total_files']} Python files ({stats['total_lines']} lines)")
            result.files_processed = stats['total_files']
            result.steps_completed.append("file_collection")
            
            # Step 2: Build RAG context
            log("\n🔧 Step 2: Building RAG context")
            vectorstore = self.rag_builder.build_vectorstore(files)
            result.steps_completed.append("rag_build")
            
            # Step 3: Generate initial post
            log("\n📖 Step 3: Generating blog post")
            initial_response = self.generator.generate_post(vectorstore, files)
            result.steps_completed.append("initial_generation")
            
            # Step 4: Grammar review
            log("\n📋 Step 4: Grammar and style editing")
            grammar_response = self.grammar_editor.edit(initial_response.content)
            result.steps_completed.append("grammar_review")
            
            # Step 5: Technical review
            log("\n🔬 Step 5: Technical review")
            tech_response = self.technical_editor.edit(grammar_response.content)
            result.steps_completed.append("technical_review")
            
            # Step 6: Final polish
            log("\n💎 Step 6: Final polish")
            final_response = self.polisher.polish(tech_response.content)
            result.steps_completed.append("final_polish")
            
            # Save output
            log(f"\n💾 Saving to {output_file}")
            self._save_output(final_response.content, output_file)
            
            log("\n" + "=" * 70)
            log("✅ BLOG POST GENERATION COMPLETE!")
            log("=" * 70)
            log(f"\n📄 Output saved to: {output_file}")
            
            result.success = True
            result.content = final_response.content
            
            return result
            
        except Exception as e:
            error_msg = f"Pipeline error: {str(e)}"
            logger.error(error_msg)
            log(f"\n❌ ERROR: {error_msg}")
            result.error = error_msg
            return result
    
    def _save_output(self, content: str, output_file: str) -> None:
        """Save content to output file"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Content saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving output: {e}")
            raise
