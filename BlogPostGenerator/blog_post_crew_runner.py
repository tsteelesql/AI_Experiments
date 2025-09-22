from crewai import Crew
from tasks import create_tasks
from utils import read_python_files

if __name__ == "__main__":
    code_context = read_python_files("./your_python_scripts")  # Replace with your folder
    tasks = create_tasks()

    crew = Crew(
        agents=[task.agent for task in tasks],
        tasks=tasks,
        process="sequential"
    )

    result = crew.kickoff(inputs={"input": code_context})  # ✅ Use kickoff + named input
    print("\n✅ Final Blog Post:\n")
    print(result)
