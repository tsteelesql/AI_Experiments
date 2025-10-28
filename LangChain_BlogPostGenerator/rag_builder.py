"""
RAG (Retrieval Augmented Generation) context builder
"""

from typing import List
import logging

from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from models import PythonFile
from config import config


logger = logging.getLogger(__name__)


class RAGContextBuilder:
    """Builds RAG context from Python files using LangChain and Chroma"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.model.name
        self.embeddings = OllamaEmbeddings(model=self.model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.chunk_overlap,
            separators=config.rag.separators
        )
        
    def build_vectorstore(self, files: List[PythonFile]) -> Chroma:
        """
        Create a vector store from Python files
        
        Args:
            files: List of PythonFile objects
            
        Returns:
            Chroma vector store
        """
        if not files:
            raise ValueError("No files provided for vector store creation")
            
        documents = []
        metadatas = []
        
        try:
            for file in files:
                chunks = self.text_splitter.split_text(file.content)
                for chunk in chunks:
                    documents.append(chunk)
                    metadatas.append({
                        "source": file.relative_path,
                        "full_path": file.path,
                        "file_size": file.size,
                        "file_lines": file.lines
                    })
            
            logger.info(f"📚 Creating vector store with {len(documents)} chunks...")
            
            vectorstore = Chroma.from_texts(
                texts=documents,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"✅ Vector store created successfully")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise
    
    def get_context_summary(self, files: List[PythonFile]) -> str:
        """Generate a summary of the codebase context"""
        file_list = "\n".join([f"- {f.relative_path} ({f.lines} lines)" for f in files])
        
        return f"""Files in the codebase:
{file_list}

Total files: {len(files)}
Total lines: {sum(f.lines for f in files)}
Average lines per file: {sum(f.lines for f in files) / len(files):.1f}"""
