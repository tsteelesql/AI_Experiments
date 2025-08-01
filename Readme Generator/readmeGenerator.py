import ollama

client = ollama.Client()


model = "llama3.2"
DIRECTORY = 'C:/Users/tstee/PycharmProjects/AI_Code_Testing/main.py'
template = "Templates/readme_template.txt"
script = ''

#prompt = f"Analyze this document: $(cat {os.path.join(DIRECTORY,script)})"

#print(os.path.join(DIRECTORY,script))

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

print("Response from Ollama:")
print(response.response)
