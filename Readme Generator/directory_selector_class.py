# file_selector.py
import tkinter as tk
from tkinter import filedialog, ttk

class DirectorySelectorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("500x300")
        self.root.title("File Selector")

        self.selected_file_path = tk.StringVar()

        self.dropdown_label = tk.Label(self.root, text="Choose a directory:")
        self.dropdown_label.pack(pady=5)

        self.recent_dirs = [filedialog.askdirectory(title="Select a directory")]
        self.dir_combobox = ttk.Combobox(self.root, values=self.recent_dirs, state="readonly")
        self.dir_combobox.pack(pady=5)
        self.dir_combobox.current(0)
        self.dir_combobox.bind("<<ComboboxSelected>>", self.update_file_list)

        self.browse_button = tk.Button(self.root, text="Browse Directory", command=self.browse_directory)
        self.browse_button.pack(pady=5)

        self.path_label = tk.Label(self.root, textvariable=self.selected_file_path, wraplength=400)
        self.path_label.pack(pady=5)

        self.save_button = tk.Button(self.root, text="Generate Readme", command=self._save_path)
        self.save_button.pack(pady=10)

        self.saved_path = None


    def browse_directory(self):
        selected_dir = filedialog.askdirectory(title="Select a directory")
        if selected_dir:
            self.selected_file_path.set(selected_dir)


    def update_file_list(self, event):
        pass  # Optional logic


    def _save_path(self):
        self.saved_path = self.dir_combobox.get()
        print(f"Saved directory path: {self.saved_path}")
        self.root.destroy()  # Closes the window


    def run(self):
        self.root.mainloop()


    def get_saved_path(self):
        return self.saved_path
