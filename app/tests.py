import unittest

from .money import coin, purse, has_enough, CLT, GLD, SCN, sum_purses
from .game import (
    assign_vacancies,
    issue_salaries,
    init as init_game,
    SEC_SCN,
    SEC_CLT,
    INIT_PLAYER_COINS
)


class TestMoneyMethods(unittest.TestCase):

    def test_has_enough_positive(self):
        price = purse(coin(5, GLD), coin(1, CLT))
        owned = purse(coin(5, GLD), coin(2, CLT))
        self.assertEqual(has_enough(owned, price), True)

    def test_has_enough_positive_non_matter_coins(self):
        price = purse(coin(5, GLD))
        owned = purse(coin(10, GLD), coin(1, SCN))
        self.assertEqual(has_enough(owned, price), True)

    def test_has_enough_negative(self):
        price = purse(coin(10, GLD))
        owned = purse(coin(5, GLD), coin(1, SCN))
        self.assertEqual(has_enough(owned, price), False)

    def test_has_enough_negative_has_no_needed_coin(self):
        price = purse(coin(5, GLD), coin(1, SCN))
        owned = purse(coin(10, GLD))
        self.assertEqual(has_enough(owned, price), False)

    def test_sum_purses(self):
        p1 = purse(coin(5, GLD), coin(3, SCN))
        p2 = purse(coin(3, GLD), coin(2, SCN))
        ttl = sum_purses(p1, p2)

        self.assertEqual(p1[SCN]['amount'], 3)
        self.assertEqual(p1[GLD]['amount'], 5)
        self.assertEqual(p2[SCN]['amount'], 2)
        self.assertEqual(p2[GLD]['amount'], 3)
        self.assertEqual(ttl[SCN]['amount'], 5)
        self.assertEqual(ttl[GLD]['amount'], 8)

    def test_sum_purses_absent_currency(self):
        p1 = purse(coin(5, GLD))
        p2 = purse(coin(2, SCN))
        ttl = sum_purses(p1, p2)

        self.assertEqual(ttl[SCN]['amount'], 2)
        self.assertEqual(ttl[GLD]['amount'], 5)


class TestGameMethods(unittest.TestCase):

    def test_assign_vacancies(self):
        game = init_game([
            {'player_name': 'A'},
            {'player_name': 'B'},
            {'player_name': 'C'},
        ], 10)
        game['players']['A']['purse'] = game['vacancies'][SEC_SCN]['min_purse']
        game['players']['C']['purse'] = game['vacancies'][SEC_CLT]['min_purse']
        game = assign_vacancies(game)

        self.assertEqual(game['vacancies'][SEC_SCN]['assignee'], 'A')
        self.assertEqual(game['vacancies'][SEC_CLT]['assignee'], 'C')

    def test_assign_vacancies_no_assignee_on_equality(self):
        game = init_game([
            {'player_name': 'A'},
            {'player_name': 'B'},
            {'player_name': 'C'},
        ], 10)
        game['players']['A']['purse'] = game['vacancies'][SEC_SCN]['min_purse']
        game['players']['C']['purse'] = game['vacancies'][SEC_SCN]['min_purse']
        game = assign_vacancies(game)

        self.assertEqual(game['vacancies'][SEC_SCN]['assignee'], None)

    def test_assign_vacancies_no_assignment_on_low_currency(self):
        game = init_game([
            {'player_name': 'A'},
            {'player_name': 'B'},
            {'player_name': 'C'},
        ], 10)
        game['players']['A']['purse'] = purse(coin(1, SCN))
        game = assign_vacancies(game)

        self.assertEqual(game['vacancies'][SEC_SCN]['assignee'], None)

    def test_issue_salaries(self):
        game = init_game([
            {'player_name': 'A'},
            {'player_name': 'B'},
            {'player_name': 'C'},
        ], 10)

        game['players']['A']['purse'] = game['vacancies'][SEC_SCN]['min_purse']
        game['players']['C']['purse'] = game['vacancies'][SEC_CLT]['min_purse']
        game = assign_vacancies(game)
        game = issue_salaries(game)

        self.assertEqual(game['players']['A']['purse'][GLD]['amount'], game['vacancies'][SEC_SCN]['salary']['amount'])
        self.assertEqual(game['players']['B']['purse'][GLD]['amount'], INIT_PLAYER_COINS)
        self.assertEqual(game['players']['C']['purse'][GLD]['amount'], game['vacancies'][SEC_SCN]['salary']['amount'])


if __name__ == '__main__':
    unittest.main()
