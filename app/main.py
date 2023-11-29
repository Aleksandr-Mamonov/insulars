import json
import random
import uuid

from flask import Flask, url_for, redirect, request, render_template, session
from flask_socketio import SocketIO, emit, send, join_room, leave_room

from .config import MIN_PLAYERS, MAX_PLAYERS
from .database import select_one_from_db, select_all_from_db, write_to_db
from .cards import build_deck, default_houses
from .money import purse, coin, compare_purses, sum_purses, sub_purses

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


# flask --app app.main run --debug
# python -m app.main
# app.secret_key = "7f7c27265646902d9775e9fa1369fbf200cde69c"


def _join_player_to_room(player_name, room_id):
    # TODO: validate player_name and room_id
    room = select_one_from_db("SELECT uid FROM rooms WHERE uid=:room_id", {"room_id": room_id})
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


def _draw_cards(game_id):
    sql = f"""
        SELECT gd2.* FROM game_deck gd2
        INNER JOIN (
            SELECT gd1.family, MIN(gd1.tier) as tier FROM game_deck gd1
            WHERE gd1.is_available=TRUE AND gd1.game_id=:game_id
            GROUP BY 1
        ) as min_tier ON min_tier.tier = gd2.tier AND min_tier.family=gd2.family
        WHERE gd2.game_id = :game_id 
        ORDER BY RANDOM()
        LIMIT 3"""

    cards = select_all_from_db(sql, {"game_id": game_id})

    return [json.loads(card.get("card")) for card in cards]


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

    emit("room_entered", build_payload(room_id), to=room_id)


@socketio.on("start_game")
def handle_game_start(data):
    room_id = data["room_id"]

    players = select_all_from_db("SELECT player_name FROM room_players WHERE room_id=:room_id", {"room_id": room_id})

    player_names = [pl["player_name"] for pl in players]
    leader = random.choice(player_names)

    game = {
        "game_id": str(uuid.uuid4()),
        "round": 0,
        "players": {pl["player_name"]: {'name': pl["player_name"], "purse": purse(coin(5))} for pl in players},
        "players_order": player_names,
        "leader": leader,
        "rounds": int(data["rounds"]),
        "houses": [],
        "round_cards_draw": [],
        'active_player': leader,
        'selected_house': None,
        'job_assignment': {}
    }

    # выбрать N дефолтных строений по количеству игроков
    # чтобы обеспечить стартовые работы
    for house in default_houses(len(players)):
        game['houses'].append(house)

    cards = build_deck()
    _store_deck(cards, game['game_id'])

    game = _pre_round(game, 1)

    store_game(room_id, game)

    emit("game_started", build_payload(room_id), to=data["room_id"])


def _store_deck(cards, game_id):
    for card in cards:
        write_to_db(
            """INSERT INTO game_deck (game_id, name, card_type, family, tier, is_available, card)
               VALUES (:game_id, :name, :card_type, :family, :tier, :is_available, :card)""",
            {
                "game_id": game_id,
                "name": card["name"],
                "card_type": card["card_type"],
                "family": card["family"],
                "tier": card["tier"],
                "is_available": True,
                "card": json.dumps(card),
            },
        )


@socketio.on("select_house_card")
def handle_select_house_card(data):
    """Card can be selected only by leader in current round."""
    room_id = data["room_id"]
    game = get_game(room_id)

    for card in game["round_cards_draw"]:
        if card["name"] == data["selected_card_name"]:
            game["selected_house"] = card
            break

    game = _next_player(game)

    store_game(room_id, game)
    emit("house_card_selected", build_payload(room_id), to=room_id)


