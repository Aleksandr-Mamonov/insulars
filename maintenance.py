import sqlite3


def init_db():
    con = sqlite3.connect("insulars.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS rooms(uid, owner, game)")
    cur.execute("CREATE TABLE IF NOT EXISTS room_players(room_id, player_name, sid)")


if __name__ == "__main__":
    init_db()
