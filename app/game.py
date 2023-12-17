import random
import uuid

from .money import has_enough, sum_purses, purse, coin, CLT, RLG, SCN, PPR

SEC_PRD = 'production'
SEC_CLT = 'culture'
SEC_FFN = 'finance'
SEC_SCN = 'science'
SEC_RLG = 'religion'

SEC_ENT = 'entertainment'
SEC_MED = 'medicine'
SEC_SHP = 'shopping'
SEC_MNG = 'management'

INIT_PLAYER_COINS = 5


def _deal(price, reward):
    return [price, reward]


def _job(name, deal):
    return {
        'name': name,
        "deal": deal,
    }


def _card(name: str, family: str, tier: int, card_type: str = 'house', project_jobs=None, jobs=None):
    card = {
        "name": name,
        "card_type":  card_type,
        "family": family,
        "tier": tier,
        "repeatable": card_type != 'house',
        "jobs": jobs or [],
        'project_jobs': project_jobs or []
    }

    return card


def init(players: list, rounds: int):
    player_names = [pl["player_name"] for pl in players]
    leader = random.choice(player_names)

    game = {
        "game_id": str(uuid.uuid4()),
        "round": 0,
        "players": {pl["player_name"]: {'name': pl["player_name"], "purse": purse(coin(INIT_PLAYER_COINS))} for pl in players},
        "players_order": player_names,
        "leader": leader,
        "rounds": rounds,
        "houses": [],
        "round_cards_draw": [],
        'active_player': leader,
        'selected_house': None,
        'job_assignment': {},
        'vacancies': {
            SEC_SCN: {'name': 'Учёный', 'assignee': None, 'salary': coin(10),
                      'currency': [SCN],
                      'min_purse': purse(coin(2, SCN))},
            SEC_CLT: {'name': 'Маэстро', 'assignee': None, 'salary': coin(10),
                      'currency': [CLT],
                      'min_purse': purse(coin(2, CLT))},
            SEC_FFN: {'name': 'Банкир', 'assignee': None, 'salary': coin(10),
                      'currency': [PPR],
                      'min_purse': purse(coin(2, PPR))},
            SEC_RLG: {'name': 'Гуру', 'assignee': None, 'salary': coin(10),
                      'currency': [RLG],
                      'min_purse': purse(coin(2, RLG))},
            SEC_ENT: {'name': 'Поп звезда', 'assignee': None, 'salary': coin(10),
                      'currency': [RLG, CLT],
                      'min_purse': purse(coin(1, RLG), coin(1, CLT))},
            SEC_MED: {'name': 'Главрач', 'assignee': None, 'salary': coin(10),
                      'currency': [SCN, CLT],
                      'min_purse': purse(coin(1, SCN), coin(1, CLT))},
            SEC_SHP: {'name': 'Магнат', 'assignee': None, 'salary': coin(10),
                      'currency': [RLG, PPR],
                      'min_purse': purse(coin(1, RLG), coin(1, PPR))},
            SEC_MNG: {'name': 'Управляющий', 'assignee': None, 'salary': coin(10),
                      'currency': [SCN, PPR],
                      'min_purse': purse(coin(1, SCN), coin(1, PPR))},
        }
    }

    # выбрать N дефолтных строений по количеству игроков
    # чтобы обеспечить стартовые работы
    for house in _default_houses(len(players)):
        game['houses'].append(house)

    return game


def _max_coins_player(players, currencies: list):
    winner = None

    max_coins = 0
    for player in players.values():
        total_sum = 0
        for curr in currencies:
            total_sum += player['purse'][curr]['amount'] if curr in player['purse'] else 0

        if max_coins < total_sum:
            winner = player
            max_coins = total_sum
        elif max_coins == total_sum:
            winner = None

    return winner


def issue_salaries(game):
    for sector, vacancy in game['vacancies'].items():
        assignee = vacancy['assignee']
        if assignee:
            game['players'][assignee]['purse'] = sum_purses(game['players'][assignee]['purse'], purse(vacancy['salary']))

    return game


def assign_vacancies(game):
    for sector, vacancy in game['vacancies'].items():
        assignee = _max_coins_player(game['players'], vacancy['currency'])
        has_assignee = assignee is not None and has_enough(assignee['purse'], vacancy['min_purse'])
        game['vacancies'][sector]['assignee'] = assignee['name'] if has_assignee else None

    return game


def _default_houses(n):
    basic_deal = _deal(purse(coin(0)), purse(coin(5)))
    cards = [
        _card('Лагерь', SEC_PRD, 1, jobs=[_job("Охотник", basic_deal)]),
        _card('Причал', SEC_PRD, 1, jobs=[_job("Рыбак", basic_deal)]),
        _card('Шахта', SEC_PRD, 1, jobs=[_job("Шахтёр", basic_deal)]),
        _card('Хижина', SEC_PRD, 1, jobs=[_job("Егерь", basic_deal)]),
        _card('Кузница', SEC_PRD, 1, jobs=[_job("Кузнец", basic_deal)]),
        _card('Пекарня', SEC_PRD, 1, jobs=[_job("Пекарь", basic_deal)]),
        _card('Дровня', SEC_PRD, 1, jobs=[_job("Дровосек", basic_deal)]),
        _card('Мастерская', SEC_PRD, 1, jobs=[_job("Гончар", basic_deal)]),
    ]

    return random.sample(cards, min([n, 8]))


