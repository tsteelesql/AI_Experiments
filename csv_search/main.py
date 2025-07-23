import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import glob

# Constants
CSV_DIRECTORY = '' # 🔁 Change this to your actual directory
CHUNK_SIZE = 100_000  # Adjust based on available memory

# GUI Application
class CSVSearcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV Search Tool")
        self.geometry("400x250")
        #self.create_widgets()

#    def create_widgets(self):
        # Labels and entry fields
        ttk.Label(self, text="File Identifier").pack(pady=5)
        self.file_id_entry = ttk.Entry(self, width=40)
        self.file_id_entry.pack()

        ttk.Label(self, text="Search Column").pack(pady=5)
        self.search_col_entry = ttk.Entry(self, width=40)
        self.search_col_entry.pack()

        ttk.Label(self, text="Search String").pack(pady=5)
        self.search_str_entry = ttk.Entry(self, width=40)
        self.search_str_entry.pack()

        # Search button
        ttk.Button(self, text="Search", command=self.search_files).pack(pady=15)

    def search_files(self):
        file_id = self.file_id_entry.get().strip()
        search_col = self.search_col_entry.get().strip()
        search_str = self.search_str_entry.get().strip()

        if not file_id or not search_col or not search_str:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        pattern = os.path.join(CSV_DIRECTORY, f"*{file_id}*.csv")
        matching_files = glob.glob(pattern)
        if not matching_files:
            messagebox.showinfo("No Files Found", "No matching files were found.")
            return

        matched_rows = []
        for file_path in matching_files:
            try:
                for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE):
                    if search_col not in chunk.columns:
                        continue
                    chunk['__source_file__'] = os.path.basename(file_path)  # Add file name as new column
                    results = chunk[chunk[search_col].astype(str).str.lower() == search_str.lower()]
                    if not results.empty:
                        matched_rows.append(results)
            except Exception as e:
                messagebox.showerror("Processing Error", f"Error reading {file_path}:\n{str(e)}")

        if matched_rows:
            self.show_results(pd.concat(matched_rows, ignore_index=True))
        else:
            messagebox.showinfo("No Matches", "No rows matched the given criteria.")

    def show_results(self, dataframe):
        result_window = tk.Toplevel(self)
        result_window.title("Search Results")
        tree = ttk.Treeview(result_window)
        tree.pack(fill='both', expand=True)

        tree["columns"] = list(dataframe.columns)
        tree["show"] = "headings"
        for col in dataframe.columns:
            tree.heading(col, text=col)

        for _, row in dataframe.iterrows():
            tree.insert("", "end", values=list(row))

# Run App
if __name__ == "__main__":
    app = CSVSearcher()
    app.mainloop()
