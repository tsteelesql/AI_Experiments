# Star Wars Life Counter
A simple graphical application for tracking life totals and force status in a Star Wars context.

## Features
- Uses tkinter library for GUI setup.
- Applies OOP principles through class definition.

## Getting Started
### Required Python Version:
Python 3.x (tested on Python 3.9)

### Dependencies:
```bash
pip install tk
```

### Installing Tkinter (for macOS and Linux):
```bash
sudo apt-get install python3-tk
```

### Running the Application:
```bash
python star_wars_life_counter.py
```

## Usage
To run the application:

1. Launch the `star_wars_life_counter.py` script.
2. The GUI will appear, displaying life totals and force status for two players.
3. Click on buttons to increase or decrease a player's life total, toggle their force status, or switch between players.

## How It Works
### Creating Widgets

The `StarWarsLifeCounter` class creates the necessary widgets (labels, buttons, etc.) using the `grid()` method for layout management.

#### Code Snippet
```python
self.player_labels = [
    tk.Label(self.root, text="Player 1", font=self.large_font),
    tk.Label(self.root, text="Player 2", font=self.large_font)
]
# ...

self.force_buttons = [
    tk.Button(self.root, text="Toggle Force P1", command=lambda: self.toggle_force(0)),
    tk.Button(self.root, text="Toggle Force P2", command=lambda: self.toggle_force(1))
]

self.create_widgets()
```

#### Explanation
This code creates two labels for player names and two buttons to toggle force status. Each label and button is assigned a command using the `command` parameter of the `tkinter.Button` class.

### Updating Colors

The `update_colors()` method changes the background color of selected elements (player labels, life labels) based on their current state.

#### Code Snippet
```python
self.update_colors()
```

#### Explanation
This method updates the colors of all player-related elements by comparing their states to a predefined set. When a player's force status is updated, it triggers this update function.

### Switching First Player

The `switch_first_player()` method changes who is considered "first" when calculating life totals and forces.

#### Code Snippet
```python
def switch_first_player(self):
    self.first_player = 1 - self.first_player
    # ...
```

#### Explanation
This method simply toggles the value of `self.first_player` by subtracting its current value from itself, thus switching between Player 1 and Player 2.

## Example
```python
# Initialize application
root = tk.Tk()
app = StarWarsLifeCounter(root)
# Run main loop
root.mainloop()
```

## Customization
To extend the functionality of this application, you can:

*   Modify or create new widgets to add additional features.
*   Improve existing logic and algorithms to optimize performance.
*   Create more complex data structures for player information.
