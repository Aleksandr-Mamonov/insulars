import json
import random
import uuid

from flask import Flask, url_for, redirect, request, render_template, session
from flask_socketio import SocketIO, emit, send, join_room, leave_room

from .config import (
    MIN_PLAYERS,
    MAX_PLAYERS,
    CARDS_ON_TABLE_IN_ROUND,
)
from .database import select_one_from_db, select_all_from_db, write_to_db
from .cards import generate_cards, CARD_FAMILIES

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

# flask --app app.main run --debug
# python -m app.main
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


def build_deck(game_id: str, players_number: int):
    card_families = dict(random.sample(list(CARD_FAMILIES.items()), players_number))
    cards = generate_cards(card_families, players_number)
    for card in cards:
        write_to_db(
            """INSERT INTO game_deck (game_id, card_family, card_tier, card_name, points_to_succeed, min_team, max_team, on_success, on_failure)
             VALUES (:game_id, :card_family, :card_tier, :card_name, :points_to_succeed, :min_team, :max_team, :on_success, :on_failure)""",
            {
                "game_id": game_id,
                "card_family": card["family"],
                "card_tier": card["tier"],
                "card_name": card["name"],
                "points_to_succeed": card["points_to_succeed"],
                "min_team": card["min_team"],
                "max_team": card["max_team"],
                "on_success": json.dumps(card["on_success"]),
                "on_failure": json.dumps(card["on_failure"]),
            },
        )


def draw_cards_for_round(game: dict) -> dict:
    """
    1) iterates over all succeeded cards and selects cards of next tiers from same families.
    i.e. if 2nd tier card of family 'Shopping' is succeeded in previous round,
    then it draws a 3rd tier card of 'Shopping' family and add it to cards list.
    2) adds all available 1st tier cards to cards list
    3) randomly chooses <CARDS_ON_TABLE_IN_ROUND> from cards list and update them as unavailable in game_deck
    4) returns chosen cards
    """
    game_id = game["game_id"]
    cards = []
    if game["history"]:
        families_max_tiers = {}
        for item in game["history"]:
            card_tier = int(item["card"]["card_tier"])
            card_family = item["card"]["card_family"]
            if item["succeeded"] == True and card_tier != 5:
                max_tier = families_max_tiers.get(card_family)
                if max_tier:
                    if card_tier > int(max_tier):
                        families_max_tiers[card_family] = str(card_tier)
                else:
                    families_max_tiers[card_family] = str(card_tier)
            elif card_tier == 5:
                families_max_tiers.pop(card_family)
                switch_card_availability_to(False, item["card"]["card_id"], game_id)

        succeeded_cards_with_next_tier_available = [
            item["card"]
            for item in game["history"]
            if item["card"]["card_family"] in families_max_tiers.keys()
            and item["card"]["card_tier"]
            == families_max_tiers[item["card"]["card_family"]]
            and item["card"]["card_tier"] != "5"
        ]
        if succeeded_cards_with_next_tier_available:
            for card in succeeded_cards_with_next_tier_available:
                family = card["card_family"]
                next_tier = int(card["card_tier"]) + 1
                next_tier_card = select_one_from_db(
                    """
                    SELECT 
                        gd.card_id,
                        gd.card_family,
                        gd.card_tier,
                        gd.card_name as name,
                        gd.points_to_succeed,
                        gd.min_team,
                        gd.max_team,
                        gd.on_success,
                        gd.on_failure
                    FROM game_deck AS gd 
                    WHERE gd.game_id=:game_id 
                    AND gd.card_family=:card_family 
                    AND gd.card_tier=:card_tier
                    """,
                    {
                        "game_id": game_id,
                        "card_family": family,
                        "card_tier": str(next_tier),
                    },
                )
                cards.append(next_tier_card)

    available_first_tier_cards = select_all_from_db(
        """
        SELECT 
            gd.card_id,
            gd.card_family,
            gd.card_tier,
            gd.card_name as name,
            gd.points_to_succeed,
            gd.min_team,
            gd.max_team,
            gd.on_success,
            gd.on_failure
        FROM game_deck AS gd 
        WHERE gd.game_id=:game_id 
        AND gd.available=TRUE
        AND gd.card_tier='1'
        """,
        {"game_id": game_id},
    )
    cards.extend(available_first_tier_cards)
    chosen_cards = random.sample(cards, CARDS_ON_TABLE_IN_ROUND)
    for card in chosen_cards:
        write_to_db(
            "UPDATE game_deck SET available=FALSE WHERE card_id=:card_id AND game_id=:game_id",
            {"card_id": card["card_id"], "game_id": game_id},
        )

    return chosen_cards


