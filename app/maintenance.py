import sqlite3


def init_db():
    con = sqlite3.connect("insulars.db")

    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS rooms (uid, owner, game INTEGER DEFAULT 0)")
    cur.execute("CREATE TABLE IF NOT EXISTS room_players (room_id, player_name, portrait_id)")

    cur.execute("""CREATE TABLE IF NOT EXISTS game_deck (
        game_id,
        name, 
        card_type,
        family,
        tier,
        is_available BOOLEAN DEFAULT TRUE,
        card)""")


if __name__ == "__main__":
    init_db()
