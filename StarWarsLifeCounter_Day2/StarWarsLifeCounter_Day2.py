import tkinter as tk
from tkinter import font

class LifeCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Star Wars Life Counter")

        # Scalable font
        self.default_font = font.Font(family="Helvetica", size=12)
        self.root.bind("<Configure>", self.resize_font)

        # Player states
        self.life = [30, 30]
        self.has_force = [False, False]
        self.first_player = 0

        # UI Elements
        self.create_widgets()

    def resize_font(self, event):
        new_size = max(12, int(event.width / 30))
        self.default_font.configure(size=new_size)

    def create_widgets(self):
        # Player labels
        self.p1_label = tk.Label(self.root, text="Player 1", font=self.default_font)
        self.p2_label = tk.Label(self.root, text="Player 2", font=self.default_font)
        self.p1_label.grid(row=0, column=0, columnspan=2)
        self.p2_label.grid(row=0, column=2, columnspan=2)

        # Life totals
        self.p1_life = tk.Label(self.root, text=str(self.life[0]), font=self.default_font)
        self.p2_life = tk.Label(self.root, text=str(self.life[1]), font=self.default_font)
        self.p1_life.grid(row=1, column=0, columnspan=2)
        self.p2_life.grid(row=1, column=2, columnspan=2)

        # Life control buttons
        tk.Button(self.root, text="+", font=self.default_font, command=lambda: self.change_life(0, 1)).grid(row=2, column=0)
        tk.Button(self.root, text="-", font=self.default_font, command=lambda: self.change_life(0, -1)).grid(row=2, column=1)
        tk.Button(self.root, text="+", font=self.default_font, command=lambda: self.change_life(1, 1)).grid(row=2, column=2)
        tk.Button(self.root, text="-", font=self.default_font, command=lambda: self.change_life(1, -1)).grid(row=2, column=3)

        # Force toggles
        self.p1_force_btn = tk.Button(self.root, text="Force: OFF", font=self.default_font, command=lambda: self.toggle_force(0))
        self.p2_force_btn = tk.Button(self.root, text="Force: OFF", font=self.default_font, command=lambda: self.toggle_force(1))
        self.p1_force_btn.grid(row=3, column=0, columnspan=2)
        self.p2_force_btn.grid(row=3, column=2, columnspan=2)

        # First player indicator
        self.first_player_label = tk.Label(self.root, text="First Player: 1", font=self.default_font)
        self.first_player_label.grid(row=4, column=0, columnspan=4)

        # Toggle first player button
        tk.Button(self.root, text="Toggle First Player", font=self.default_font, command=self.toggle_first_player).grid(row=5, column=0, columnspan=4)

    def change_life(self, player, delta):
        self.life[player] += delta
        if player == 0:
            self.p1_life.config(text=str(self.life[0]))
        else:
            self.p2_life.config(text=str(self.life[1]))

    def toggle_force(self, player):
        self.has_force[player] = not self.has_force[player]
        btn = self.p1_force_btn if player == 0 else self.p2_force_btn
        btn.config(text=f"Force: {'ON' if self.has_force[player] else 'OFF'}")

    def toggle_first_player(self):
        self.first_player = 1 - self.first_player
        self.first_player_label.config(text=f"First Player: {self.first_player + 1}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LifeCounterApp(root)
    root.mainloop()