def switch_card_availability_to(available: bool, card_id, game_id):
    write_to_db(
        "UPDATE game_deck SET available=:available WHERE card_id=:card_id AND game_id=:game_id",
        {"card_id": card_id, "game_id": game_id, "available": available},
    )


def rotate_players_order_in_round(game: dict):
    """Rotate players order in round, set active_player and leader in round accordingly."""
    new_order = game["players_order_in_round"]

    # Rotate players order for next round
    new_order.append(new_order.pop(0))
    game["players_order_in_round"] = new_order
    game["players_to_move"] = new_order
    game["active_player"] = new_order[0]
    game["leader"] = new_order[0]

    return game


def cancel_effects(cancel_effect: dict, effects: list):
    """
    Args:
        cancel_effect: effect with name "cancel_effects"
        effects: list of all current effects in game
    """

    cancel_type = cancel_effect["payload"]["cancel"]
    if (
        cancel_effect["payload"]["categories_of_players"] == ["all"]
        and cancel_type == "all_effects"
    ):
        effects.clear()
        return effects

    effects.remove(cancel_effect)
    cancel_effects_for_players = cancel_effect["payload"]["players"]
    for eff in effects[:]:
        payload = eff["payload"]
        if cancel_type == "positive_effects":
            if eff["type"] == "positive":
                pass
            else:
                continue
        elif cancel_type == "negative_effects":
            if eff["type"] == "negative":
                pass
            else:
                continue
        else:  # cancel all effects
            pass
        payload["players"] = [
            player
            for player in payload["players"]
            if player not in cancel_effects_for_players
        ]
        if len(payload["players"]) == 0:
            effects.remove(eff)
        else:
            eff["payload"] = payload

    return effects


def apply_effects(game: dict, effects: list) -> dict:
    """Get game from db, apply effects, return game.
    Apply effects after round setup.
    """
    if len(effects) > 0 and effects[0]["name"] == "cancel_effects":
        effects = cancel_effects(cancel_effect=effects[0], effects=effects)

    expired_effects = []
    for i, effect in enumerate(effects):
        payload = effect["payload"]
        players = payload["players"]
        if effect["name"] == "change_player_points":
            for player in players:
                game = change_player_points(game, player, payload["points"])
            payload["rounds_to_apply"] -= 1
            if payload["rounds_to_apply"] <= 0:
                expired_effects.append(i)
        elif effect["name"] == "leadership_ban_next_time":
            if game["leader"] == players[0]:
                game = rotate_players_order_in_round(game)
                expired_effects.append(i)
        elif effect["name"] == "give_overpayment":
            overpayment = game["round_delta"]
            if overpayment > 0:
                points_to_each_player = overpayment // len(players)
                for player in players:
                    game = change_player_points(game, player, points_to_each_player)
            expired_effects.append(i)
        elif effect["name"] == "take_away_underpayment":
            underpayment = game["round_delta"]
            if underpayment < 0:
                points_from_each_player = underpayment // len(players)
                for player in players:
                    game = change_player_points(game, player, points_from_each_player)
            expired_effects.append(i)
        elif effect["name"] == "cards_selection_ban_next_time":
            # TODO
            pass
        elif effect["name"] == "team_selection_ban_next_time":
            # TODO
            pass

    effects = [
        item for item in effects if item not in [effects[i] for i in expired_effects]
    ]
    game["effects_to_apply"] = effects

    return game


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
    game_id = str(uuid.uuid4())
    players = select_all_from_db(
        "SELECT player_name FROM room_players WHERE room_id=:room_id",
        {"room_id": room_id},
    )
    player_names = [pl["player_name"] for pl in players]

    game = {
        "game_id": game_id,
        "round": 1,
        "players": tuple(player_names),
        "players_order_in_round": player_names,
        "players_to_move": player_names,
        "active_player": player_names[0],
        "leader": player_names[0],
        "all_players_points": {
            pln: int(data["initial_player_points"]) for pln in player_names
        },
        "round_common_account_points": 0,
        "cards_selected_by_leader": [],
        "team": [],
        "effects_to_apply": [],
        "rounds": int(data["rounds"]),
        "card_effect_visibility": data["card_effect_visibility"],
        "history": [],
    }
    build_deck(game_id=game_id, players_number=len(player_names))
    cards_on_table = draw_cards_for_round(game)
    game["cards_on_table"] = cards_on_table
    rm = select_one_from_db(
        "SELECT number_of_games FROM rooms WHERE uid=:room_id", {"room_id": room_id}
    )
    if rm["number_of_games"] > 0:
        for rotation in range(rm["number_of_games"] % len(player_names)):
            game = rotate_players_order_in_round(game)

    write_to_db(
        "UPDATE rooms SET game=:game WHERE uid=:room_id",
        {"game": json.dumps(game), "room_id": room_id},
    )

    emit("game_started", build_payload(room_id), to=data["room_id"])


