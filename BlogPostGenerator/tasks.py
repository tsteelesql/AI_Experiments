from crewai import Task
from agents import initial_writer, technical_editor, writing_editor

def create_tasks():
    write_task = Task(
        description="Read the provided Python scripts and write an excited blog post for a low-to-medium technical audience. Highlight interesting use cases and explain them like a teacher.",
        expected_output="A blog post draft that covers the scripts and their use cases.",
        agent=initial_writer,
        inputs=["input"],        # ← match kickoff key
        outputs=["blog_post"]    # ← this task’s output name
    )

    tech_edit_task = Task(
        description="Review the blog post for technical accuracy. Point out any mistakes or misleading explanations.",
        expected_output="A technically accurate version of the blog post with comments or corrections.",
        agent=technical_editor,
        inputs=["blog_post"],    # ← takes previous output
        outputs=["reviewed_post"]
    )

    writing_edit_task = Task(
        description="Edit the blog post for grammar, spelling, and flow. Make it engaging and well-written.",
        expected_output="A polished blog post ready for publishing.",
        agent=writing_editor,
        inputs=["reviewed_post"], # ← takes previous output
        outputs=["final_post"]
    )

    return [write_task, tech_edit_task, writing_edit_task]
