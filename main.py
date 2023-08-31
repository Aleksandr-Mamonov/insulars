from flask import Flask, url_for, redirect, request, render_template, session
from flask_socketio import SocketIO, emit, send, join_room, leave_room

import json
import sqlite3
import uuid

from config import (
    MIN_PLAYERS,
    MAX_PLAYERS,
    GAME_ROUNDS,
    INITIAL_PLAYER_POINTS,
    CARDS_ON_TABLE_IN_ROUND,
    CARDS_IN_GAME,
)
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


def build_deck(game_id: str):
    # TODO: How we build a deck? What rules?
    result = select_all_from_db("SELECT name FROM cards", params={})
    # [{'name': 'Bridge'}, {'name': 'Hospital'}, {'name': 'School'}, {'name': 'Station'}]
    all_cards = [i["name"] for i in result]
    multiple = CARDS_IN_GAME // len(all_cards) + 1

    for card_name in all_cards * multiple:
        write_to_db(
            "INSERT INTO game_deck (game_id, card_name) VALUES (:game_id, :card_name)",
            {"game_id": game_id, "card_name": card_name},
        )


def draw_random_card_from_deck(game_id: str) -> dict:
    card = select_one_from_db(
        """
        SELECT 
            gd.card_id,
            c.name,
            c.points_to_succeed, 
            c.min_team, 
            c.max_team, 
            c.on_success, 
            c.on_failure 
        FROM game_deck AS gd 
        INNER JOIN cards AS c ON c.name=gd.card_name
        WHERE gd.game_id=:game_id 
        AND gd.available=TRUE 
        ORDER BY RANDOM() 
        LIMIT 1
        """,
        {"game_id": game_id},
    )

    try:
        card_id = card["card_id"]
    except TypeError as e:
        print("The deck is empty.")
        # TODO: What to do if deck is empty? Rebuild again?
        raise

    write_to_db(
        "UPDATE game_deck SET available=FALSE WHERE card_id=:card_id AND game_id=:game_id",
        {"card_id": card_id, "game_id": game_id},
    )
    return card


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
    room_id = data["room_id"]
    result = select_all_from_db(
        "SELECT player_name FROM room_players WHERE room_id=:room_id",
        {"room_id": room_id},
    )
    players = [i["player_name"] for i in result]
    all_players_points = {i["player_name"]: INITIAL_PLAYER_POINTS for i in result}
    # {'a': 10, 'b': 10}
    game_id = str(uuid.uuid4())
    build_deck(game_id)
    cards_on_table = [
        draw_random_card_from_deck(game_id) for _ in range(CARDS_ON_TABLE_IN_ROUND)
    ]
    game = {
        "game_id": game_id,
        "round": 1,
        "players": tuple(players),
        "players_order_in_round": players,
        "players_to_move": players,
        "active_player": players[0],
        "leader": players[0],
        "all_players_points": all_players_points,
        "round_common_account_points": 0,
        "cards_on_table": cards_on_table,
        "cards_selected_by_leader": [],
        "team_selected_by_leader": [],
    }
    write_to_db(
        "UPDATE rooms SET game=:game WHERE uid=:room_id",
        {"game": json.dumps(game), "room_id": room_id},
    )
    emit(
        "game_started",
        {"game": game},
        to=data["room_id"],
    )


def change_player_points(room_id, player_name, points: int):
    game = get_room_game(room_id)
    all_players_points = game["all_players_points"]

    all_players_points[player_name] = (all_players_points[player_name] + points)
    game["all_players_points"] = all_players_points
    store_room_game(room_id, game)

    return game


def change_project_points(room_id, points_delta: int):
    game = get_room_game(room_id)

    round_common_account_points = game["round_common_account_points"]
    round_common_account_points = (round_common_account_points + points_delta)

    game["round_common_account_points"] = round_common_account_points

    store_room_game(room_id, game)

    return game


@socketio.on("select_cards_from_table")
def handle_select_cards_from_table(data):
    """Card(s) can be selected only by leader in current round."""
    result = select_one_from_db(
        "SELECT game FROM rooms WHERE uid=:room_id", {"room_id": data["room_id"]}
    )
    game = json.loads(result["game"])

    for card in game["cards_on_table"]:
        card_id = card["card_id"]
        for selected_card_id in data["selected_cards_ids"]:
            if selected_card_id == card_id:
                game["cards_selected_by_leader"].append(card)
                break

    game["cards_on_table"].clear()
    write_to_db(
        "UPDATE rooms SET game=:game WHERE uid=:room_id",
        {"game": json.dumps(game), "room_id": data["room_id"]},
    )
    emit("cards_for_round_selected", {"game": game}, to=data["room_id"])


def get_room_game(room_id):
    result = select_one_from_db("SELECT game FROM rooms WHERE uid=:room_id", {"room_id": room_id})

    return json.loads(result["game"])


