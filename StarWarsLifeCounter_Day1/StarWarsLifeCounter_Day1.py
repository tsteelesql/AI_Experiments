import tkinter as tk

class StarWarsLifeCounter:
    def __init__(self, root):
        self.root = root
        self.root.title("🌟 Star Wars Life Counter")

        self.life_totals = {"Player 1": 30, "Player 2": 30}
        self.force_status = {"Player 1": False, "Player 2": False}
        self.first_player = "Player 1"

        self.create_ui()

    def create_ui(self):
        # Player Frames
        for i, player in enumerate(self.life_totals):
            frame = tk.Frame(self.root, padx=10, pady=10, bd=2, relief="groove")
            frame.grid(row=0, column=i, padx=10, pady=10)

            label = tk.Label(frame, text=player, font=("Arial", 14, "bold"))
            label.pack()

            self.life_label(player, frame)
            self.life_buttons(player, frame)
            self.force_toggle(player, frame)

        # First Player indicator
        self.first_player_label = tk.Label(self.root, text=f"🎲 First Player: {self.first_player}", font=("Arial", 12))
        self.first_player_label.grid(row=1, column=0, columnspan=2, pady=10)

        change_button = tk.Button(self.root, text="🔁 Switch First Player", command=self.switch_first_player)
        change_button.grid(row=2, column=0, columnspan=2, pady=5)

    def life_label(self, player, frame):
        label = tk.Label(frame, text=f"Life: {self.life_totals[player]}", font=("Arial", 12))
        label.pack()
        setattr(self, f"{player}_life_label", label)

    def life_buttons(self, player, frame):
        b_frame = tk.Frame(frame)
        b_frame.pack()
        tk.Button(b_frame, text="+", command=lambda: self.update_life(player, 1)).pack(side="left")
        tk.Button(b_frame, text="-", command=lambda: self.update_life(player, -1)).pack(side="left")

    def force_toggle(self, player, frame):
        btn = tk.Button(frame, text="🌌 Toggle Force", command=lambda: self.toggle_force(player))
        btn.pack()
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
        getattr(self, f"{player}_force_btn").config(text=f"{status}")

    def switch_first_player(self):
        self.first_player = "Player 2" if self.first_player == "Player 1" else "Player 1"
        self.first_player_label.config(text=f"🎲 First Player: {self.first_player}")

# Launch the app
if __name__ == "__main__":
    root = tk.Tk()
    app = StarWarsLifeCounter(root)
    root.mainloop()
