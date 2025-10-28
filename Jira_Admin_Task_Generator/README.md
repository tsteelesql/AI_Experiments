# Jira Admin Task Generator

A modular Python application that generates realistic Jira administrative tasks for practice, testing, and training purposes.

<img width="1978" height="1356" alt="image" src="https://github.com/user-attachments/assets/50bd5b53-dc80-424c-93b4-eaa797681f55" />

## Features

- **Varied Task Generation**: Creates different types of Jira tasks (bug creation, priority updates, workflow management, etc.)
- **History Tracking**: Prevents repetition by tracking previously generated questions
- **Smart Categorization**: Analyzes task types to ensure variety
- **Modern GUI**: Clean CustomTkinter interface with toggleable sections
- **Persistent Storage**: Saves question history across sessions

## Project Structure

```
Jira_Admin_Task_Generator/
├── main.py                 # Entry point
├── models.py              # Pydantic models and constants
├── history_manager.py     # Question history management
├── task_generator.py      # LLM chain and generation logic
├── gui.py                 # CustomTkinter GUI implementation
├── requirements.txt       # Python dependencies
├── question_history.json  # Persistent question history (auto-generated)
└── README.md             # This file
```

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure Ollama is running with the `llama3.2` model:
   ```bash
   ollama serve
   ollama pull llama3.2
   ```

## Usage

Run the application:
```bash
python main.py
```

### GUI Features

- **Generate New Task**: Creates a new, unique Jira administrative task
- **Show Hint**: Reveals a technical hint for the task
- **Show Solution**: Displays step-by-step solution instructions
- **Show History**: Views previously generated questions with timestamps

## Architecture

### Models (`models.py`)
- `JiraSupportTask`: Pydantic model for structured output
- `JIRA_ADMIN_CONTEXT`: Context and examples for task generation
- Configuration constants

### History Manager (`history_manager.py`)
- `QuestionHistory`: Manages persistent question storage
- Category analysis for variety
- History display formatting

### Task Generator (`task_generator.py`)
- `TaskGenerator`: Handles LLM chain creation and execution
- `robust_json_parser`: Parses LLM output with error handling
- Dynamic prompt creation with history context

### GUI (`gui.py`)
- `JiraTaskGeneratorGUI`: Main application interface
- Threaded task generation to prevent UI freezing
- Toggleable sections for hints, solutions, and history

## Dependencies

- `customtkinter>=5.2.0`: Modern GUI framework
- `langchain-ollama>=0.1.0`: Ollama integration
- `langchain-core>=0.1.0`: LangChain core functionality
- `pydantic>=2.0.0`: Data validation and settings

## Configuration

Key settings can be modified in `models.py`:
- `MODEL_NAME`: Ollama model to use
- `MODEL_TEMPERATURE`: Generation randomness
- `MAX_HISTORY_ENTRIES`: Maximum stored questions
- `HISTORY_FILE`: History storage location

## Benefits of Modular Structure

1. **Maintainability**: Each module has a single responsibility
2. **Testability**: Individual components can be tested in isolation
3. **Extensibility**: Easy to add new features or modify existing ones
4. **Readability**: Clear separation of concerns
5. **Reusability**: Components can be used independently
