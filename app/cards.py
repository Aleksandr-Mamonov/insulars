import random

CATEGORIES_OF_PLAYERS = ["all", "leader", "team", "others", "random_player"]
"""
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
"""


def _card(name: str, family: str, tier: int, vacancy=None, feature=None, repeatable=False):
    card = {
        "family": family,
        "tier": tier,
        "name": name,
        "points_to_succeed": int(tier) * 10,
        "min_team": max([tier - 1, 2]),
        "max_team": max([tier, 2]),
        "vacancy": vacancy,
        "feature": feature,
        "repeatable": repeatable,
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

    return card


def _vacancy(name: str, income: int):
    return {'name': name, 'income': income}


def _feat(feat_type, magnitude):
    return {'type': feat_type, 'magnitude': magnitude}


def build_deck(families_num: int):
    families_num = min([families_num, 10])
    cards = [
        # Transport
        _card("Rickshaw", 'Transport', 1,
              vacancy=_vacancy('Извозчик', 10),
              feature=_feat('cards_cost', -3)
              ),
        _card("Bike rental network", 'Transport', 2),
        _card("Taxi station", 'Transport', 3,
              vacancy=_vacancy('Логист', 40),
              feature=_feat('cards_cost', -5)
              ),
        _card("Railway station", 'Transport', 4),
        _card("Airport", 'Transport', 5,
              vacancy=_vacancy('Министр транспорта', 75),
              feature=_feat('cards_cost', -10)
              ),
        # Prompt:
        # Massive ceremonial event for the opening of new international airlines at the airport
        _card("Запуск авиамаршрута", 'Transport', 6, repeatable=True),

        #  Shopping
        _card("Tent", 'Shopping', 1,
              vacancy=_vacancy('Лавочник', 15),
              feature=_feat('cards_cost', +3)
              ),
        _card("Trailer", 'Shopping', 2),
        _card("Shop", 'Shopping', 3,
              vacancy=_vacancy('Торговец', 30),
              feature=_feat('cards_cost', +5)
              ),
        _card("Market", 'Shopping', 4),
        _card("Shopping center", 'Shopping', 5,
              vacancy=_vacancy('Капиталист', 75),
              feature=_feat('cards_cost', +10)
              ),
        # Prompt:
        # Shopping event like Black Friday with a lot of people and shiny showcases around
        _card("Черная пятница", 'Shopping', 6, repeatable=True),

        #  Education
        _card("Kindergarten", 'Education', 1,
              vacancy=_vacancy('Воспитатель', 5),
              feature=_feat('cards_reward', +3),
              ),
        _card("School", 'Education', 2),
        _card("College", 'Education', 3,
              vacancy=_vacancy('Профессор', 30),
              feature=_feat('cards_reward', +5),
              ),
        _card("University", 'Education', 4),
        _card("Academy", 'Education', 5,
              vacancy=_vacancy('Академик', 70),
              feature=_feat('cards_reward', +10),
              ),
        # Prompt:
        # Scientific lection in a physical laboratory with a lector and few listeners
        _card("Конференция", 'Education', 6, repeatable=True),

        # Religion
        _card("Altar", 'Religion', 1,
              vacancy=_vacancy('Служка', 5),
              feature=_feat('cards_reward', -3),
              ),
        _card("Chapel", 'Religion', 2),
        _card("Church", 'Religion', 3,
              vacancy=_vacancy('Священник', 20),
              feature=_feat('cards_reward', -5)
              ),
        _card("Temple", 'Religion', 4),
        _card("Cathedral", 'Religion', 5,
              vacancy=_vacancy('Кадринал', 80),
              feature=_feat('cards_reward', -10)
              ),
        # Prompt:
        # Mysterious religious ritual with a lot of people in the center of the city, which looks like from noir movies
        _card("Обряд", 'Religion', 6, repeatable=True),

        # Government
        _card("Rented office", 'Government', 1,
              vacancy=_vacancy('Зам зама', 3),
              feature=_feat('clerks_salary', +3),
              ),
        _card("Administration", 'Government', 2),
        _card("City hall", 'Government', 3,
              vacancy=_vacancy('Депутат', 25),
              feature=_feat('clerks_salary', +5),
              ),
        _card("Parliament", 'Government', 4),
        _card("Government house", 'Government', 5,
              vacancy=_vacancy('Сенатор', 85),
              feature=_feat('clerks_salary', +10)
              ),
        # Prompt:
        # An official political debates between several people in a TV studio in a noir like movie style
        _card("Дебаты", 'Government', 6, repeatable=True),

        # Culture
        _card("Museum", 'Culture', 1,
              vacancy=_vacancy('Смотритель', 5),
              feature=_feat('clerks_salary', -3)),
        _card("Theatre", 'Culture', 2),
        _card("Philarmony", 'Culture', 3,
              vacancy=_vacancy('Маэстро', 25),
              feature=_feat('clerks_salary', -5),
              ),
        _card("Opera", 'Culture', 4),
        _card("Cultural center", 'Culture', 5,
              vacancy=_vacancy('Поп-идол', 90),
              feature=_feat('clerks_salary', -10),
              ),
        # Prompt:
        # A celebration of fun holiday with a lot of live music and people on the streets
        # in the center of the city, which looks like from noir movies
        _card("Фестиваль", 'Culture', 6, repeatable=True),

        # Food
        _card("Hot dog trailer", 'Food', 1,
              vacancy=_vacancy('Официант', 10),
              feature=_feat('basic_income', +5),
              ),
        _card("Bakery", 'Food', 2),
        _card("Canteen", 'Food', 3,
              vacancy=_vacancy('Шеф-повар', 25),
              feature=_feat('basic_income', +10),
              ),
        _card("Restaurant", 'Food', 4),
        _card("Hotel", 'Food', 5,
              vacancy=_vacancy('Метродотель', 70),
              feature=_feat('basic_income', +15),
              ),
        # Prompt:
        # Great food festival with a lot of people and dishes around on the streets in the center of the city
        _card("Ярмарка", 'Food', 6, repeatable=True),

        _card("Emergency room", 'Medicine', 1,
              vacancy=_vacancy('Медбрат', 10),
              feature=_feat('basic_income', +3),
              ),
        _card("Local clinic", 'Medicine', 2),
        _card("City polyclinic", 'Medicine', 3,
              vacancy=_vacancy('Фельдшер', 25),
              feature=_feat('basic_income', +5),
              ),
        _card("Hospital", 'Medicine', 4),
        _card("Medical center", 'Medicine', 5,
              vacancy=_vacancy('Главврач', 70),
              feature=_feat('basic_income', +10),
              ),
        # Prompt:
        # Scientific medical conference in a luxurious hotel with a lot of people and a speeker on a tribune
        _card("Симпозиум", 'Medicine', 6, repeatable=True),

        _card("Playground", 'Entertainment', 1,
              vacancy=_vacancy('Аниматор', 10),
              feature=_feat('random_gift', +10),
              ),
        _card("Amusement park", 'Entertainment', 2),
        _card("Cinema", 'Entertainment', 3,
              vacancy=_vacancy('Администратор', 30),
              feature=_feat('random_gift', +15),
              ),
        _card("City park", 'Entertainment', 4),
        _card("Recreational complex", 'Entertainment', 5,
              vacancy=_vacancy('Гуру', 65),
              feature=_feat('random_gift', +25),
              ),
        # Prompt:
        # Massive crowdy final of world wide football championship on a huge stadium
        _card("Чемпионат мира", 'Entertainment', 6, repeatable=True),

        _card("Pawnshop", 'Finance', 1,
              vacancy=_vacancy('Ростовщик', 15),
              feature=_feat('random_gift', -10),
              ),
        _card("Micro-credit", 'Finance', 2),
        _card("Bank", 'Finance', 3,
              vacancy=_vacancy('Банкир', 40),
              feature=_feat('random_gift', -15),
              ),
        _card("Exchange", 'Finance', 4),
        _card("Ministry of finance", 'Finance', 5,
              vacancy=_vacancy('Финансист', 80),
              feature=_feat('random_gift', -25),
              ),
        # Prompt:
        # A hectic day of trading at the stock exchange with several clerks holding papers in their hands
        _card("Торги", 'Entertainment', 6, repeatable=True),
    ]

    families = list(set([card["family"] for card in cards]))
    deck_card_families = random.sample(families, families_num)

    return [card for card in cards if card["family"] in deck_card_families]
