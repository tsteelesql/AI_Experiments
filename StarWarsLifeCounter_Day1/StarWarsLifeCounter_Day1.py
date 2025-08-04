import tkinter as tk
import tkinter.font as tkFont

class StarWarsLifeCounter:
    def __init__(self, root):
        self.root = root
        self.root.title("🌌 Star Wars Life Counter")

        self.life_totals = {"Player 1": 30, "Player 2": 30}
        self.force_status = {"Player 1": False, "Player 2": False}
        self.first_player = "Player 1"

        # Create scalable fonts
        self.title_font = tkFont.Font(family="Arial", size=14, weight="bold")
        self.label_font = tkFont.Font(family="Arial", size=12)

        # Make root grid expandable
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.create_ui()

        # Bind resize event to adjust fonts
        self.root.bind("<Configure>", self.on_resize)

    def create_ui(self):
        for i, player in enumerate(self.life_totals):
            frame = tk.Frame(self.root, padx=10, pady=10, bd=2, relief="groove")
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            # Configure frame grid
            frame.grid_columnconfigure(0, weight=1)
            for r in range(4):
                frame.grid_rowconfigure(r, weight=1)

            label = tk.Label(frame, text=player, font=self.title_font)
            label.grid(row=0, column=0, sticky="nsew")

            self.life_label(player, frame, row=1)
            self.life_buttons(player, frame, row=2)
            self.force_toggle(player, frame, row=3)

        self.root.grid_rowconfigure(1, weight=0)
        self.first_player_label = tk.Label(self.root, text=f"🎲 First Player: {self.first_player}", font=self.label_font)
        self.first_player_label.grid(row=1, column=0, columnspan=2, pady=5)

        change_button = tk.Button(self.root, text="🔁 Switch First Player", font=self.label_font, command=self.switch_first_player)
        change_button.grid(row=2, column=0, columnspan=2, pady=5)

    def life_label(self, player, frame, row):
        label = tk.Label(frame, text=f"Life: {self.life_totals[player]}", font=self.label_font)
        label.grid(row=row, column=0, sticky="nsew")
        setattr(self, f"{player}_life_label", label)

    def life_buttons(self, player, frame, row):
        b_frame = tk.Frame(frame)
        b_frame.grid(row=row, column=0, sticky="nsew")
        b_frame.grid_columnconfigure(0, weight=1)
        b_frame.grid_columnconfigure(1, weight=1)

        plus_btn = tk.Button(b_frame, text="+", font=self.label_font, command=lambda: self.update_life(player, 1))
        minus_btn = tk.Button(b_frame, text="-", font=self.label_font, command=lambda: self.update_life(player, -1))
        plus_btn.grid(row=0, column=0, sticky="nsew")
        minus_btn.grid(row=0, column=1, sticky="nsew")

    def force_toggle(self, player, frame, row):
        btn = tk.Button(frame, font=self.label_font, command=lambda: self.toggle_force(player))
        btn.grid(row=row, column=0, sticky="nsew", pady=5)
        setattr(self, f"{player}_force_btn", btn)
        self.update_force_display(player)

    def update_life(self, player, change):
        self.life_totals[player] += change
        getattr(self, f"{player}_life_label").config(text=f"Life: {self.life_totals[player]}")

    def toggle_force(self, player):
        self.force_status[player] = not self.force_status[player]
        self.update_force_display(player)

    def update_force_display(self, player):
        status = "✅ Has the Force" if self.force_status[player] else "❌ No Force"
        getattr(self, f"{player}_force_btn").config(text=status)

    def switch_first_player(self):
        self.first_player = "Player 2" if self.first_player == "Player 1" else "Player 1"
        self.first_player_label.config(text=f"🎲 First Player: {self.first_player}")

    def on_resize(self, event):
        # Adjust font sizes based on window width
        new_title_size = max(10, int(event.width / 25))
        new_label_size = max(8, int(event.width / 35))
        self.title_font.config(size=new_title_size)
        self.label_font.config(size=new_label_size)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = StarWarsLifeCounter(root)
    root.mainloop()
