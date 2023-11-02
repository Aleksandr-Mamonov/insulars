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


def _card(name: str, family: str, tier: int, vacancy=None):
    return {
        "family": family,
        "tier": tier,
        "name": name,
        "points_to_succeed": int(tier) * 10,
        "min_team": max([tier-1, 2]),
        "max_team": max([tier, 2]),
        "vacancy": vacancy,
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


def _vacancy(name: str, income: int):
    return {'name': name, 'income': income}


def build_deck(families_num: int):
    families_num = max([families_num, 10])

    cards = [
        _card("Rickshaw", 'Transport', 1, vacancy=_vacancy('Извозчик', 10)),
        _card("Bike rental network", 'Transport', 2),
        _card("Taxi station", 'Transport', 3, vacancy=_vacancy('Логист', 40)),
        _card("Railway station", 'Transport', 4),
        _card("Airport", 'Transport', 5, vacancy=_vacancy('Министр транспорта', 75)),

        _card("Tent", 'Shopping', 1, vacancy=_vacancy('Лавочник', 15)),
        _card("Trailer", 'Shopping', 2),
        _card("Shop", 'Shopping', 3, vacancy=_vacancy('Торговец', 30)),
        _card("Market", 'Shopping', 4),
        _card("Shopping center", 'Shopping', 5, vacancy=_vacancy('Капиталист', 75)),

        _card("Kindergarten", 'Education', 1, vacancy=_vacancy('Воспитатель', 5)),
        _card("School", 'Education', 2),
        _card("College", 'Education', 3, vacancy=_vacancy('Профессор', 30)),
        _card("University", 'Education', 4),
        _card("Academy", 'Education', 5, vacancy=_vacancy('Академик', 70)),

        _card("Altar", 'Religion', 1, vacancy=_vacancy('Служка', 5)),
        _card("Chapel", 'Religion', 2),
        _card("Church", 'Religion', 3, vacancy=_vacancy('Священник', 20)),
        _card("Temple", 'Religion', 4),
        _card("Cathedral", 'Religion', 5, vacancy=_vacancy('Кадринал', 80)),

        _card("Rented office", 'Government', 1, vacancy=_vacancy('Зам зама', 3)),
        _card("Administration", 'Government', 2),
        _card("City hall", 'Government', 3, vacancy=_vacancy('Депутат', 25)),
        _card("Parliament", 'Government', 4),
        _card("Government house", 'Government', 5, vacancy=_vacancy('Сенатор', 85)),

        _card("Museum", 'Culture', 1, vacancy=_vacancy('Смотритель', 5)),
        _card("Theatre", 'Culture', 2),
        _card("Philarmony", 'Culture', 3, vacancy=_vacancy('Маэстро', 25)),
        _card("Opera", 'Culture', 4),
        _card("Cultural center", 'Culture', 5, vacancy=_vacancy('Поп-идол', 90)),

        _card("Hot dog trailer", 'Food', 1, vacancy=_vacancy('Официант', 10)),
        _card("Bakery", 'Food', 2),
        _card("Canteen", 'Food', 3, vacancy=_vacancy('Шеф-повар', 25)),
        _card("Restaurant", 'Food', 4),
        _card("Hotel", 'Food', 5, vacancy=_vacancy('Метродотель', 70)),

        _card("Emergency room", 'Medicine', 1, vacancy=_vacancy('Медбрат', 10)),
        _card("Local clinic", 'Medicine', 2),
        _card("City polyclinic", 'Medicine', 3, vacancy=_vacancy('Фельдшер', 25)),
        _card("Hospital", 'Medicine', 4),
        _card("Medical center", 'Medicine', 5, vacancy=_vacancy('Главврач', 70)),

        _card("Playground", 'Entertainment', 1, vacancy=_vacancy('Аниматор', 10)),
        _card("Amusement park", 'Entertainment', 2),
        _card("Cinema", 'Entertainment', 3,  vacancy=_vacancy('Администратор', 30)),
        _card("City park", 'Entertainment', 4),
        _card("Recreational complex", 'Entertainment', 5, vacancy=_vacancy('Гуру', 65)),

        _card("Pawnshop", 'Finance', 1, vacancy=_vacancy('Ростовщик', 15)),
        _card("Micro-credit", 'Finance', 2),
        _card("Bank", 'Finance', 3, vacancy=_vacancy('Банкир', 40)),
        _card("Exchange", 'Finance', 4),
        _card("Ministry of finance", 'Finance', 5, vacancy=_vacancy('Финансист', 80)),
    ]

    families = list(set([card['family'] for card in cards]))
    deck_card_families = random.sample(families, families_num)

    return [card for card in cards if card['family'] in deck_card_families]

