def change_player_points(game: dict, player_name, points: int):
    game["all_players_points"][player_name] = max(
        game["all_players_points"][player_name] + points, 0
    )
    return game
