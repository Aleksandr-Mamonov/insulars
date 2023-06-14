from flask import Flask, url_for, redirect, request, render_template
from flask_socketio import SocketIO, emit, send, join_room, leave_room


import sqlite3
import uuid

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/room/<room_id>/<player_name>", methods=["GET"])
def room(room_id, player_name):
    return render_template("app.html", player_name=player_name, room_id=room_id)


@app.route("/create_room", methods=["POST"])
def create_room():
    player_name = request.form["player_name"]
    con = sqlite3.connect("insulars.db")
    cur = con.cursor()
    room_id = uuid.uuid4()
    cur.execute(f"""INSERT INTO rooms VALUES ('{room_id}')""")
    con.commit()
    return redirect(url_for("room", room_id=room_id, player_name=player_name))


@app.route("/join_room", methods=["POST"])
def handle_join_room():
    # TODO: validate player_name and room_id
    player_name = request.form["player_name"]
    room_id = request.form["room_id"]
    return redirect(url_for("room", room_id=room_id, player_name=player_name))


@socketio.on("player_enter")
def handle_player_enter(json):
    print(f"received args: {json}")
    print(request.sid)
    print(json)
    room_id = json["room_id"]
    player_name = json["player_name"]
    join_room(room_id)
    con = sqlite3.connect("insulars.db")
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(
        f"""INSERT INTO room_players (room_id, player_name, sid) VALUES ('{room_id}', '{player_name}', '{request.sid}')"""
    )
    con.commit()

    res = cur.execute(f"SELECT player_name FROM room_players WHERE room_id='{room_id}'")
    players = res.fetchall()
    # players = [x[0] for x in players]
    print(players)
    emit("room_entered", {"players": players}, to=room_id)


if __name__ == "__main__":
    socketio.run(app)
