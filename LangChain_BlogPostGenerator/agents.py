"""
AI agents for blog post generation and editing
"""

import logging
from typing import Optional, List

from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma

from models import PythonFile, AgentResponse
from config import config


logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for AI agents"""
    
    def __init__(self, model_name: str = None, temperature: float = 0.7):
        self.model_name = model_name or config.model.name
        self.temperature = temperature
        self.llm = ChatOllama(model=self.model_name, temperature=temperature)
    
    def _extract_content(self, response) -> str:
        """Extract content from Ollama response"""
        if isinstance(response, dict):
            return response.get('content', str(response))
        return str(response)


class BlogPostGenerator(BaseAgent):
    """Generates blog posts using Ollama and RAG context"""
    
    def __init__(self, model_name: str = None, temperature: float = 0.7):
        super().__init__(model_name, temperature)
        
    def generate_post(self, vectorstore: Chroma, files: List[PythonFile]) -> AgentResponse:
        """Generate initial blog post from Python files context"""
        
        try:
            # Create retrieval chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": config.rag.retrieval_k})
            )
            
            # Build context summary
            file_list = "\n".join([f"- {f.relative_path}" for f in files])
            
            prompt = f"""You are a technical blog writer. Analyze the following Python codebase and create an engaging blog post.

Files in the codebase:
{file_list}

Your task:
1. Identify the main purpose and functionality of the code
2. Highlight interesting Python use cases, patterns, and techniques used
3. Extract key learning opportunities for readers
4. Include relevant code snippets with explanations
5. Write in an engaging, educational tone

Create a comprehensive blog post (800-1200 words) that would help developers learn from this code.

Focus on:
- What problems does this code solve?
- What Python features/libraries are used effectively?
- What can developers learn from this implementation?
- Include 2-3 code examples with explanations

Generate the blog post:"""

            logger.info("✍️  Generating initial blog post...")
            response = qa_chain.invoke(prompt)
            content = self._extract_content(response)
            
            return AgentResponse(
                content=content,
                metadata={"step": "initial_generation", "files_analyzed": len(files)}
            )
            
        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            raise


class GrammarEditorAgent(BaseAgent):
    """AI agent that reviews and corrects grammar"""
    
    def __init__(self, model_name: str = None):
        super().__init__(model_name, temperature=0.3)
        
    def edit(self, content: str) -> AgentResponse:
        """Review and fix grammatical errors"""
        
        prompt = f"""You are a professional editor specializing in technical writing. 
Review the following blog post for grammatical errors, clarity, and readability.

Instructions:
- Fix any grammatical errors
- Improve sentence structure where needed
- Ensure consistent tone and style
- Keep all technical content and code examples intact
- Maintain the original meaning and structure
- Do not add or remove sections

Blog post to edit:

{content}

Provide the edited version:"""

        logger.info("📝 Running grammar and style review...")
        response = self.llm.invoke(prompt)
        content = self._extract_content(response)
        
        return AgentResponse(
            content=content,
            metadata={"step": "grammar_review"}
        )


class TechnicalEditorAgent(BaseAgent):
    """AI agent that reviews technical accuracy and code examples"""
    
    def __init__(self, model_name: str = None):
        super().__init__(model_name, temperature=0.2)
        
    def edit(self, content: str) -> AgentResponse:
        """Review technical accuracy and validate code examples"""
        
        prompt = f"""You are a senior Python developer and technical editor.
Review this blog post for technical accuracy and code correctness.

Instructions:
- Verify all code examples are syntactically correct
- Check that technical explanations are accurate
- Ensure code examples follow Python best practices
- Validate that imports and usage are correct
- Flag any potential bugs or issues in code snippets
- Fix any technical inaccuracies
- Keep the writing style and structure intact

Blog post to review:

{content}

Provide the technically reviewed version:"""

        logger.info("🔍 Running technical review...")
        response = self.llm.invoke(prompt)
        content = self._extract_content(response)
        
        return AgentResponse(
            content=content,
            metadata={"step": "technical_review"}
        )


class FinalPolishAgent(BaseAgent):
    """AI agent that creates the final concise version"""
    
    def __init__(self, model_name: str = None):
        super().__init__(model_name, temperature=0.4)
        
    def polish(self, content: str) -> AgentResponse:
        """Create final polished and concise version"""
        
        prompt = f"""You are a content strategist finalizing a technical blog post.
Create the final, polished version that is concise yet comprehensive.

Instructions:
- Remove any redundancy or repetition
- Ensure the post flows logically
- Keep it engaging and readable
- Maintain all key technical insights
- Preserve all code examples
- Aim for clarity and impact
- Add a compelling title and brief introduction if missing

Blog post to polish:

{content}

Provide the final polished version:"""

        logger.info("✨ Creating final polished version...")
        response = self.llm.invoke(prompt)
        content = self._extract_content(response)
        
        return AgentResponse(
            content=content,
            metadata={"step": "final_polish"}
        )
