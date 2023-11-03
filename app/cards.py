from .config import MIN_PLAYERS
import random

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


card_features = {
    "Transport": "decrease_cards_costs",
    "Shopping": "increase_cards_costs",
    "Education": "increase_cards_rewards",
    "Religion": "decrease_cards_rewards",
    "Government": "increase_clerks_pay",
    "Culture": "decrease_clerks_pay",
    "Food": "increase_basic_income_for_all",
    "Medicine": "decrease_basic_income_for_all",
    "Entertainment": "increase_basic_income_for_random",
    "Finance": "decrease_basic_income_for_random",
}
features_tiers_multiples = {
    "decrease": {1: 0.9, 3: 0.7, 5: 0.5},
    "increase": {1: 1.1, 3: 1.3, 5: 1.5},
}


def _card(name: str, family: str, tier: int):
    card = {
        "family": family,
        "tier": tier,
        "name": name,
        "points_to_succeed": int(tier) * 10,
        "min_team": max([tier - 1, 2]),
        "max_team": max([tier, 2]),
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
    feature = card_features[family]
    if tier in [1, 3, 5] and feature.startswith("increase"):
        card["feature"] = {
            "name": feature,
            "multiple": features_tiers_multiples["increase"][tier],
        }
    elif tier in [1, 3, 5] and feature.startswith("decrease"):
        card["feature"] = {
            "name": feature,
            "multiple": features_tiers_multiples["decrease"][tier],
        }
    return card


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


def build_deck(families_num: int):
    families_num = max([families_num, 10])

    cards = [
        _card("Rickshaw", "Transport", 1),
        _card("Bike rental network", "Transport", 2),
        _card("Taxi station", "Transport", 3),
        _card("Railway station", "Transport", 4),
        _card("Airport", "Transport", 5),
        _card("Tent", "Shopping", 1),
        _card("Trailer", "Shopping", 2),
        _card("Shop", "Shopping", 3),
        _card("Market", "Shopping", 4),
        _card("Shopping center", "Shopping", 5),
        _card("Kindergarten", "Education", 1),
        _card("School", "Education", 2),
        _card("College", "Education", 3),
        _card("University", "Education", 4),
        _card("Academy", "Education", 5),
        _card("Altar", "Religion", 1),
        _card("Chapel", "Religion", 2),
        _card("Church", "Religion", 3),
        _card("Temple", "Religion", 4),
        _card("Cathedral", "Religion", 5),
        _card("Rented office", "Government", 1),
        _card("Administration", "Government", 2),
        _card("City hall", "Government", 3),
        _card("Parliament", "Government", 4),
        _card("Government house", "Government", 5),
        _card("Museum", "Culture", 1),
        _card("Theatre", "Culture", 2),
        _card("Philarmony", "Culture", 3),
        _card("Opera", "Culture", 4),
        _card("Cultural center", "Culture", 5),
        _card("Hot dog trailer", "Food", 1),
        _card("Bakery", "Food", 2),
        _card("Canteen", "Food", 3),
        _card("Restaurant", "Food", 4),
        _card("Hotel", "Food", 5),
        _card("Emergency room", "Medicine", 1),
        _card("Local clinic", "Medicine", 2),
        _card("City polyclinic", "Medicine", 3),
        _card("Hospital", "Medicine", 4),
        _card("Medical center", "Medicine", 5),
        _card("Playground", "Entertainment", 1),
        _card("Amusement park", "Entertainment", 2),
        _card("Cinema", "Entertainment", 3),
        _card("City park", "Entertainment", 4),
        _card("Recreational complex", "Entertainment", 5),
        _card("Pawnshop", "Finance", 1),
        _card("Micro-credit", "Finance", 2),
        _card("Bank", "Finance", 3),
        _card("Exchange", "Finance", 4),
        _card("Ministry of finance", "Finance", 5),
    ]

    families = list(set([card["family"] for card in cards]))
    deck_card_families = random.sample(families, families_num)

    return [card for card in cards if card["family"] in deck_card_families]
