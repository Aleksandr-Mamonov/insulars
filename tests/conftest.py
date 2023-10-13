import pytest


@pytest.fixture(scope="package")
def room_id_fixture():
    return "some_random_room_id"


@pytest.fixture(scope="package")
def game_fixture():
    return {
        "game_id": "d3652faa-6405-4a7c-8c10-f532fb76adde",
        "round": 2,
        "players": ["a", "b", "c"],
        "players_order_in_round": ["b", "c", "a"],
        "players_to_move": ["b", "c", "a"],
        "active_player": "b",
        "leader": "b",
        "all_players_points": {"a": 10, "b": 7, "c": 7},
        "round_common_account_points": 0,
        "cards_on_table": [
            {
                "card_id": 67,
                "name": "Cinema",
                "points_to_succeed": 20,
                "min_team": 2,
                "max_team": 2,
                "on_success": '[\n                                    {\n                                        "name": "change_player_points",\n                                        "type": "positive",\n                                        "payload": {\n                                            "rounds_to_apply": 3,\n                                            "categories_of_players": ["team"],\n                                            "points": 6,\n                                            "players": []\n                                        }\n                                    },\n                                    {\n                                        "name": "give_overpayment",\n                                        "type": "positive",\n                                        "payload": {\n                                            "categories_of_players": ["leader"],\n                                            "players": []\n                                        }\n                                    }\n                                ]',
                "on_failure": '[\n                                    {\n                                        "name": "change_player_points",\n                                        "type": "negative",\n                                        "payload": {\n                                            "rounds_to_apply": 3,\n                                            "categories_of_players": ["team", "leader"],\n                                            "points": -1,\n                                            "players": []\n                                        }\n                                    }\n                                ]',
            },
            {
                "card_id": 82,
                "name": "Theatre",
                "points_to_succeed": 20,
                "min_team": 2,
                "max_team": 2,
                "on_success": '[\n                                    {\n                                        "name": "change_player_points",\n                                        "type": "positive",\n                                        "payload": {\n                                            "rounds_to_apply": 2,\n                                            "categories_of_players": ["team"],\n                                            "points": 8,\n                                            "players": []\n                                        }\n                                    },\n                                    {\n                                        "name": "give_overpayment",\n                                        "type": "positive",\n                                        "payload": {\n                                            "categories_of_players": ["leader"],\n                                            "players": []\n                                        }\n                                    }\n                                ]',
                "on_failure": '[\n                                    {\n                                        "name": "change_player_points",\n                                        "type": "negative",\n                                        "payload": {\n                                            "rounds_to_apply": 2,\n                                            "categories_of_players": ["team", "leader"],\n                                            "points": -2,\n                                            "players": []\n                                        }\n                                    }\n                                ]',
            },
            {
                "card_id": 89,
                "name": "Museum",
                "points_to_succeed": 30,
                "min_team": 2,
                "max_team": 2,
                "on_success": '[\n                                    {\n                                        "name": "change_player_points",\n                                        "type": "positive",\n                                        "payload": {\n                                            "rounds_to_apply": 4,\n                                            "categories_of_players": ["team"],\n                                            "points": 9,\n                                            "players": []\n                                        }\n                                    },\n                                    {\n                                        "name": "give_overpayment",\n                                        "type": "positive",\n                                        "payload": {\n                                            "categories_of_players": ["leader"],\n                                            "players": []\n                                        }\n                                    }\n                                ]',
                "on_failure": '[\n                                    {\n                                        "name": "change_player_points",\n                                        "type": "negative",\n                                        "payload": {\n                                            "rounds_to_apply": 4,\n                                            "categories_of_players": ["team", "leader"],\n                                            "points": -1,\n                                            "players": []\n                                        }\n                                    }\n                                ]',
            },
        ],
        "cards_selected_by_leader": [],
        "team": [],
        "effects_to_apply": [
            {
                "name": "change_player_points",
                "type": "negative",
                "payload": {
                    "rounds_to_apply": 2,
                    "categories_of_players": ["team", "leader"],
                    "points": -2,
                    "players": ["b", "c", "a"],
                },
            }
        ],
        "rounds": 10,
        "card_effect_visibility": {
            "onSuccess": {"leader": True, "players": True},
            "onFailure": {"leader": True, "players": True},
        },
        "round_delta": -14,
    }


@pytest.fixture(scope="package")
def effects_fixture():
    return [
        {
            "name": "change_player_points",
            "type": "negative",
            "payload": {
                "rounds_to_apply": 3,
                "categories_of_players": ["team", "leader"],
                "points": -2,
                "players": ["b", "c"],
            },
        },
        {
            "name": "change_player_points",
            "type": "positive",
            "payload": {
                "rounds_to_apply": 4,
                "categories_of_players": ["leader"],
                "points": 3,
                "players": ["a"],
            },
        },
    ]
