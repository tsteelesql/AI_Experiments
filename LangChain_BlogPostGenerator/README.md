# Blog Post Generator - Refactored

A multi-agent system that analyzes Python codebases and generates technical blog posts using Ollama and LangChain.

## Features

- **Multi-Agent Pipeline**: Uses specialized AI agents for different aspects of blog post creation
- **RAG Integration**: Retrieval Augmented Generation for context-aware content creation
- **Modern GUI**: Clean, intuitive interface built with CustomTkinter
- **Configurable**: Easy to modify models, parameters, and settings
- **Error Handling**: Robust error handling and logging throughout

## Architecture

The application is organized into modular components:

### Core Modules

- **`config.py`**: Configuration management with dataclasses
- **`models.py`**: Data models and structures
- **`file_collector.py`**: Python file collection and processing
- **`rag_builder.py`**: RAG context building with Chroma vector store
- **`agents.py`**: AI agents for different editing tasks
- **`pipeline.py`**: Main orchestration pipeline
- **`gui.py`**: User interface components

### AI Agents

1. **BlogPostGenerator**: Creates initial blog post from codebase analysis
2. **GrammarEditorAgent**: Reviews and corrects grammar and style
3. **TechnicalEditorAgent**: Validates technical accuracy and code examples
4. **FinalPolishAgent**: Creates final polished version

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Ollama is running with your preferred model (e.g., llama3.2)

## Usage

### GUI Mode
```bash
python main_refactored.py
```

### Programmatic Usage
```python
from pipeline import BlogPostPipeline

pipeline = BlogPostPipeline(model_name="llama3.2")
result = pipeline.generate(
    directory="/path/to/python/project",
    output_file="blog_post.md"
)

if result.success:
    print("Blog post generated successfully!")
    print(result.content)
else:
    print(f"Error: {result.error}")
```

## Configuration

Modify `config.py` to adjust:
- Model settings (name, temperature)
- RAG parameters (chunk size, overlap)
- UI settings (window sizes, colors)
- Default output file

## Requirements

- Python 3.8+
- Ollama with compatible model
- Sufficient RAM for model inference
- Internet connection for model downloads

## Error Handling

The application includes comprehensive error handling:
- File system errors during collection
- Model inference errors
- RAG context building errors
- GUI interaction errors

All errors are logged to both console and `blog_generator.log`.

## Contributing

The modular architecture makes it easy to:
- Add new AI agents
- Modify existing agents
- Change RAG parameters
- Customize the GUI
- Add new file processing capabilities
