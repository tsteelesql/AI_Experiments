from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Game state
game_state = {
    "player1_life": 30,
    "player2_life": 30,
    "first_player": 1,
    "player1_force": False,
    "player2_force": False
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "p1_inc":
            game_state["player1_life"] += 1
        elif action == "p1_dec":
            game_state["player1_life"] -= 1
        elif action == "p2_inc":
            game_state["player2_life"] += 1
        elif action == "p2_dec":
            game_state["player2_life"] -= 1
        elif action == "toggle_first":
            game_state["first_player"] = 2 if game_state["first_player"] == 1 else 1
        elif action == "toggle_force_p1":
            game_state["player1_force"] = not game_state["player1_force"]
        elif action == "toggle_force_p2":
            game_state["player2_force"] = not game_state["player2_force"]

        return redirect(url_for("index"))

    return render_template("index.html", state=game_state)

if __name__ == "__main__":
    app.run(debug=True)
