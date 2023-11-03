import sqlite3


def init_db():
    con = sqlite3.connect("insulars.db")

    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS rooms (uid, owner, game, number_of_games INTEGER DEFAULT 0)")
    cur.execute("CREATE TABLE IF NOT EXISTS room_players (room_id, player_name, portrait_id)")

    cur.execute("""CREATE TABLE IF NOT EXISTS game_deck (
        game_id,
        card_id, 
        family,
        tier,
        name,
        points_to_succeed,
        min_team,
        max_team,
        on_success,
        on_failure,
        available BOOLEAN DEFAULT TRUE,
        feature,
        vacancy)""")

if __name__ == "__main__":
    init_db()