def change_player_points(game: dict, player_name, points: int):
    game["all_players_points"][player_name] = max(
        game["all_players_points"][player_name] + points, 0
    )

    return game


def change_project_points(game: dict, points: int):
    game["round_common_account_points"] = game["round_common_account_points"] + points
    return game


@socketio.on("select_cards_from_table")
def handle_select_cards_from_table(data):
    """Card(s) can be selected only by leader in current round."""
    room_id = data["room_id"]
    game = get_game(room_id)
    for card in game["cards_on_table"]:
        card_id = card["card_id"]
        for selected_card_id in data["selected_cards_ids"]:
            if selected_card_id == card_id:
                game["cards_selected_by_leader"].append(card)
                break
        if card not in game["cards_selected_by_leader"]:
            write_to_db(
                "UPDATE game_deck SET available=TRUE WHERE card_id=:card_id AND game_id=:game_id",
                {"card_id": card["card_id"], "game_id": game["game_id"]},
            )
    game["cards_on_table"].clear()
    store_game(room_id, game)
    emit("cards_for_round_selected", build_payload(room_id), to=room_id)


def get_game(room_id):
    result = select_one_from_db(
        "SELECT game FROM rooms WHERE uid=:room_id", {"room_id": room_id}
    )

    return json.loads(result["game"]) if result["game"] else None


def store_game(room_id, game):
    write_to_db(
        "UPDATE rooms SET game=:game WHERE uid=:room_id",
        {"game": json.dumps(game), "room_id": room_id},
    )


def move_to_next_player(game: dict):
    """Change active player to next one"""
    game["players_to_move"].pop(0)
    if len(game["players_to_move"]) > 0:
        game["active_player"] = game["players_to_move"][0]
        return game, True
    else:
        return game, False


def populate_players_to_whom_apply_effect(game: dict, effect: dict):
    players_to_whom_apply = []
    for category in effect["payload"]["categories_of_players"]:
        if category == "all":
            players_to_whom_apply.extend(game["players"])
        elif category == "random_player":
            players_to_whom_apply.extend(random.choice(game["players"]))
        elif category == "others":
            others = [
                player
                for player in game["players"]
                if player not in game["team"] and player != game["leader"]
            ]
            players_to_whom_apply.extend(others)
        elif category == "leader":
            players_to_whom_apply.extend([game["leader"]])
        elif category == "team":
            players_to_whom_apply.extend(game["team"])
        else:
            raise RuntimeError("Unknown player category")

    effect["payload"]["players"].extend(players_to_whom_apply)
    return effect


def implement_project_result(game: dict):
    # Check whether team succeeded or failed in ended round
    points_to_succeed = sum(
        [int(card["points_to_succeed"]) for card in game["cards_selected_by_leader"]]
    )
    points_collected_by_team = game["round_common_account_points"]

    is_success = points_collected_by_team >= points_to_succeed
    game["round_delta"] = points_collected_by_team - points_to_succeed
    for card in game["cards_selected_by_leader"]:
        game["history"].append({"card": card, "succeeded": is_success})
        effects = json.loads(card["on_success" if is_success else "on_failure"])
        for effect in effects:
            if effect:
                effect = populate_players_to_whom_apply_effect(game, effect)
                if effect["name"] == "cancel_effects":
                    game["effects_to_apply"] = [effect] + game["effects_to_apply"]
                else:
                    game["effects_to_apply"].append(effect)

    return game, is_success


