from crewai import Agent
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate

llm = ChatOllama(model="ollama/llama3.2", temperature=0.7)

# Prompt for Initial Writer
initial_writer_prompt = PromptTemplate(
    input_variables=["input"],
    template="""
You are a passionate Python educator. Based on the following codebase, write an excited blog post for a low-to-medium technical audience. Highlight interesting use cases and explain them like a teacher.

{input}
"""
)

initial_writer = Agent(
    role="Initial Writer",
    goal="Write an excited, educational blog post about Python scripts",
    backstory="You're a passionate Python educator who loves sharing cool use cases.",
    verbose=True,
    llm=llm,
    prompt=initial_writer_prompt
)

# Prompt for Technical Editor
technical_editor_prompt = PromptTemplate(
    input_variables=["input"],
    template="""
You are a senior Python developer and technical writer. Review the following blog post for technical accuracy. Point out any mistakes, misleading explanations, or areas that need clarification.

{input}
"""
)

technical_editor = Agent(
    role="Technical Editor",
    goal="Review the blog post for technical accuracy and code issues",
    backstory="You're a senior Python developer and technical writer with an eye for bugs.",
    verbose=True,
    llm=llm,
    prompt=technical_editor_prompt
)

# Prompt for Writing Editor
writing_editor_prompt = PromptTemplate(
    input_variables=["input"],
    template="""
You are a professional editor. Review the following blog post for grammar, spelling, and flow. Make it engaging, clear, and well-written for a general audience.

{input}
"""
)

writing_editor = Agent(
    role="Writing Editor",
    goal="Polish grammar, spelling, and flow of the blog post",
    backstory="You're a professional editor who ensures clarity and readability.",
    verbose=True,
    llm=llm,
    prompt=writing_editor_prompt
)
