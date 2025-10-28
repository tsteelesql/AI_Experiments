"""
Main entry point for the Jira Admin Task Generator.
"""

from gui import JiraTaskGeneratorGUI


def main():
    """Main function to start the application."""
    app = JiraTaskGeneratorGUI()
    app.run()


if __name__ == "__main__":
    main()
