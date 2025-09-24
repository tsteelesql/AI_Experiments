# Ollama Code Generator Wrapper

## Project Description

The **Ollama Code Generator Wrapper** is a Python utility designed to interact with the Ollama API for generating code snippets. It allows users to provide natural language prompts and receive structured, executable Python scripts as output. The tool parses the response from Ollama, extracts code blocks written in Python, and saves them to a local directory for easy access and execution.

This wrapper is particularly useful for developers who want to quickly prototype or generate boilerplate code using AI models like `qwen3-coder` that are capable of understanding natural language instructions and producing syntactically correct Python scripts.

## Features

- **Natural Language Code Generation**: Prompt Ollama with human-readable descriptions to generate code.
- **Automatic Script Parsing**: Extracts multiple Python files from the Ollama response using markdown-style code blocks.
- **Structured Output**: Saves generated scripts into a dedicated `generated_scripts` folder for easy access.
- **User-Friendly CLI Interface**: Simple command-line interface to input prompts and view progress.

## Installation

1. Ensure you have [Ollama](https://ollama.com/) installed and running locally on port `11434`.
2. Pull a supported model (e.g., `qwen3-coder`) using the Ollama CLI:
   ```bash
   ollama pull qwen3-coder
   ```
3. Install required Python dependencies:
   ```bash
   pip install requests
   ```

> Note: This tool assumes that your local Ollama instance is accessible at `http://localhost:11434`.

## Usage Examples

### Basic Usage

Run the script and follow the prompt:

```bash
python ollama_code_generator_wrapper.py
```

You will be asked to enter a code generation prompt. For example:

```
Enter your code generation prompt: Create a Python function that calculates the factorial of a number using recursion.
```

The tool will generate one or more `.py` files and save them in the `generated_scripts` directory.

### Example Output

If you ask Ollama to create a factorial function, it might return something like:

```markdown
```python
# factorial.py
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
```
```

This will be parsed and saved as `factorial.py` in the output directory.

## Dependencies

- **Python 3.6+**
- **requests** (`pip install requests`)

No other external libraries or packages are required beyond standard Python modules and the `requests` library.

--- 

> ⚠️ Make sure Ollama is running locally before executing this script, otherwise it will fail with a connection error.