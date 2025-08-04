# Star Wars Life Counter
Experiment creating a basic life counter using CoPilot to improve prompting, with three iterations.

#### Initial Prompt
Write code using python for a Star Wars life counter application. It should set starting life to 30 and support two players.  Have buttons to raise and lower life totals, an indicator of the current first player, which can be updated, and a toggle for having the "Force", which either or both players may have at the same time.

#### Iteration 1
Can you make the window and frames for each player larger, so they scale when the window gets bigger?

#### Iteration 2
Make the content inside the frame also scale with the frame when expanded.

#### Iteration 3
Make the text in the labels also scale when expanding.

## Features
- Tkinter library for GUI creation
- Customizable fonts and layout
- Automatic font size adjustment on window resize

## Getting Started
### Requirements
- Python 3.7 or later
- tkinter library (comes bundled with Python)

### OS-Specific Instructions for Tkinter Installation
For Linux:
```bash
sudo apt-get install python3-tk
```
For MacOS:
```bash
brew install tk
```

## Usage
1. Run the application using `python star_wars_life_counter.py`.
2. The GUI will display the life totals of two players, with buttons to increase or decrease their lives.
3. A button to switch the first player between "Player 1" and "Player 2".
4. Force status for each player is displayed on a separate button.

## How It Works
### `StarWarsLifeCounter` Class Initialization
The application initializes a new instance of the `StarWarsLifeCounter` class, passing the Tkinter root window as an argument.
### GUI Creation
The `create_ui` method creates the main GUI elements:
- Frames for each player
- Labels to display player names and life totals
- Buttons to increase or decrease lives and toggle force status
- Label to display the current first player

```python
    # Create scalable fonts
    self.title_font = tkFont.Font(family="Arial", size=14, weight="bold")
    self.label_font = tkFont.Font(family="Arial", size=12)

    # Make root grid expandable
    self.root.grid_columnconfigure(0, weight=1)
    self.root.grid_columnconfigure(1, weight=1)
    self.root.grid_rowconfigure(0, weight=1)

    self.create_ui()
```

### Button Commands
Each button command updates the corresponding life totals or force status when clicked:
```python
# Update life total on button click
def update_life(self, player, change):
    self.life_totals[player] += change
    getattr(self, f"{player}_life_label").config(text=f"Life: {self.life_totals[player]}")

# Toggle force status on button click
def toggle_force(self, player):
    self.force_status[player] = not self.force_status[player]
    self.update_force_display(player)
```

### First Player Switch Button Command
Switches the first player when clicked:
```python
def switch_first_player(self):
    self.first_player = "Player 2" if self.first_player == "Player 1" else "Player 1"
    self.first_player_label.config(text=f"🎲 First Player: {self.first_player}")
```

## Example
The following is an example of how to run the application:
```bash
python star_wars_life_counter.py
```
Output:

<img width="367" height="391" alt="image" src="https://github.com/user-attachments/assets/ac202ec3-3b82-4528-8a52-704b14879520" />

## Customization
The following are suggestions for possible extensions or customization:
- Add more player options or teams.
- Allow players to input their own life totals at the start of the game.
- Implement a game loop that automatically updates lives after each turn.
