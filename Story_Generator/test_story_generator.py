"""
Unit tests for the story generator
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the script directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from story_generator import (
    StoryGenerationConfig,
    WordVectorizer,
    WriterAgent,
    EditorAgent,
    StoryGenerator
)

class TestStoryGenerator(unittest.TestCase):
    """Test cases for story generator components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = StoryGenerationConfig()
        self.test_words = ["dragon", "castle", "knight"]
    
    def test_config_initialization(self):
        """Test configuration initialization"""
        config = StoryGenerationConfig()
        self.assertEqual(config.ollama_model, "llama3.2")
        self.assertEqual(config.chroma_collection_name, "story_words")
        self.assertEqual(config.chroma_persist_directory, "./chroma_db")
    
    @patch('chromadb.PersistentClient')
    def test_word_vectorizer_initialization(self, mock_client):
        """Test word vectorizer initialization"""
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vectorizer = WordVectorizer(self.config)
        
        self.assertIsNotNone(vectorizer.client)
        self.assertIsNotNone(vectorizer.collection)
    
    @patch('chromadb.PersistentClient')
    def test_add_words(self, mock_client):
        """Test adding words to vector store"""
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vectorizer = WordVectorizer(self.config)
        vectorizer.add_words(self.test_words)
        
        mock_collection.add.assert_called_once()
    
    @patch('chromadb.PersistentClient')
    def test_search_words(self, mock_client):
        """Test searching words in vector store"""
        mock_collection = MagicMock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        vectorizer = WordVectorizer(self.config)
        result = vectorizer.search_words("dragon")
        
        mock_collection.query.assert_called_once()
        self.assertIsInstance(result, list)
    
    @patch('langchain_ollama.ChatOllama')
    def test_writer_agent_initialization(self, mock_llm):
        """Test writer agent initialization"""
        mock_llm.return_value = MagicMock()
        
        writer = WriterAgent(self.config)
        self.assertIsNotNone(writer.llm)
        self.assertIsNotNone(writer.chain)
    
    @patch('langchain_ollama.ChatOllama')
    def test_editor_agent_initialization(self, mock_llm):
        """Test editor agent initialization"""
        mock_llm.return_value = MagicMock()
        
        editor = EditorAgent(self.config)
        self.assertIsNotNone(editor.llm)
        self.assertIsNotNone(editor.chain)
    
    @patch('langchain_ollama.ChatOllama')
    def test_story_generation(self, mock_llm):
        """Test full story generation workflow"""
        # Mock the LLM response
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value = "Once upon a time, a brave knight saved a princess."
        mock_llm.return_value = mock_llm_instance
        
        # Initialize components
        generator = StoryGenerator(self.config)
        
        # Add words
        generator.process_words(self.test_words)
        
        # Generate story
        story = generator.generate_story(self.test_words, "Create a short story")
        
        self.assertIsInstance(story, str)
        self.assertTrue(len(story) > 0)

if __name__ == '__main__':
    unittest.main()