@socketio.on("select_job")
def handle_select_job(data):
    room_id = data["room_id"]

    game = get_game(room_id)
    game['job_assignment'][data['selected_job']] = data['player_name']
    game = _next_player(game)
    store_game(room_id, game)

    emit("job_selected", build_payload(room_id), to=room_id)

    if len(game['job_assignment']) == len(game['players']):
        game = _post_round(game)
        if game['round'] == game['rounds']:
            # todo rating
            emit('game_over', build_payload(room_id), to=room_id)
        else:
            game = _pre_round(game, game['round'] + 1)
            store_game(room_id, game)

            emit("round_done", build_payload(room_id), to=room_id)


def _post_round(game):
    for house in game['houses']:
        for job in house['jobs']:
            game, _ = _process_job_deal(game, job)

    house_card = game['selected_house']
    game, is_house_built = _process_card(game, house_card)
    if is_house_built:
        game['houses'].append(house_card)
        # todo deactivate card

    return game


def _pre_round(game, round_n):
    game['round'] = round_n
    game["round_cards_draw"] = _draw_cards(game["game_id"])
    game['leader'] = _player_next_to(game, game['leader'])
    game['active_player'] = game['leader']
    game['selected_house'] = None
    game['job_assignment'].clear()

    return game


def _process_card(game, card):
    built = True
    for job in card['project_jobs']:
        game, is_job_done = _process_job_deal(game, job)
        built = built and is_job_done

    return game, built


def _process_job_deal(game, job):
    assignee = game['job_assignment'].get(job['name'])
    if not assignee:
        return game, False

    assignee_purse = game['players'][assignee]['purse']

    # not enough money
    if compare_purses(assignee_purse, job['deal'][0]) < 0:
        return game, False

    # take price
    assignee_purse = sub_purses(assignee_purse, job['deal'][0])

    # give reward
    assignee_purse = sum_purses(assignee_purse, job['deal'][1])

    game['players'][assignee]['purse'] = assignee_purse

    return game, True


def get_game(room_id):
    result = select_one_from_db("SELECT game FROM rooms WHERE uid=:room_id", {"room_id": room_id})

    return json.loads(result["game"]) if result["game"] else None


def store_game(room_id, game):
    write_to_db("UPDATE rooms SET game=:game WHERE uid=:room_id", {"game": json.dumps(game), "room_id": room_id})


def rm_card_from_deck(game_id, name):
    write_to_db("UPDATE game_deck SET available=:available WHERE name=:name AND game_id=:game_id", {
        "name": name,
        "game_id": game_id,
        "available": False,
    })


def _next_player(game):
    game['active_player'] = _player_next_to(game, game['active_player'])
    return game


def _player_next_to(game, player_name):
    current_active_player = game['players_order'].index(player_name)

    next_player_idx = current_active_player + 1

    if next_player_idx >= len(game['players_order']):
        next_player_idx = 0

    return game['players_order'][next_player_idx]


@socketio.on("make_project_deposit")
def handle_make_project_deposit(data):
    """Player make a points deposit during project development"""
    room_id = data["room_id"]
    game = get_game(room_id)


@socketio.on("select_player_portrait")
def handle_portrait_select(data):
    """Portrait is selected by a player"""
    room_id = data["room_id"]

    write_to_db("UPDATE room_players SET portrait_id=:portrait_id WHERE room_id=:room_id AND player_name=:player_name",
                {"room_id": room_id, "portrait_id": data["portrait_id"], "player_name": data["player_name"]})

    emit("player_portrait_selected", build_payload(room_id), to=room_id)


def build_payload(room_id):
    sql_fetch_players = """
    SELECT
        rp.player_name as name, 
        rp.portrait_id,
        r.owner=rp.player_name AS is_owner
    FROM room_players AS rp
    INNER JOIN rooms AS r ON r.uid=rp.room_id
    WHERE rp.room_id=:room_id"""

    players = select_all_from_db(sql_fetch_players, {"room_id": room_id})

    game = get_game(room_id)

    return {
        "players": players,
        "config": {"MIN_PLAYERS": MIN_PLAYERS, "MAX_PLAYERS": MAX_PLAYERS},
        "game": game,
    }


if __name__ == "__main__":
    socketio.run(app)
