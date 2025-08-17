import tkinter as tk
from tkinter import font

class StarWarsLifeCounter:
    def __init__(self, root):
        self.root = root
        self.root.title("Star Wars Life Counter")

        # Life totals and force status
        self.life = [30, 30]
        self.force = [False, False]
        self.first_player = 0  # 0 for Player 1, 1 for Player 2

        # Fonts
        self.default_font = font.Font(family="Helvetica", size=12)
        self.large_font = font.Font(family="Helvetica", size=20, weight="bold")

        # Configure grid to scale
        for i in range(6):
            self.root.rowconfigure(i, weight=1)
        for j in range(4):
            self.root.columnconfigure(j, weight=1)

        self.create_widgets()
        self.update_colors()

    def create_widgets(self):
        # Player Labels
        self.player_labels = [
            tk.Label(self.root, text="Player 1", font=self.large_font),
            tk.Label(self.root, text="Player 2", font=self.large_font)
        ]
        self.player_labels[0].grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.player_labels[1].grid(row=0, column=2, columnspan=2, sticky="nsew")

        # Life Totals
        self.life_labels = [
            tk.Label(self.root, text=str(self.life[0]), font=self.large_font),
            tk.Label(self.root, text=str(self.life[1]), font=self.large_font)
        ]
        self.life_labels[0].grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.life_labels[1].grid(row=1, column=2, columnspan=2, sticky="nsew")

        # Life Buttons
        self.create_life_buttons()

        # Force Toggles
        self.force_buttons = [
            tk.Button(self.root, text="Toggle Force P1", command=lambda: self.toggle_force(0)),
            tk.Button(self.root, text="Toggle Force P2", command=lambda: self.toggle_force(1))
        ]
        self.force_buttons[0].grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.force_buttons[1].grid(row=4, column=2, columnspan=2, sticky="nsew")

        # First Player Indicator
        self.first_player_label = tk.Label(self.root, text="First Player: Player 1", font=self.large_font)
        self.first_player_label.grid(row=5, column=0, columnspan=4, sticky="nsew")

        # Switch First Player Button
        self.switch_button = tk.Button(self.root, text="Switch First Player", command=self.switch_first_player)
        self.switch_button.grid(row=3, column=1, columnspan=2, sticky="nsew")

    def create_life_buttons(self):
        # Player 1
        tk.Button(self.root, text="+", command=lambda: self.change_life(0, 1)).grid(row=2, column=0, sticky="nsew")
        tk.Button(self.root, text="-", command=lambda: self.change_life(0, -1)).grid(row=2, column=1, sticky="nsew")
        # Player 2
        tk.Button(self.root, text="+", command=lambda: self.change_life(1, 1)).grid(row=2, column=2, sticky="nsew")
        tk.Button(self.root, text="-", command=lambda: self.change_life(1, -1)).grid(row=2, column=3, sticky="nsew")

    def change_life(self, player, delta):
        self.life[player] += delta
        self.life_labels[player].config(text=str(self.life[player]))

    def toggle_force(self, player):
        self.force[player] = not self.force[player]
        status = "Has Force" if self.force[player] else "No Force"
        self.force_buttons[player].config(text=f"{status} P{player + 1}")

    def switch_first_player(self):
        self.first_player = 1 - self.first_player
        self.first_player_label.config(text=f"First Player: Player {self.first_player + 1}")
        self.update_colors()

    def update_colors(self):
        color = "blue" if self.first_player == 0 else "red"
        self.player_labels[0].config(bg=color)
        self.player_labels[1].config(bg=color)
        self.life_labels[0].config(bg=color)
        self.life_labels[1].config(bg=color)
        self.first_player_label.config(bg=color)

        # Reset other buttons to default grey
        for btn in self.force_buttons:
            btn.config(bg="lightgrey")
        self.switch_button.config(bg="lightgrey")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = StarWarsLifeCounter(root)
    root.mainloop()
