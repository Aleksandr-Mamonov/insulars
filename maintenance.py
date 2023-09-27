import sqlite3


def init_db():
    con = sqlite3.connect("insulars.db")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS rooms(uid, owner, game, number_of_games INTEGER DEFAULT 0)"
    )
    cur.execute("CREATE TABLE IF NOT EXISTS room_players(room_id, player_name, sid)")
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

    cur.execute(
        """INSERT INTO cards VALUES
        ('Station', 20, 1, 2, '{"type": "change_player_points", "payload": {"rounds_to_apply": 1, "points": 10, "players": []}}', '{"type": "change_player_points", "payload": {"rounds_to_apply": 1, "points": -5, "players": []}}')
    """
    )
    con.commit()


if __name__ == "__main__":
    init_db()
