"""Each player (or some of them) has a role(mission) for a game. 
No one else knows about this role, except player himself.
Roles:
- провалить n строек за игру как член команды
- построить n строек за игру как член команды
0) проверяем счетчик
1) был ли в этом раунде в команде?
2) если да, то был ли успех/провал?
3) если да, счетчик+

- провалить n строек за игру как лидер
- построить n строек за игру как лидер

- вложи n монет за раз как член команды > получишь 2n через m раундов
1) был ли в этом раунде в команде?
2) если да, вложил ли n монет?

- честный мэр - ни разу не получить переплату как мэр
1) был ли в этом раунде мэром?
2) если да, получил ли переплату?

- продержаться на одной должности n раундов
1) имеет ли должность?
2) если да, то сколько раундов уже он на ней сидит?

- за игру д.б. построено хотя бы одно здание 5 tier
1) построено ли здание 5 tier?

- за игру д.б. построены здания не выше n tier
1) построено ли здание n+1 tier?

- во время игры перейди отметку в n очков > получишь +m очков
1) player_points больше, чем нужное кол-во?
"""
import random

from .config import ROUNDS, INITIAL_PLAYER_POINTS
from .database import select_one_from_db
from .game import change_player_points


MISSIONS = [
    {
        "name": "fail_as_team_n_rounds",
        "player": None,
        "counter": 0,
        "rounds": 2,
        "reward": INITIAL_PLAYER_POINTS,
        "is_failed": False,
        "is_complete": False,
    },
    {
        "name": "succeed_as_team_n_rounds",
        "player": None,
        "counter": 0,
        "rounds": 2,
        "reward": INITIAL_PLAYER_POINTS,
        "is_failed": False,
        "is_complete": False,
    },
    {
        "name": "fail_as_leader_n_rounds",
        "player": None,
        "counter": 0,
        "rounds": 2,
        "reward": INITIAL_PLAYER_POINTS,
        "is_failed": False,
        "is_complete": False,
    },
    {
        "name": "succeed_as_leader_n_rounds",
        "player": None,
        "counter": 0,
        "rounds": 2,
        "reward": INITIAL_PLAYER_POINTS,
        "is_failed": False,
        "is_complete": False,
    },
    {
        "name": "deposit_n_points_at_once",
        "player": None,
        "deposit": 2 * INITIAL_PLAYER_POINTS,
        "reward": 4 * INITIAL_PLAYER_POINTS,
        "is_failed": False,
        "is_complete": False,
    },
    {
        "name": "leader_without_overpayment",
        "player": None,
        "reward": 2 * INITIAL_PLAYER_POINTS,
        "is_failed": False,
        "is_complete": False,
    },
    {
        "name": "suceeded_n_tier",
        "player": None,
        "tier": 5,
        "reward": 3 * INITIAL_PLAYER_POINTS,
        "is_failed": False,
        "is_complete": False,
    },
    {
        "name": "lower_than_n_tier",
        "player": None,
        "tier": 3,
        "reward": 3 * INITIAL_PLAYER_POINTS,
        "is_failed": False,
        "is_complete": False,
    },
    {
        "name": "earn_n_points",
        "player": None,
        "earn": 3 * INITIAL_PLAYER_POINTS,
        "reward": 2 * INITIAL_PLAYER_POINTS,
        "is_failed": False,
        "is_complete": False,
    },
]


def assign_missions(game: dict):
    game["missions"] = random.sample(MISSIONS, len(game["players"]))
    for i, player in enumerate(game["players"]):
        game["missions"][i]["player"] = player
    return game


def complete_mission(game: dict, mission: dict):
    game = change_player_points(game, mission["player"], mission["reward"])
    mission["is_complete"] = True


def update_counter_and_check_mission_completion(game: dict, mission: dict):
    mission["counter"] += 1
    if mission["counter"] == mission["rounds"]:
        complete_mission(game, mission)


def process_missions(game: dict, is_round_successful: bool):
    for mission in game["missions"]:
        if mission["is_complete"] or mission["is_failed"]:
            continue

        player = mission["player"]

        match mission["name"]:
            case "fail_as_team_n_rounds":
                if not is_round_successful and player in game["team"]:
                    update_counter_and_check_mission_completion(game, mission)

            case "succeed_as_team_n_rounds":
                if is_round_successful and player in game["team"]:
                    update_counter_and_check_mission_completion(game, mission)

            case "fail_as_leader_n_rounds":
                if not is_round_successful and player == game["leader"]:
                    update_counter_and_check_mission_completion(game, mission)

            case "succeed_as_leader_n_rounds":
                if is_round_successful and player == game["leader"]:
                    update_counter_and_check_mission_completion(game, mission)

            case "deposit_n_points_at_once":
                if player in game["team"]:
                    if game["round_deposits"][player] >= mission["deposit"]:
                        complete_mission(game, mission)

            case "leader_without_overpayment":
                if player == game["leader"] and game["round_delta"] > 0:
                    mission["is_failed"] = True
                    continue
                if game["round"] == game["rounds"]:
                    complete_mission(game, mission)

            case "suceeded_n_tier":
                result = select_one_from_db(
                    """
                    SELECT * FROM game_deck
                    WHERE game_id=:game_id
                    AND tier=:tier
                    AND available=false
                    """,
                    {"game_id": game["game_id"], "tier": mission["tier"]},
                )
                if result:
                    complete_mission(game, mission)

            case "lower_than_n_tier":
                result = select_one_from_db(
                    """
                    SELECT * FROM game_deck
                    WHERE game_id=:game_id
                    AND tier>=:tier
                    AND available=false
                    """,
                    {"game_id": game["game_id"], "tier": mission["tier"]},
                )
                if result:
                    mission["is_failed"] = True
                    continue
                if game["round"] == game["rounds"]:
                    complete_mission(game, mission)

            case "earn_n_points":
                if game["all_players_points"][player] >= mission["earn"]:
                    complete_mission(game, mission)

    return game
