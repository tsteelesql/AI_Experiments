# Blog Post Generator

## 📝 Project Description

The **Blog Post Generator** is an AI-powered tool designed to automate the creation of educational blog posts from Python codebases. It leverages a multi-agent system to analyze code, generate content, and polish it for clarity and technical accuracy — all in a structured, sequential workflow.

This project is ideal for developers who want to quickly turn their Python scripts into engaging, well-written articles suitable for audiences with a low-to-medium level of technical knowledge.

---

## ✨ Features

- **Multi-Agent Workflow**: Uses specialized agents for writing, technical editing, and grammar polishing.
- **Code Analysis**: Reads and parses Python files from a specified directory to extract code snippets and context.
- **Educational Tone**: Designed to explain code use cases like a teacher, making content accessible to beginners and intermediate developers.
- **Seamless Integration**: Built using CrewAI and LangChain for efficient task execution and LLM integration.

---

## 🛠️ Installation

To get started with the Blog Post Generator:

1. Clone or download this repository.
2. Install the required dependencies using pip:

```bash
pip install crewai langchain-ollama
```

> Note: This project uses `ChatOllama` to connect to local LLMs (e.g., Llama3.2). Ensure you have Ollama installed and running locally.

---

## 🚀 Usage

1. **Prepare Your Python Scripts**:
   Place your `.py` files in a folder (e.g., `./your_python_scripts`).

2. **Run the Generator**:

```bash
python blog_post_crew_runner.py
```

3. **View the Output**:
   The final blog post will be printed to the console after all agents have processed the input.

---

## 🧠 Example Workflow

1. **Initial Writer Agent** reads your Python scripts and writes a rough draft of the blog post.
2. **Technical Editor Agent** reviews the content for accuracy, pointing out any errors or unclear explanations.
3. **Writing Editor Agent** polishes the text for grammar, flow, and readability.

Each agent contributes to producing a high-quality, publish-ready article based on your codebase.

---

## 📦 Dependencies

- `crewai`: For managing multi-agent workflows.
- `langchain_ollama`: For connecting to local LLMs via Ollama.
- Python 3.8+

> Ensure that you are running a compatible version of Ollama with the `llama3.2` model or update the `model` parameter in `agents.py` accordingly.

--- 

> 💡 Tip: You can customize prompts, agents, and tasks by modifying the files under `agents.py`, `tasks.py`, and `utils.py`.

--- 

Happy coding and blogging! 🐍✍️