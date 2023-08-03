from flask import Flask, url_for, redirect, request, render_template, session
from flask_socketio import SocketIO, emit, send, join_room, leave_room

import json
import sqlite3
import uuid

from config import MIN_PLAYERS, MAX_PLAYERS, GAME_ROUNDS
from database import select_one_from_db, select_all_from_db, write_to_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
# Run command
# flask --app main run --debug

# app.secret_key = "7f7c27265646902d9775e9fa1369fbf200cde69c"


def _join_player_to_room(player_name, room_id):
    # TODO: validate player_name and room_id
    room = select_one_from_db(
        "SELECT uid FROM rooms WHERE uid=:room_id",
        {"room_id": room_id},
    )
    if not room:
        raise Exception("Room not found.")

    player = select_one_from_db(
        "SELECT player_name FROM room_players WHERE room_id=:room_id AND player_name=:player_name",
        {"room_id": room_id, "player_name": player_name},
    )
    if player:
        raise Exception("Name is already used. Try another one.")

    write_to_db(
        "INSERT INTO room_players (room_id, player_name) VALUES (:room_id, :player_name)",
        {"room_id": room_id, "player_name": player_name},
    )
    session["player_name"] = player_name


@app.route("/")
def index():
    return render_template("index.html", room_id=request.args.get("room_id", ""))


@app.route("/room/<room_id>", methods=["GET"])
def room(room_id):
    player_name = session.get("player_name")
    return render_template("app.html", player_name=player_name, room_id=room_id)


@app.route("/create_room", methods=["POST"])
def create_room():
    player_name = request.form["player_name"]
    room_id = str(uuid.uuid4())
    write_to_db(
        "INSERT INTO rooms (uid, owner) VALUES (:room_id, :player_name)",
        {"room_id": room_id, "player_name": player_name},
    )
    _join_player_to_room(player_name=player_name, room_id=room_id)
    return redirect(url_for("room", room_id=room_id))


@app.route("/join_room", methods=["POST"])
def handle_join_room():
    room_id = request.form["room_id"]
    player_name = request.form["player_name"]
    _join_player_to_room(player_name=player_name, room_id=room_id)
    return redirect(url_for("room", room_id=room_id))


@socketio.on("player_enter")
def handle_player_enter(data):
    room_id = data["room_id"]
    join_room(room_id)

    players = select_all_from_db(
        """
    SELECT
        rp.player_name, 
        r.owner=rp.player_name AS is_owner
    FROM room_players AS rp
    INNER JOIN rooms AS r ON r.uid=rp.room_id
    WHERE rp.room_id=:room_id
    """,
        {"room_id": room_id},
    )
    print(players)

    room = select_one_from_db(
        "SELECT game FROM rooms WHERE uid=:room_id",
        {"room_id": room_id},
    )
    emit(
        "room_entered",
        {
            "players": players,
            "config": {"MIN_PLAYERS": MIN_PLAYERS, "MAX_PLAYERS": MAX_PLAYERS},
            "game": json.loads(room["game"]) if room["game"] else None,
        },
        to=room_id,
    )


@socketio.on("start_game")
def handle_game_start(data):
    game = {"round": 1}
    write_to_db(
        "UPDATE rooms SET game=:game WHERE uid=:room_id",
        {"game": json.dumps(game), "room_id": data["room_id"]},
    )
    emit(
        "game_started",
        {"game": game},
        to=data["room_id"],
    )


@socketio.on("end_round")
def handle_round_end(data):
    result = select_one_from_db(
        "SELECT game FROM rooms WHERE uid=:room_id", {"room_id": data["room_id"]}
    )
    game = result["game"]
    # Update to next round
    game = json.loads(game)
    game["round"] += 1

    # That was last round, so game ended. Show game results.
    if game["round"] > GAME_ROUNDS:
        # TODO
        data["game_results"] = "Results of a game..."
        handle_game_end(data=data)
    else:
        write_to_db(
            "UPDATE rooms SET game=:game WHERE uid=:room_id",
            {"game": json.dumps(game), "room_id": data["room_id"]},
        )
        emit(
            "round_started",
            {"game": game},
            to=data["room_id"],
        )


@socketio.on("end_game")
def handle_game_end(data):
    write_to_db(
        "UPDATE rooms SET game=NULL WHERE uid=:room_id", {"room_id": data["room_id"]}
    )
    emit(
        "game_ended",
        {"msg": "Game ended!", "Game results": data.get("game_results")},
        to=data["room_id"],
    )


if __name__ == "__main__":
    socketio.run(app)
