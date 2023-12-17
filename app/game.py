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
    cards = [
        _card("Уличный театр", SEC_CLT, 1,
              jobs=[
                  _job('Актёр', _deal(purse(coin(5)), purse(coin(1, CLT)))),
              ],
              project_jobs=[
                  _job('Прораб', _deal(purse(coin(5)), purse(coin(10)))),
                  _job('Строитель', _deal(purse(coin(5)), purse(coin(1, CLT))))
              ]),
        _card("Библиотека", SEC_SCN, 1,
              jobs=[
                  _job('Библиотекарь', _deal(purse(coin(5)), purse(coin(1, SCN)))),
              ],
              project_jobs=[
                  _job('Прораб', _deal(purse(coin(5)), purse(coin(10)))),
                  _job('Строитель', _deal(purse(coin(5)), purse(coin(1, SCN)))),
              ]),
        _card("Алтарь", SEC_RLG, 1,
              jobs=[
                  _job('Служка', _deal(purse(coin(5)), purse(coin(1, RLG)))),
              ],
              project_jobs=[
                  _job('Прораб', _deal(purse(coin(5)), purse(coin(10)))),
                  _job('Строитель', _deal(purse(coin(5)), purse(coin(1, RLG)))),
              ]),
        _card("Ломбард", SEC_FFN, 1,
              jobs=[
                  _job('Ростовщик', _deal(purse(coin(5)), purse(coin(1, PPR)))),
              ],
              project_jobs=[
                  _job('Прораб', _deal(purse(coin(5)), purse(coin(10)))),
                  _job('Строитель', _deal(purse(coin(5)), purse(coin(1, PPR)))),
              ]
              )
    ]

    return cards

