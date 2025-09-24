import requests
import re
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3-coder"  # or any model you've pulled that supports code generation
OUTPUT_DIR = OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_scripts")

def call_ollama(prompt: str) -> str:
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["response"]

def parse_scripts(text: str) -> dict:
    # Match headers like ```python filename.py\n<code>\n```
    pattern = r"```python\s*#\s*(\S+\.py)\s*\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return {filename: code.strip() for filename, code in matches}

def save_scripts(scripts: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename, code in scripts.items():
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"✅ Saved: {path}")

def main():
    user_prompt = input("Enter your code generation prompt: ")
    print("🧠 Generating code from Ollama...")
    response = call_ollama(user_prompt)
    scripts = parse_scripts(response)
    if scripts:
        save_scripts(scripts)
    else:
        print("⚠️ No scripts found in the response.")
        print(response)

if __name__ == "__main__":
    main()
