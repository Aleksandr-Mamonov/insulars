import json
import sqlite3

from .database import write_to_db


def init_db():
    con = sqlite3.connect("insulars.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS rooms(uid, owner, game, number_of_games INTEGER DEFAULT 0)")
    cur.execute("CREATE TABLE IF NOT EXISTS room_players(room_id, player_name, portrait_id)")
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

    for card in cards:
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

cards = [
    {
        "name": "Station",
        "points_to_succeed": 20,
        "min_team": 2,
        "max_team": 2,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 1,
                    "categories_of_players": ["team"],
                    "points": 15,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 1,
                    "categories_of_players": ["team", "leader"],
                    "points": -3,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Theatre",
        "points_to_succeed": 20,
        "min_team": 2,
        "max_team": 2,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 2,
                    "categories_of_players": ["team"],
                    "points": 8,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 2,
                    "categories_of_players": ["team", "leader"],
                    "points": -2,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Cinema",
        "points_to_succeed": 20,
        "min_team": 2,
        "max_team": 2,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 3,
                    "categories_of_players": ["team"],
                    "points": 6,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 3,
                    "categories_of_players": ["team", "leader"],
                    "points": -1,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "School",
        "points_to_succeed": 20,
        "min_team": 2,
        "max_team": 2,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 4,
                    "categories_of_players": ["team"],
                    "points": 5,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 4,
                    "categories_of_players": ["team", "leader"],
                    "points": -1,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Restaurant",
        "points_to_succeed": 20,
        "min_team": 2,
        "max_team": 2,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 5,
                    "categories_of_players": ["team"],
                    "points": 5,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 5,
                    "categories_of_players": ["team", "leader"],
                    "points": -1,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Church",
        "points_to_succeed": 30,
        "min_team": 2,
        "max_team": 2,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 1,
                    "categories_of_players": ["team"],
                    "points": 25,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 1,
                    "categories_of_players": ["team", "leader"],
                    "points": -3,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Market",
        "points_to_succeed": 30,
        "min_team": 2,
        "max_team": 2,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 2,
                    "categories_of_players": ["team"],
                    "points": 13,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 2,
                    "categories_of_players": ["team", "leader"],
                    "points": -2,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Highway",
        "points_to_succeed": 30,
        "min_team": 2,
        "max_team": 2,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 3,
                    "categories_of_players": ["team"],
                    "points": 10,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 3,
                    "categories_of_players": ["team", "leader"],
                    "points": -1,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Museum",
        "points_to_succeed": 30,
        "min_team": 2,
        "max_team": 2,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 4,
                    "categories_of_players": ["team"],
                    "points": 9,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 4,
                    "categories_of_players": ["team", "leader"],
                    "points": -1,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Library",
        "points_to_succeed": 30,
        "min_team": 2,
        "max_team": 2,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 5,
                    "categories_of_players": ["team"],
                    "points": 8,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 5,
                    "categories_of_players": ["team", "leader"],
                    "points": -1,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Plant",
        "points_to_succeed": 40,
        "min_team": 3,
        "max_team": 3,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 1,
                    "categories_of_players": ["team"],
                    "points": 25,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 1,
                    "categories_of_players": ["team", "leader"],
                    "points": -3,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Factory",
        "points_to_succeed": 40,
        "min_team": 3,
        "max_team": 3,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 2,
                    "categories_of_players": ["team"],
                    "points": 14,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 2,
                    "categories_of_players": ["team", "leader"],
                    "points": -2,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "University",
        "points_to_succeed": 40,
        "min_team": 3,
        "max_team": 3,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 3,
                    "categories_of_players": ["team"],
                    "points": 10,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 3,
                    "categories_of_players": ["team", "leader"],
                    "points": -1,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Airport",
        "points_to_succeed": 60,
        "min_team": 4,
        "max_team": 4,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 1,
                    "categories_of_players": ["team"],
                    "points": 30,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 1,
                    "categories_of_players": ["team", "leader"],
                    "points": -3,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Bus_station",
        "points_to_succeed": 60,
        "min_team": 4,
        "max_team": 4,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 2,
                    "categories_of_players": ["team"],
                    "points": 17,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 2,
                    "categories_of_players": ["team", "leader"],
                    "points": -2,
                    "players": [],
                },
            }
        ],
    },
    {
        "name": "Metro_station",
        "points_to_succeed": 60,
        "min_team": 4,
        "max_team": 4,
        "on_success": [
            {
                "name": "change_player_points",
                "type": "positive",
                "payload": {
                    "rounds_to_apply": 3,
                    "categories_of_players": ["team"],
                    "points": 13,
                    "players": [],
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
        ],
        "on_failure": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 3,
                    "categories_of_players": ["team", "leader"],
                    "points": -1,
                    "players": [],
                },
            }
        ],
    },
]


if __name__ == "__main__":
    init_db()
