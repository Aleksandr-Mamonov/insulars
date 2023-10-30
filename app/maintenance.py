import json
import sqlite3

from .database import write_to_db
from .cards import CARDS


def init_db():
    con = sqlite3.connect("insulars.db")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS rooms(uid, owner, game, number_of_games INTEGER DEFAULT 0)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS room_players(room_id, player_name, portrait_id)"
    )
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
    for card in CARDS:
        write_to_db(
            """
        INSERT INTO cards (name, points_to_succeed, min_team, max_team, on_success, on_failure)
        VALUES (:name, :points_to_succeed, :min_team, :max_team, :on_success, :on_failure)
        """,
            {
                "name": card["name"],
                "points_to_succeed": card["points_to_succeed"],
                "min_team": card["min_team"],
                "max_team": card["max_team"],
                "on_success": json.dumps(card["on_success"]),
                "on_failure": json.dumps(card["on_failure"]),
            },
        )
    con.commit()


if __name__ == "__main__":
    init_db()
