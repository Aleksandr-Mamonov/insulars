import sqlite3


def init_db():
    con = sqlite3.connect("insulars.db")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS rooms(uid, owner, game, number_of_games INTEGER DEFAULT 0)"
    )
    cur.execute("CREATE TABLE IF NOT EXISTS room_players(room_id, player_name)")
    cur.execute(
        """CREATE TABLE IF NOT EXISTS cards (
        name UNIQUE,
        points_to_succeed,
        min_team,
        max_team,
        on_success,
        on_failure
    )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS game_deck (
        game_id,
        card_id INTEGER PRIMARY KEY,
        card_name,
        points_to_succeed,
        min_team,
        max_team,
        on_success,
        on_failure,
        available BOOLEAN DEFAULT TRUE
    )"""
    )
    # on_success/on_failure['payload']['categories_of_players'] = ['all', 'leader', 'team', 'others', 'random_player']
    cur.execute(
        """INSERT INTO cards VALUES
        ('Station', 20, 1, 2, '{"name": "change_player_points", "type": "positive", "payload": {"rounds_to_apply": 1, "categories_of_players": ["leader", "team"], "points": 10, "players": []}}', '{"name": "change_player_points", "type": "negative", "payload": {"rounds_to_apply": 2, "categories_of_players": ["leader", "team"], "points": -5, "players": []}}')
    """
    )
    con.commit()


if __name__ == "__main__":
    init_db()

effects = [
    {
        "name": "change_player_points",
        "type": "positive",
        "payload": {
            "categories_of_players": ["leader", "team"],
            "players": [],
            "rounds_to_apply": 1,
            "points": 10,
        },
    },
    {
        "name": "leadership_ban_next_time",
        "type": "negative",
        "payload": {
            "categories_of_players": ["leader"],
            "players": [],
        },
    },
    {
        "name": "cancel_effects",
        "payload": {
            "categories_of_players": ["all"],
            "players": [],
            "cancel": "all_effects",  # ['all_effects','positive_effects','negative_effects']
        },
    },
    {
        "name": "give_overpayment",
        "type": "positive",
        "payload": {
            "categories_of_players": ["leader"],
            "players": [],
        },
    },
    {
        "name": "take_away_underpayment",
        "type": "negative",
        "payload": {
            "categories_of_players": ["leader"],
            "players": [],
        },
    },
]
