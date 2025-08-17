# Flask Web Game Framework
## Description
This is a simple web game framework built using Flask, a lightweight Python web application framework. The framework allows users to create games with basic state management and user interactions.

#### Intial Prompt

Act as an expert python programmer.  
Write code using python for a Star Wars life counter application. It should set starting life to 30 and support two players.  Have buttons to raise and lower life totals, an indicator of the current first player, which can be updated, and a toggle for having the "Force", which either or both players may have at the same time.
Use Flask to generate the application as a basic web application.

The additional criteria need met:

The buttons should scale when the window is expanded.

When Player 1 is the first player, change the color to blue for only these elements:

a. The Player 1/Player 2 labels

b. The current life totals for both players

c. The first player label

When Player 2 becomes the first player, change the color to red for the same elements.

All other elements should remain a default grey background, and not update.


## Features
- Built using Flask
- State management for players
- User interaction handling
- HTML template rendering

## Getting Started
### Prerequisites
- Required: Python 3.x

### Installation
```bash
pip install flask
```

### Development Environment
For development, ensure you have a code editor or IDE with Flask support. The recommended setup includes:

- Flask installed via pip
- A local web server like Flask's built-in server (default)

## Usage
To use the framework:
1. Run the application using `python app.py` in your terminal.
2. Open your web browser and navigate to `http://localhost:5000/`.
3. Use the form inputs to interact with the game state.

## How It Works
#### Game State Management
This part of the code is responsible for managing the game's state, including player lives and turn order.

```python
game_state = {
    "player1_life": 30,
    "player2_life": 30,
    "first_player": 1,
    "player1_force": False,
    "player2_force": False
}
```

#### Game Logic Handling
This snippet handles the game's logic, including player actions and updates.

```python
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")

        # Update player life based on action
        if action == "p1_inc":
            game_state["player1_life"] += 1
        elif action == "p1_dec":
            game_state["player1_life"] -= 1
        # ...

        return redirect(url_for("index"))
```

#### Rendering the Game State
This part renders the current state of the game in the web page.

```python
return render_template("index.html", state=game_state)
```

## Example
To demonstrate how to use the framework, consider a scenario where you want to update player life when the "p1_inc" action is selected. Here's an example:

### Sample Input
Submit `action=p1_inc` in the form.

### Expected Output
- Player 1's life will increase by one.
- Redirect back to the game page.

## Customization
This framework allows for easy customization through:
- Changing the game state variables and their initial values.
- Modifying or adding new player actions.
- Updating the game logic to accommodate different game scenarios.
