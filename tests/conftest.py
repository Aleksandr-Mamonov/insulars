import pytest


@pytest.fixture(scope="function")
def game_fixture():
    return {
        "game_id": "d3652faa-6405-4a7c-8c10-f532fb76adde",
        "round": 2,
        "players": ["a", "b", "c", "d"],
        "players_order_in_round": [],
        "players_to_move": [],
        "active_player": "",
        "leader": "",
        "all_players_points": {"a": 10, "b": 7, "c": 4, "d": 1},
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
        "effects_to_apply": [],
        "rounds": 10,
        "card_effect_visibility": {
            "onSuccess": {"leader": True, "players": True},
            "onFailure": {"leader": True, "players": True},
        },
        "round_delta": 0,
    }


@pytest.fixture(scope="function")
def effect_change_player_points_fixture():
    return {
        "name": "change_player_points",
        "type": "",
        "payload": {
            "categories_of_players": [],
            "players": [],
            "rounds_to_apply": 1,
            "points": 0,
        },
    }


@pytest.fixture(scope="function")
def effect_give_overpayment_fixture():
    return {
        "name": "give_overpayment",
        "type": "positive",
        "payload": {
            "categories_of_players": [],
            "players": [],
        },
    }


@pytest.fixture(scope="function")
def effect_take_away_underpayment_fixture():
    return {
        "name": "take_away_underpayment",
        "type": "negative",
        "payload": {
            "categories_of_players": [],
            "players": [],
        },
    }


@pytest.fixture(scope="function")
def effect_leadership_ban_next_time_fixture():
    return {
        "name": "leadership_ban_next_time",
        "type": "negative",
        "payload": {
            "categories_of_players": ["leader"],
            "players": [],
        },
    }