def store_room_game(room_id, game):
    write_to_db("UPDATE rooms SET game=:game WHERE uid=:room_id", {"game": json.dumps(game), "room_id": room_id})


def move_to_next_player(room_id):
    """ Change active player to next one"""

    game = get_room_game(room_id)

    game["active_player"] = game["players_to_move"][0]
    game["players_to_move"].pop(0)

    store_room_game(room_id, game)

    return game


def apply_project_result(game):
    # Check whether team succeeded or failed in ended round
    points_to_succeed = sum(
        [card["points_to_succeed"] for card in game["cards_selected_by_leader"]]
    )
    points_collected_by_team = game["round_common_account_points"]

    is_success = points_collected_by_team >= points_to_succeed
    if is_success:
        # TODO: Apply condition(s) on success from all selected card(s)
        rewards = [card["on_success"] for card in game["cards_selected_by_leader"]]
        print(f'Team succeeded in {game["round"]} round! Rewards: {rewards}')
    else:
        # TODO: Apply condition(s) on failure from all selected card(s)
        punishment = [card["on_failure"] for card in game["cards_selected_by_leader"]]
        print(f'Team failed in {game["round"]} round! Punishment: {punishment}')

    return is_success


def start_next_round(room_id, game):
    game["round"] += 1
    # That was last round, so game ended. Show game results.
    if game["round"] > GAME_ROUNDS:
        return None
    else:
        players_order_in_new_round = game["players_order_in_round"]
        # Rotate players order for next round
        players_order_in_new_round.append(players_order_in_new_round.pop(0))

        # Reset round common account
        game["round_common_account_points"] = 0
        new_cards_on_table = [
            draw_random_card_from_deck(game["game_id"])
            for _ in range(CARDS_ON_TABLE_IN_ROUND)
        ]
        game["cards_on_table"] = new_cards_on_table
        game["cards_selected_by_leader"] = []
        game["team_selected_by_leader"] = []

        game["players_order_in_round"] = players_order_in_new_round
        game["players_to_move"] = players_order_in_new_round
        game["active_player"] = players_order_in_new_round[0]
        game["leader"] = players_order_in_new_round[0]

        store_room_game(room_id, game)

        return game


@socketio.on('make_project_deposit')
def handle_make_project_deposit(data):
    """Player make a points deposit during project development"""

    room_id = data["room_id"]
    points = int(data['points'])

    change_player_points(room_id, data['player_name'], points)
    game = change_project_points(room_id, points)

    emit("project_deposited", {"game": game}, to=data["room_id"])
    emit("player_points_changed", {"game": game}, to=data["room_id"])

    # Remove player who already moved from a list
    game["players_to_move"].pop(0)
    store_room_game(room_id, game)

    has_player_to_move_next = len(game["players_to_move"]) > 0

    if has_player_to_move_next:
        game = move_to_next_player(room_id)
        emit("move_started", {"game": game}, to=data["room_id"])
    else:
        is_success = apply_project_result(game)
        emit("round_result", {"is_success": is_success}, to=data["room_id"])
        game = start_next_round(room_id, game)
        if game is None:
            write_to_db("UPDATE rooms SET game=NULL WHERE uid=:room_id", {"room_id": data["room_id"]})
            emit("game_ended", {"winner": 1}, to=data["rom_id"])
        else:
            emit("round_started", {"game": game}, to=data["room_id"])


@socketio.on("select_team_for_round")
def handle_select_team_for_round(data):
    """Team is selected by a leader.
    Team should include
        from min players of min(min_players from all selected cards)
        to max players of max(max_players from all selected cards).
    Data = {
    "game_id": game_id,
    "selected_players": [player_name1, player_name2 ...],
    }
    """
    result = select_one_from_db("SELECT game FROM rooms WHERE uid=:room_id", {"room_id": data["room_id"]})
    game = json.loads(result["game"])
    # Check whether card(s) for a given round were selected already or not
    if game["cards_selected_by_leader"] == []:
        # TODO
        raise
    # How many min and max players should be in a team
    min_players_in_team = min(
        [card["min_team"] for card in game["cards_selected_by_leader"]]
    )
    max_players_in_team = max(
        [card["max_team"] for card in game["cards_selected_by_leader"]]
    )
    # Check whether leader selected appropriate number of players
    if min_players_in_team <= len(data["selected_players"]) <= max_players_in_team:
        game["team_selected_by_leader"] = data["selected_players"]
        game['players_to_move'] = game["team_selected_by_leader"]
    else:
        # TODO
        raise

    store_room_game(data["room_id"], game)
    game = move_to_next_player(data["room_id"])

    emit("team_for_round_selected", {"game": game}, to=data["room_id"])


if __name__ == "__main__":
    # socketio.run(app)
    # build_deck("a")
    draw_random_card_from_deck("a")