def start_next_round(game: dict):
    game["round"] += 1
    # That was last round, so game ended. Show game results.
    if game["round"] > game["rounds"]:
        return None, game
    else:
        players_order_in_new_round = game["players_order_in_round"]
        # Rotate players order for next round
        players_order_in_new_round.append(players_order_in_new_round.pop(0))
        game["round_common_account_points"] = 0
        if game["latest_round_result"] == False:
            for card in game["cards_selected_by_leader"]:
                write_to_db(
                    "UPDATE game_deck SET available=TRUE WHERE card_id=:card_id AND game_id=:game_id",
                    {"card_id": card["card_id"], "game_id": game["game_id"]},
                )
        new_cards_on_table = draw_cards_for_round(game)
        game["cards_on_table"] = new_cards_on_table
        game["cards_selected_by_leader"] = []
        game["team"] = []
        game["players_order_in_round"] = players_order_in_new_round
        game["players_to_move"] = players_order_in_new_round
        game["active_player"] = players_order_in_new_round[0]
        game["leader"] = players_order_in_new_round[0]
        return game["round"], game


@socketio.on("make_project_deposit")
def handle_make_project_deposit(data):
    """Player make a points deposit during project development"""
    room_id = data["room_id"]
    points = int(data["points"])
    game = get_game(room_id)
    game = change_player_points(game, data["player_name"], -points)
    game = change_project_points(game, points)

    game, has_player_to_move_next = move_to_next_player(game)
    store_game(room_id, game)

    payload = build_payload(room_id)
    emit("project_deposited", payload, to=room_id)
    emit("player_points_changed", payload, to=room_id)
    if has_player_to_move_next:
        emit("move_started", payload, to=room_id)
    else:
        game, is_success = implement_project_result(game)
        game["latest_round_result"] = is_success
        store_game(room_id, game)

        emit("round_result", build_payload(room_id), to=room_id)

        next_round_n, game = start_next_round(game)
        game = apply_effects(game, game["effects_to_apply"])

        if next_round_n is None:
            write_to_db(
                "UPDATE rooms SET game=NULL, number_of_games=number_of_games+1 WHERE uid=:room_id",
                {"room_id": room_id},
            )

            rating = define_rating(game)
            payload = build_payload(room_id)
            payload["rating"] = rating
            emit("game_ended", payload, to=room_id)
        else:
            store_game(room_id, game)
            emit("round_started", build_payload(room_id), to=room_id)


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
    room_id = data["room_id"]
    game = get_game(room_id)

    # Check whether card(s) for a given round were selected already or not
    if game["cards_selected_by_leader"] == []:
        # TODO
        raise

    # How many min and max players should be in a team
    min_players_in_team = min(
        [int(card["min_team"]) for card in game["cards_selected_by_leader"]]
    )
    max_players_in_team = max(
        [int(card["max_team"]) for card in game["cards_selected_by_leader"]]
    )

    # Check whether leader selected appropriate number of players
    if min_players_in_team <= len(data["selected_players"]) <= max_players_in_team:
        game["team"] = data["selected_players"]
        game["players_to_move"] = [""] + game["team"]
    else:
        # TODO
        raise

    game, _ = move_to_next_player(game)
    store_game(room_id, game)

    emit("team_for_round_selected", build_payload(room_id), to=room_id)


@socketio.on("select_player_portrait")
def handle_portrait_select(data):
    """Portrait is selected by a player.
    Data = {
    "player_name": player_name,
    "room_id": room_id,
    "portrait_id": portrait_id,
    }
    """
    room_id = data["room_id"]

    sql = "UPDATE room_players SET portrait_id=:portrait_id WHERE room_id=:room_id AND player_name=:player_name"
    write_to_db(
        sql,
        {
            "room_id": room_id,
            "portrait_id": data["portrait_id"],
            "player_name": data["player_name"],
        },
    )

    emit("player_portrait_selected", build_payload(room_id), to=room_id)


def define_rating(game: dict):
    """Returns rating of all players in the game and winner(s).
    If multiple players have the same max number of points, they all are winners.
    """

    all_players_points = game["all_players_points"]
    rating = sorted(all_players_points.items(), key=lambda item: int(item[1]))[::-1]

    return rating


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
