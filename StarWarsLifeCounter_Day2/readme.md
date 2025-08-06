# Star Wars Life Counter
A simple GUI application to track players' lives in a game of Star Wars.

## Description
This script creates a simple graphical user interface (GUI) for tracking players' lives in a game of Star Wars. It allows users to add or subtract lives from each player, toggle their force abilities, and switch between the two players. The background color of the GUI changes based on which player is currently selected.

## Features
- tkinter library for creating the GUI
- Python for coding

## Getting Started
### Requirements
- Python 3.x
- pip (for installing dependencies)

No additional libraries are required, as the script only uses built-in Python modules.

## Usage
1. Run the script using `python life_counter.py`.
2. A GUI window will appear with two player labels, their respective lives counters, and buttons to add or subtract lives.
3. Click on one of the force buttons to toggle its ability for the selected player.
4. Click on the "Toggle First Player" button to switch between players.

## How It Works
### Resizing Font

The `resize_font` method is called whenever the window is resized. This updates the font size based on the new window dimensions.

#### Code Snippet
```python
def resize_font(self, event):
    new_size = max(12, int(min(event.width, event.height) / 30))
    self.default_font.configure(size=new_size)
```

#### Explanation

This code is called when the window is resized. It calculates a new font size based on the minimum of the window's width and height, and sets this size for all labels using `self.default_font`.

### Creating Widgets

The `create_widgets` method creates all the UI elements in the GUI.

#### Code Snippet
```python
def create_widgets(self):
    # ... (other code)

    self.p1_label = tk.Label(self.root, text="Player 1", font=self.default_font)
    # ... (other code)

    # Add widgets to background update list
    self.bg_widgets = [
        # ... (other widgets)
    ] + self.btns
```

#### Explanation

This method creates all the UI elements for the GUI. The `p1_label`, `p2_label`, etc., are created and placed in their respective positions on the window.

### Updating Background

The `update_background` method is called whenever a player's force ability or first player status changes. It updates the background color of the GUI based on the selected player.

#### Code Snippet
```python
def update_background(self):
    color = "lightblue" if self.first_player == 0 else "lightcoral"
    self.root.configure(bg=color)
    for widget in self.bg_widgets:
        widget.configure(bg=color)
```

#### Explanation

This method updates the background color of the GUI based on the selected player. If it's player 1, the background is set to light blue; otherwise, it's set to light coral.

## Example
Here is an example use case:

Player 1 starts with 30 lives and no force ability. Player 2 also starts with 30 lives and no force ability.

```
Player 1: 30
Player 2: 30
Force: OFF
First Player: 1
```

After Player 1 clicks the "+" button, their life count increases by 1:

```
Player 1: 31
Player 2: 30
Force: OFF
First Player: 1
```

## Customization
This script can be customized further by adding more features or modifying existing ones. For example, you could add a timer that decreases over time if a player's force ability is active, or create a separate GUI for tracking the score.
