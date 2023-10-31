from pprint import pprint

CATEGORIES_OF_PLAYERS = ["all", "leader", "team", "others", "random_player"]
EFFECTS = [
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
CARD_FAMILIES = {
    "Transport": {
        "1": "Rickshaw",
        "2": "Bike rental network",
        "3": "Taxi station",
        "4": "Railway station",
        "5": "Airport",
    },
    "Shopping": {
        "1": "Tent",
        "2": "Trailer",
        "3": "Shop",
        "4": "Market",
        "5": "Shopping center",
    },
    "Education": {
        "1": "Kindergarten",
        "2": "School",
        "3": "College",
        "4": "University",
        "5": "Academy",
    },
    "Religion": {
        "1": "Altar",
        "2": "Chapel",
        "3": "Church",
        "4": "Temple",
        "5": "Cathedral",
    },
    "Government": {
        "1": "Rented office",
        "2": "Administration building",
        "3": "City hall",
        "4": "Ministry",
        "5": "Government house",
    },
    "Culture": {
        "1": "Museum",
        "2": "Theatre",
        "3": "Philarmony",
        "4": "Opera",
        "5": "Cultural center",
    },
    "Food": {
        "1": "Hot dog trailer",
        "2": "Bakery",
        "3": "Canteen",
        "4": "Farm",
        "5": "Food plant",
    },
    "Medicine": {
        "1": "Emergency room",
        "2": "Local clinic",
        "3": "City polyclinic",
        "4": "Hospital",
        "5": "Medical center",
    },
    "Entertainment": {
        "1": "Playground",
        "2": "Amusement park",
        "3": "Cinema",
        "4": "City park",
        "5": "Recreational complex",
    },
    "Finance": {
        "1": "Pawnshop",
        "2": "Micro-credit",
        "3": "Bank",
        "4": "Exchange",
        "5": "Ministry of finance",
    },
}

"""
Card template
{
    'family': <str> from CARD_FAMILIES.keys(),
    'tier': <str> from ['1','2','3','4','5']
    "name": CARD_FAMILIES['family']['tier']
    "points_to_succeed": <int(tier)> * 10,
    "min_team": <int> >= 2,
    "max_team": <int> < config.MAX_PLAYERS,
    "on_success": [effect1: <dict>, effect2: <dict>, ...],
    "on_failure": [effect1: <dict>, effect2: <dict>, ...],
}
"""
TIER_EFFECTS = {
    "1": {"on_success": [], "on_failure": []},
    "2": {"on_success": [], "on_failure": []},
    "3": {"on_success": [], "on_failure": []},
    "4": {"on_success": [], "on_failure": []},
    "5": {"on_success": [], "on_failure": []},
}


def generate_cards(card_families: dict):
    cards = [
        {
            "family": family,
            "tier": tier,
            "name": card_families[family][tier],
            "points_to_succeed": int(tier) * 10,
            "min_team": int(tier) + 1,
            "max_team": int(tier) + 1,
            "on_success": [
                {
                    "name": "change_player_points",
                    "type": "positive",
                    "payload": {
                        "categories_of_players": ["team"],
                        "players": [],
                        "rounds_to_apply": int(tier),
                        "points": 10,
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
                        "categories_of_players": ["random_player"],
                        "players": [],
                        "rounds_to_apply": int(tier),
                        "points": -10,
                    },
                },
            ],
        }
        for family in card_families.keys()
        for tier in card_families[family].keys()
    ]
    return cards


CARDS = [
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
NEW_CARDS = generate_cards(CARD_FAMILIES)
