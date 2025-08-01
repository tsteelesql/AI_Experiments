import ollama
import tkinter as tk
from tkinter import messagebox

client = ollama.Client()

model = "llama3.2"
DIRECTORY = 'PycharmProjects/AI_Code_Testing/SWU_LifeCounter.py'
template = "Templates/readme_template.txt"
script = ''

def copy_to_clipboard():
    result = text_widget.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(result.strip())
    messagebox.showinfo("Copied", "Text copied to clipboard!")

# Create the main window
root = tk.Tk()
root.title("Result Display")
root.geometry("500x600")

# Frame to hold the Text widget and Scrollbar side by side
frame = tk.Frame(root)
frame.pack(pady=20, fill=tk.BOTH, expand=True)

# Create the Text widget
text_widget = tk.Text(frame, wrap=tk.WORD)
text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a vertical scrollbar
scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Link the scrollbar to the text widget
text_widget.config(yscrollcommand=scrollbar.set)

# Create a copy button
copy_button = tk.Button(root, text="Copy Result", command=copy_to_clipboard)
copy_button.pack(pady=10)


with open(DIRECTORY, 'r', encoding='utf-8') as f:
    file_content = f.read()

with open(template, 'r', encoding='utf-8') as f:
    prompt = f.read()

prompt += (f"<START OF SCRIPT>"
           f"{file_content}"
           f"<END OF SCRIPT>"
           f"📤 OUTPUT:"
           f"Your output should be valid GitHub markdown."
           f"Do not include any explanation or commentary — just the raw markdown text of the README.")


response = client.generate(model=model, prompt=prompt)

# Insert sample text
text_widget.insert(tk.END, response.response)

# Run the application
root.mainloop()
