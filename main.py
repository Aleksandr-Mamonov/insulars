from flask import Flask, url_for, redirect, request, render_template, session
from flask_socketio import SocketIO, emit, send, join_room, leave_room

import json
import sqlite3
import uuid

from config import MIN_PLAYERS, MAX_PLAYERS

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
# Run command
# flask --app main run --debug

# app.secret_key = "7f7c27265646902d9775e9fa1369fbf200cde69c"


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def _join_player_to_room(player_name, room_id):
    # TODO: validate player_name and room_id
    con = sqlite3.connect("insulars.db")
    con.row_factory = dict_factory
    cur = con.cursor()
    res = cur.execute(f"SELECT uid FROM rooms WHERE uid='{room_id}'")
    room = res.fetchone()
    if not room:
        raise Exception("Room not found.")

    res = cur.execute(
        "SELECT player_name FROM room_players WHERE room_id=:room_id AND player_name=:player_name",
        {"room_id": room_id, "player_name": player_name},
    )
    player = res.fetchone()
    if player:
        raise Exception("Name is already used. Try another one.")

    cur.execute(
        f"""INSERT INTO room_players (room_id, player_name) VALUES ('{room_id}', '{player_name}')"""
    )
    con.commit()
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
    con = sqlite3.connect("insulars.db")
    cur = con.cursor()
    room_id = str(uuid.uuid4())
    # TODO: parameters SQL
    cur.execute(
        f"""INSERT INTO rooms (uid, owner) VALUES ('{room_id}', '{player_name}')"""
    )
    con.commit()
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

    con = sqlite3.connect("insulars.db")
    con.row_factory = dict_factory
    cur = con.cursor()
    res = cur.execute(
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
    players = res.fetchall()

    room = cur.execute(
        """
    SELECT game FROM rooms WHERE uid=:room_id
    """,
        {"room_id": room_id},
    ).fetchone()
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
    con = sqlite3.connect("insulars.db")
    con.row_factory = dict_factory
    cur = con.cursor()

    cur.execute(
        "UPDATE rooms SET game=:game WHERE uid=:room_id",
        {"game": json.dumps(game), "room_id": data["room_id"]},
    )
    con.commit()
    emit(
        "game_started",
        {"game": game},
        to=data["room_id"],
    )


@socketio.on("end_game")
def handle_game_end(data):
    con = sqlite3.connect("insulars.db")
    con.row_factory = dict_factory
    cur = con.cursor()

    cur.execute(
        "UPDATE rooms SET game=NULL WHERE uid=:room_id",
        {"room_id": data["room_id"]},
    )
    con.commit()
    emit(
        "game_ended",
        {"msg": "Game ended!"},
        to=data["room_id"],
    )


if __name__ == "__main__":
    socketio.run(app)
