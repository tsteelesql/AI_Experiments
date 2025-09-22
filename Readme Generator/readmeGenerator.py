import os
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from directory_selector_class import DirectorySelectorApp

ollama_model = "qwen3-coder"

def read_python_files(directory):
    code_blocks = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    code_blocks.append(f"# File: {file_path}\n{content}")
    return "\n\n".join(code_blocks)

def generate_readme(code_context, model_name=ollama_model):
    prompt = PromptTemplate(
        input_variables=["code"],
        template="""
You are an expert software documenter. Based on the following Python codebase, generate a professional README.md file that includes:
- Project description
- Features
- Installation instructions
- Usage examples
- Any dependencies or requirements

This README should be written for GitHub, so that formatting appears correctly.
Do not include a License section.

Codebase:
{code}
"""
    )

    llm = ChatOllama(model=model_name,temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(code=code_context)


if __name__ == "__main__":

    LocalFileSelector = DirectorySelectorApp()
    LocalFileSelector.run()

    # After the window closes, you can access the saved path
    selected_path = LocalFileSelector.get_saved_path()
    if selected_path:
        print(f"Main script received path: {selected_path}")

    code_context = read_python_files(selected_path)
    readme_content = generate_readme(code_context)

    with open(f"{selected_path}/README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("README.md generated successfully.")