def build_deck():
    novice_builder_job = _job('Прораб', _deal(purse(coin(5)), purse(coin(10))))
    advanced_builder_job = _job('Менеджер', _deal(purse(coin(15)), purse(coin(30))))
    expert_builder_job = _job('Шеф', _deal(purse(coin(50)), purse(coin(100))))

    def novice_mastery_deal(curr):
        return _deal(purse(coin(5)), purse(coin(1, curr)))

    def advanced_mastery_deal(curr):
        return _deal(purse(coin(5), coin(1, curr)), purse(coin(3, curr)))

    def expert_mastery_deal(curr, secondary_currencies: list):
        price_coins = [coin(5)]
        for secondary_curr in secondary_currencies:
            price_coins.append(coin(1, secondary_curr))

        return _deal(purse(*price_coins), purse(coin(10), coin(7, curr)))

    cards = list()
    cards.extend([
        _card("Балаган", SEC_CLT, 1,
              jobs=[
                  _job('Мим', novice_mastery_deal(CLT)),
              ],
              project_jobs=[
                  novice_builder_job,
                  _job('Подмастерье', novice_mastery_deal(CLT))
              ]),
        _card("Варьете", SEC_CLT, 2,
              jobs=[
                  _job('Актёр', advanced_mastery_deal(CLT)),
              ],
              project_jobs=[
                  advanced_builder_job,
                  _job('Подмастерье', advanced_mastery_deal(CLT))
              ]),
        _card("Опера", SEC_CLT, 3,
              jobs=[
                  _job('Дирижёр', expert_mastery_deal(CLT, [RLG, SCN])),
              ],
              project_jobs=[
                  expert_builder_job,
                  _job('Подмастерье', expert_mastery_deal(CLT, [RLG, SCN]))
              ])
    ])

    cards.extend([
        _card("Библиотека", SEC_SCN, 1,
              jobs=[
                  _job('Библиотекарь', novice_mastery_deal(SCN)),
              ],
              project_jobs=[
                  novice_builder_job,
                  _job('Подмастерье', novice_mastery_deal(SCN)),
              ]),
        _card("Школа", SEC_SCN, 2,
              jobs=[
                  _job('Учитель', advanced_mastery_deal(SCN)),
              ],
              project_jobs=[
                  advanced_builder_job,
                  _job('Подмастерье', advanced_mastery_deal(SCN)),
              ]),
        _card("Университет", SEC_SCN, 3,
              jobs=[
                  _job('Профессор', expert_mastery_deal(SCN, [CLT, PPR])),
              ],
              project_jobs=[
                  expert_builder_job,
                  _job('Подмастерье', expert_mastery_deal(SCN, [CLT, PPR])),
              ]),
    ])

    cards.extend([
        _card("Алтарь", SEC_RLG, 1,
              jobs=[
                  _job('Служка', novice_mastery_deal(RLG)),
              ],
              project_jobs=[
                  novice_builder_job,
                  _job('Подмастерье', novice_mastery_deal(RLG)),
              ]),
        _card("Часовня", SEC_RLG, 2,
              jobs=[
                  _job('Священник', advanced_mastery_deal(RLG)),
              ],
              project_jobs=[
                  advanced_builder_job,
                  _job('Подмастерье', advanced_mastery_deal(RLG)),
              ]),
        _card("Храм", SEC_RLG, 3,
              jobs=[
                  _job('Епископ', expert_mastery_deal(RLG, [PPR, CLT])),
              ],
              project_jobs=[
                  expert_builder_job,
                  _job('Подмастерье', expert_mastery_deal(RLG, [PPR, CLT])),
              ]),
    ])

    cards.extend([
        _card("Ломбард", SEC_FFN, 1,
              jobs=[
                  _job('Ростовщик', novice_mastery_deal(PPR)),
              ],
              project_jobs=[
                  novice_builder_job,
                  _job('Подмастерье', novice_mastery_deal(PPR)),
              ]),
        _card("Банк", SEC_FFN, 2,
              jobs=[
                  _job('Банкир', advanced_mastery_deal(PPR)),
              ],
              project_jobs=[
                  advanced_builder_job,
                  _job('Подмастерье', advanced_mastery_deal(PPR)),
              ]),
        _card("Биржа", SEC_FFN, 3,
              jobs=[
                  _job('Брокер', expert_mastery_deal(PPR, [RLG, SCN])),
              ],
              project_jobs=[
                  expert_builder_job,
                  _job('Подмастерье', expert_mastery_deal(PPR, [RLG, SCN])),
              ]),
    ])

    return cards

