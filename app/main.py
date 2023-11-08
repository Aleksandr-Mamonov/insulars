import json
import random
import uuid

from flask import Flask, url_for, redirect, request, render_template, session
from flask_socketio import SocketIO, emit, send, join_room, leave_room

from .config import (
    MIN_PLAYERS,
    MAX_PLAYERS,
    CARDS_ON_TABLE_IN_ROUND,
    STARTING_BASIC_INCOME,
)
from .database import select_one_from_db, select_all_from_db, write_to_db
from .cards import build_deck
from .game import change_player_points
from .missions import assign_missions, process_missions

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


def draw_cards(game_id):
    return select_all_from_db(
        f"""
        SELECT gd2.* FROM game_deck gd2
        INNER JOIN (
            SELECT gd1.family, MIN(gd1.tier) as tier FROM game_deck gd1
            WHERE gd1.available=TRUE AND gd1.game_id=:game_id
            GROUP BY 1
        ) as min_tier ON min_tier.tier = gd2.tier AND min_tier.family=gd2.family
        WHERE gd2.game_id = :game_id 
        ORDER BY RANDOM()
        LIMIT {CARDS_ON_TABLE_IN_ROUND}
    """,
        {"game_id": game_id},
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
        # elif effect["name"] == "leadership_ban_next_time":
        #     if game["leader"] == players[0]:
        #         game = rotate_players_order_in_round(game)
        #         expired_effects.append(i)
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

    players = select_all_from_db(
        "SELECT player_name FROM room_players WHERE room_id=:room_id",
        {"room_id": room_id},
    )
    player_names = [pl["player_name"] for pl in players]

    game = {
        "game_id": str(uuid.uuid4()),
        "round": 1,
        "players": tuple(player_names),
        "vacancies": {},
        "players_order_in_round": player_names,
        "players_to_move": player_names,
        "active_player": player_names[0],
        "leader": player_names[0],
        "all_players_points": {
            pln: int(data["initial_player_points"]) for pln in player_names
        },
        "round_deposits": {},
        "cards_selected_by_leader": [],
        "team": [],
        "effects_to_apply": [],
        "rounds": int(data["rounds"]),
        "card_effect_visibility": data["card_effect_visibility"],
        "history": [],
        "incomes": {"basic_income_for_all": 0, "basic_income_for_random_player": 0},
    }
    game = assign_missions(game)
    cards = build_deck(len(player_names) + 1)
    for card in cards:
        write_to_db(
            """INSERT INTO game_deck (
                game_id, card_id, family, tier, name, points_to_succeed, min_team, max_team, on_success, on_failure, feature, vacancy
            )
            VALUES (
                :game_id, :card_id, :family, :tier, :name, :points_to_succeed, :min_team, :max_team, :on_success, :on_failure, :feature, :vacancy
            )""",
            {
                "game_id": game["game_id"],
                "card_id": card["name"],
                "family": card["family"],
                "tier": card["tier"],
                "name": card["name"],
                "points_to_succeed": card["points_to_succeed"],
                "min_team": card["min_team"],
                "max_team": card["max_team"],
                "on_success": json.dumps(card["on_success"]),
                "on_failure": json.dumps(card["on_failure"]),
                "feature": json.dumps(card.get("feature")),
                "vacancy": json.dumps(card["vacancy"]),
            },
        )

    game["cards_on_table"] = draw_cards(game["game_id"])

    rm = select_one_from_db(
        "SELECT number_of_games FROM rooms WHERE uid=:room_id", {"room_id": room_id}
    )
    if rm["number_of_games"] > 0:
        for rotation in range(rm["number_of_games"] % len(player_names)):
            game = rotate_players_order_in_round(game)

    store_game(room_id, game)

    emit("game_started", build_payload(room_id), to=data["room_id"])


@socketio.on("select_cards_from_table")
def handle_select_cards_from_table(data):
    """Card(s) can be selected only by leader in current round."""
    room_id = data["room_id"]
    game = get_game(room_id)

    for card in game["cards_on_table"]:
        if card["card_id"] == data["selected_card_id"]:
            game["cards_selected_by_leader"].append(card)
            break

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


def activate_card_feature(card: dict, game: dict):
    game_id = game["game_id"]
    basic_for_all = game["incomes"]["basic_income_for_all"]
    basic_for_random = game["incomes"]["basic_income_for_random_player"]
    feat = json.loads(card["feature"])
    if feat:
        feature = feat["name"]
        multiple = feat["multiple"]
        if feature in ["decrease_cards_costs", "increase_cards_costs"]:
            # change points to succeed for all cards
            write_to_db(
                """
                UPDATE game_deck 
                SET points_to_succeed=ROUND(:multiple * points_to_succeed)
                WHERE game_id=:game_id""",
                {
                    "game_id": game_id,
                    "multiple": multiple,
                },
            )
        elif feature in ["decrease_cards_rewards", "increase_cards_rewards"]:
            # change rewards on success for all availablecards
            all_cards = select_all_from_db(
                """
                SELECT card_id, on_success 
                FROM game_deck
                WHERE game_id=:game_id
                """,
                {
                    "game_id": game_id,
                },
            )
            for c in all_cards:
                c["on_success"] = json.loads(c["on_success"])
                for effect in c["on_success"]:
                    if effect["name"] == "change_player_points":
                        effect["payload"]["points"] = round(
                            effect["payload"]["points"] * multiple
                        )
                write_to_db(
                    """
                UPDATE game_deck 
                SET on_success=:on_success
                WHERE card_id=:card_id
                AND game_id=:game_id
                """,
                    {
                        "on_success": json.dumps(c["on_success"]),
                        "card_id": c["card_id"],
                        "game_id": game_id,
                    },
                )
        elif feature in ["increase_clerks_pay", "decrease_clerks_pay"]:
            # TODO
            pass

        elif feature == "increase_basic_income_for_all":
            if card["tier"] == 1:
                basic_for_all = round(STARTING_BASIC_INCOME * multiple)
            else:
                basic_for_all = round(basic_for_all * multiple)
        elif feature == "decrease_basic_income_for_all":
            if basic_for_all > 0:
                basic_for_all = round(basic_for_all * multiple)

        elif feature == "increase_basic_income_for_random_player":
            if card["tier"] == 1:
                basic_for_random = round(STARTING_BASIC_INCOME * multiple)
            else:
                basic_for_random = round(basic_for_random * multiple)
        elif feature == "decrease_basic_income_for_random_player":
            if basic_for_random > 0:
                basic_for_random = round(basic_for_random * multiple)

        game["incomes"]["basic_income_for_all"] = basic_for_all
        game["incomes"]["basic_income_for_random_player"] = basic_for_random
    return game


def implement_project_result(game: dict):
    """Check whether team succeeded or failed in ended round"""
    card = game["cards_selected_by_leader"][0]
    overpayment = sum(game["round_deposits"].values()) - int(card["points_to_succeed"])

    is_success = overpayment >= 0

    game["round_delta"] = overpayment
    game["latest_round_result"] = is_success
    game["history"].append({"card": card, "succeeded": is_success})
    if is_success:
        game = activate_card_feature(card, game)
    effects = json.loads(card["on_success" if is_success else "on_failure"])
    for effect in effects:
        if effect:
            effect = populate_players_to_whom_apply_effect(game, effect)
            if effect["name"] == "cancel_effects":
                game["effects_to_apply"] = [effect] + game["effects_to_apply"]
            else:
                game["effects_to_apply"].append(effect)

    if is_success and card["vacancy"] != "null":
        vacancy = json.loads(card["vacancy"])
        if vacancy:
            deposits = game["round_deposits"]
            max_dep = max(deposits.values())
            max_dep_players = [pl for pl in deposits if deposits[pl] == max_dep]
            game["vacancies"][vacancy["name"]] = (
                max_dep_players[0] if len(max_dep_players) == 1 else game["leader"]
            )

    if is_success:
        write_to_db(
            "UPDATE game_deck SET available=:available WHERE card_id=:card_id AND game_id=:game_id",
            {
                "card_id": card["card_id"],
                "game_id": game["game_id"],
                "available": False,
            },
        )

    return game, is_success


def pay_incomes(game: dict):
    basic_income = game["incomes"]["basic_income_for_all"]
    if basic_income != 0:
        for player in game["players"]:
            game = change_player_points(game, player, basic_income)

    basic_income_for_random = game["incomes"]["basic_income_for_random_player"]
    if basic_income_for_random != 0:
        game = change_player_points(
            game, random.choice(game["players"]), basic_income_for_random
        )
    return game


def issue_salaries(game):
    vacancies = [card["vacancy"] for card in build_deck(999) if card["vacancy"]]
    salaries = {vcn["name"]: vcn["income"] for vcn in vacancies}

    for vcn in game["vacancies"]:
        game = change_player_points(game, game["vacancies"][vcn], int(salaries[vcn]))

    return game


@socketio.on("make_project_deposit")
def handle_make_project_deposit(data):
    """Player make a points deposit during project development"""
    room_id = data["room_id"]
    points = int(data["points"])

    game = get_game(room_id)
    game = change_player_points(game, data["player_name"], -points)
    game["round_deposits"][data["player_name"]] = points

    game, has_player_to_move_next = move_to_next_player(game)
    store_game(room_id, game)

    payload = build_payload(room_id)
    emit("project_deposited", payload, to=room_id)
    emit("player_points_changed", payload, to=room_id)

    if has_player_to_move_next:
        emit("move_started", payload, to=room_id)
    else:
        game, is_success = implement_project_result(game)
        game = issue_salaries(game)
        game = apply_effects(game, game["effects_to_apply"])
        game = pay_incomes(game)
        game = process_missions(game, is_round_successful=is_success)

        store_game(room_id, game)

        emit("round_result", build_payload(room_id), to=room_id)

        is_game_over = game["round"] >= game["rounds"]
        if is_game_over:
            write_to_db(
                "UPDATE rooms SET game=NULL, number_of_games=number_of_games+1 WHERE uid=:room_id",
                {"room_id": room_id},
            )

            payload = build_payload(room_id)
            payload["rating"] = define_rating(game)

            emit("game_ended", payload, to=room_id)
        else:
            # start next round
            game["round"] += 1
            game["round_deposits"] = {}
            game["cards_on_table"] = draw_cards(game["game_id"])
            game["cards_selected_by_leader"] = []
            game["team"] = []

            # Rotate players order for next round
            players_order_in_new_round = game["players_order_in_round"]
            players_order_in_new_round.append(players_order_in_new_round.pop(0))

            game["players_order_in_round"] = players_order_in_new_round
            game["players_to_move"] = players_order_in_new_round
            game["active_player"] = players_order_in_new_round[0]
            game["leader"] = players_order_in_new_round[0]

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
