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


def apply_effects(game: dict, effects: list) -> dict:
    """Get game from db, apply effects, return game.
    Apply effects after round setup.
    """
    for i, effect in enumerate(effects):
        payload = effect["payload"]
        if effect["type"] == "change_player_points":
            if payload["rounds_to_apply"] > 0:
                for player in payload["players"]:
                    game["all_players_points"][player] = (
                        game["all_players_points"][player] + payload["points"]
                    )
                effect["payload"]["rounds_to_apply"] -= 1
            else:
                effects.pop(i)
        elif effect["type"] == "leadership_ban_next_time":
            if game["leader"] == payload["player"]:
                game = rotate_players_order_in_round(game)
                effects.pop(i)
        elif effect["type"] == "cards_selection_ban_next_time":
            # TODO
            pass
        elif effect["type"] == "team_selection_ban_next_time":
            # TODO
            pass

    game["effects_to_apply"] = effects
    return game
