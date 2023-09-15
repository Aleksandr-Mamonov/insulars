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
    # cur.execute(
    #     """INSERT INTO cards VALUES
    #     ('School', 15, 1, 2, '''
    #                 {
    #         "type": "change_player_points",
    #         "payload": {
    #             "rounds_to_apply": 3,
    #             "points": 5,
    #             "players": []
    #         }
    #         }
    #         ''',
    #         '''
    #         {
    #         "type": "change_player_points",
    #         "payload": {
    #             "rounds_to_apply": 3,
    #             "points": -5,
    #             "players": []
    #         }
    #         }
    #         '''),
    #     ('Station', 20, 1, 2, '''{"type": "change_player_points", "payload": {"rounds_to_apply": 1, "points": 10,"players": []}}''', ''),
    #     ('Bridge', 20, 2, 2, '''
    #         {
    #         "type": "change_player_points",
    #         "payload": {
    #             "rounds_to_apply": 2,
    #             "points": 10,
    #             "players": []
    #         }
    #         }
    #         ''', ''),
    #     ('Hospital', 40, 1, 2, '''
    #         {
    #         "type": "change_player_points",
    #         "payload": {
    #             "rounds_to_apply": 3,
    #             "points": 3,
    #             "players": []
    #         }
    #         }
    #         ''', '')
    #         """
    # )
    cur.execute(
        """INSERT INTO cards VALUES
        
        ('Station', 20, 1, 2, '{"type": "change_player_points", "payload": {"rounds_to_apply": 1, "points": 10,"players": []}}', '{"type": "change_player_points", "payload": {"rounds_to_apply": 2, "points": -3,"players": []}}')

            """
    )
    con.commit()


if __name__ == "__main__":
    init_db()
