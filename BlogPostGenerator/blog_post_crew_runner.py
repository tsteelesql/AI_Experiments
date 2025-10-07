from crewai import Crew
from tasks import create_tasks
from utils import read_python_files
from directory_selector_class import DirectorySelectorApp



if __name__ == "__main__":

    LocalFileSelector = DirectorySelectorApp()
    LocalFileSelector.run()

    # After the window closes, you can access the saved path
    selected_path = LocalFileSelector.get_saved_path()
    if selected_path:
        print(f"Main script received path: {selected_path}")


    code_context = read_python_files(selected_path)  # Replace with your folder
    tasks = create_tasks()

    crew = Crew(
        agents=[task.agent for task in tasks],
        tasks=tasks,
        process="sequential"
    )


    result = crew.kickoff(inputs={"input": code_context})  # ✅ Use kickoff + named input
    print("\n✅ Final Blog Post:\n")
    print(result)
