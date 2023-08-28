import sqlite3


def init_db():
    con = sqlite3.connect("insulars.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS rooms(uid, owner, game)")
    cur.execute("CREATE TABLE IF NOT EXISTS room_players(room_id, player_name, sid)")
    cur.execute(
        """CREATE TABLE IF NOT EXISTS cards (
    name UNIQUE, 
    points_to_succeed, 
    min_team, 
    max_team, 
    on_success, 
    on_failure)"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS game_deck (
    game_id, 
    card_id INTEGER PRIMARY KEY,
    card_name,
    available BOOLEAN DEFAULT TRUE)"""
    )
    cur.execute(
        """INSERT INTO cards VALUES
        ('School', 35, 1, 2, '{"condition_on_success": "some_condition"}', '{"condition_on_failure": "some_condition"}'),
        ('Station', 50, 1, 2, '{"condition_on_success": "some_condition"}', '{"condition_on_failure": "some_condition"}'),
        ('Bridge', 30, 2, 2, '{"condition_on_success": "some_condition"}', '{"condition_on_failure": "some_condition"}'),
        ('Hospital', 40, 1, 2, '{"condition_on_success": "some_condition"}', '{"condition_on_failure": "some_condition"}')
        """
    )
    con.commit()


if __name__ == "__main__":
    init_db()
