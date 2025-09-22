import os

def read_python_files(directory):
    code_blocks = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    code_blocks.append(f"# File: {path}\n{content}")
    return "\n\n".join(code_blocks)
