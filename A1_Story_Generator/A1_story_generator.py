#!/usr/bin/env python3
"""
run_ollama_http_gui.py

Usage:
    python run_ollama_http_gui.py "Write a haiku about autumn"
    python run_ollama_http_gui.py

Requirements:
    pip install requests

Notes:
    - This script assumes a local Ollama HTTP endpoint accepting JSON POSTs.
    - If your Ollama endpoint differs, change API_ENDPOINT accordingly.
"""


import json
import requests
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Adjust these to match your local Ollama HTTP server and model
API_ENDPOINT = "http://localhost:11434/api/generate"  # change if needed
MODEL_NAME = "llama3.2"  # change to the model you want to use
REQUEST_TIMEOUT = 120  # seconds



def call_ollama(prompt: str) -> str:
    """
    Call the Ollama HTTP API and return the model output as text.
    Attempts to parse common JSON response shapes and falls back to raw text.
    Raises RuntimeError on network or API errors.
    """
    try:
        response = requests.post(API_ENDPOINT, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        })
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request failed: {e}") from e
    
    if not response.ok:
        # Try to present a helpful error body if available
        body = response.text.strip()
        msg = f"HTTP {response.status_code}: {body or 'No response body'}"
        raise RuntimeError(msg)
    return response.json()["response"]




def call_ollama_http(prompt: str, model: str = MODEL_NAME, timeout: int = REQUEST_TIMEOUT) -> str:
    """
    Call the Ollama HTTP API and return the model output as text.
    Attempts to parse common JSON response shapes and falls back to raw text.
    Raises RuntimeError on network or API errors.
    """
    payload = {"model": model, "prompt": prompt}
    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=timeout)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request failed: {e}") from e

    if not resp.ok:
        # Try to present a helpful error body if available
        body = resp.text.strip()
        msg = f"HTTP {resp.status_code}: {body or 'No response body'}"
        raise RuntimeError(msg)

    # Try to parse JSON responses
    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type:
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return resp.text

        # Common response keys that may contain generated text
        for key in ("text", "output", "result", "generation", "content"):
            if isinstance(data, dict) and key in data:
                val = data[key]
                if isinstance(val, str):
                    return val
                if isinstance(val, list):
                    return "\n".join(map(str, val))
                return str(val)

        # If API returns a list of tokens/chunks
        if isinstance(data, list):
            try:
                return "\n".join(item.get("text", str(item)) if isinstance(item, dict) else str(item) for item in data)
            except Exception:
                return json.dumps(data, ensure_ascii=False, indent=2)

        # Fallback: pretty-print JSON
        return json.dumps(data, ensure_ascii=False, indent=2)

    # Non-JSON response: return raw text
    return resp.text

def show_text_window(title: str, content: str, width: int = 800, height: int = 600):
    root = tk.Tk()
    root.title(title)

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = max((screen_w - width) // 2, 0)
    y = max((screen_h - height) // 2, 0)
    root.geometry(f"{width}x{height}+{x}+{y}")

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 11))
    text_area.pack(fill=tk.BOTH, expand=True)
    text_area.insert(tk.END, content)
    text_area.configure(state=tk.NORMAL)
    text_area.bind("<Key>", lambda e: "break")

    def copy_all():
        root.clipboard_clear()
        root.clipboard_append(text_area.get("1.0", tk.END).rstrip("\n"))
        messagebox.showinfo("Copied", "All text copied to clipboard.")

    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Copy All", command=copy_all)
    filemenu.add_separator()
    filemenu.add_command(label="Close", command=root.destroy)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)

    root.mainloop()

def main():
    # Determine prompt: CLI arg or interactive input
    # if len(sys.argv) >= 2:
    #     prompt = " ".join(sys.argv[1:])
    # else:
    #     try:
    #         prompt = input("Enter prompt for Ollama: ").strip()
        # except EOFError:
    prompt = "Act as a seasoned **Linguistics Expert, Professional Writer, and Graded Reader Author/Translator**. Your task is to generate and translate a short story based on the user's request.\
    **Part 1: Story Generation (Source Language)**"\
    \
    "1.  **Goal:** Write a cohesive narrative short story."\
    "2.  **Length Constraint:** Must be between 100 and 120 words."\
    "3.  **Linguistic Constraint:** The story must strictly adhere to the **CEFR A1 level** for language learners. This means:\
        * Use only the simple present tense.\
        * Use highly common, core vocabulary (e.g., *dog, ball, run, is, happy, go*).\
        * Employ simple, declarative, non-complex sentences (e.g., ""Tom is a boy."" not ""Tom, who is five years old, is a boy."").\
    4.  **Format:** Provide a clear **Title** and the story text.\
    \
    **Part 2: Translation (Target Language)**\
    \
    1.  **Goal:** Translate the **entire original story** into the user-specified target language (e.g., German, Spanish).\
    2.  **Linguistic Constraint:** The translation must be an **A1-level equivalent** translation. Use the most direct, common, and beginner-friendly equivalent words and sentence structures. Avoid idiomatic expressions or complex verb tenses in the target language.\
    3.  **Format:** Provide the translation with the translated **Title** and story text.\
    4.  **Value-Add:** Include a short ""**Vocabulary Note**"" section listing at least five of the most important nouns/adjectives from the story along with their respective articles (e.g., *der Hund*, *la pelota*).\
    **Instructions:** Create a comtemporary mystery story using a light tone that remains friendly for all ages.  Translate it into German."

    

    print(prompt)
    if not prompt:
        print("No prompt provided. Exiting.")
        return

    try:
        output = call_ollama(prompt)
    except RuntimeError as e:
        show_text_window("Ollama Error", str(e))
        return

    show_text_window("Ollama Output", output)

if __name__ == "__main__":
    main()
