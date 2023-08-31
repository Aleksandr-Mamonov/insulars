game_id = "jksjfdfjgfjklsdjflaskjdfldhfjsdh"
players = [1, 2, 3]
all_players_points = {i["player_name"]: 10 for i in players}
cards_on_table = ["card1", "card2", "card3"]

game = {
    "game_id": game_id,
    "players": tuple(players),
    "all_players_points": all_players_points,
    "active_round": {
        "round": 1,
        "players_order_in_round": players,
        "players_to_move": players,
        "active_player": players[0],
        "leader": players[0],
        "common_points_in_round": 0,
        "cards_on_table": cards_on_table,
        "cards_selected_by_leader": [],
        "team_selected_by_leader": [],
    },
    # for example 1st and 2nd player gets 5 points next 3 rounds - pop from list
    "future_effects_on_players_to_apply": {
        1: {
            "add_each_next_round": [5, 5, 5],
            "can_be_leader_next_round": True,
            "can_select_team_as_leader": True,
            "can_select_cards_as_leader": True,
        },
        2: {
            "add_each_next_round": [5, 5, 5],
            "can_be_leader_next_round": True,
            "can_select_team_as_leader": True,
            "can_select_cards_as_leader": True,
        },
        3: {
            "add_each_next_round": [-5, -5],
            "can_be_leader_next_round": False,
            "can_select_team_as_leader": True,
            "can_select_cards_as_leader": True,
        },
    },
    "round_history": {},  # TODO: Do we need to store sth about rounds that ended?
}

"""
There are 2 types of results that we apply after round ended: immediate and future.
Immediate: for example, add 10 points to each player on_success.
Future: for example, add 5 points each round in next 3 rounds.
Initial conditions for all players:
    "add_each_next_round": [],
    "can_be_leader_next_round": True,
    "can_select_team_as_leader": True,
    "can_select_cards_as_leader": True,

After 1st round those conditions for each player changed.
And at the beginning of each new round (starting from round #2) we apply conditions accordingly 
to this "future_effects_on_players_to_apply" object.

"""

effects = {
    "apply_to_player": None,  # default None, otherwise player_name
    "apply_to_all": True,
    "add_each_next_round": [],
    "can_be_leader_next_round": True,
    "can_select_team_as_leader": True,
    "can_select_cards_as_leader": True,
}


def apply_effects(game: dict, effects: dict) -> dict:
    """Get game from db, apply effects"""
    return game
