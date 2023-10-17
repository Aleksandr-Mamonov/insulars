# pytest -W ignore::DeprecationWarning
import copy
from pprint import pprint as pp
import pytest

from app.main import apply_effects


class TestApplyEffectChangePlayerPoints:
    """Testing apply 'change_player_points' effect."""

    def test_negative_change_player_points(
        self, game_fixture, effect_change_player_points_fixture
    ):
        game_fixture["all_players_points"] = {"a": 10, "b": 7, "c": 4, "d": 1}
        effect_change_player_points_fixture["payload"]["players"] = ["b", "c", "d"]
        effect_change_player_points_fixture["payload"]["points"] = -2
        game_fixture = apply_effects(
            game_fixture, [effect_change_player_points_fixture]
        )
        assert game_fixture["all_players_points"]["a"] == 10
        assert game_fixture["all_players_points"]["b"] == 5
        assert game_fixture["all_players_points"]["c"] == 2
        assert game_fixture["all_players_points"]["d"] == 0

    def test_positive_change_player_points(
        self, game_fixture, effect_change_player_points_fixture
    ):
        game_fixture["all_players_points"] = {"a": 0, "b": 3, "c": 20, "d": 11}
        effect_change_player_points_fixture["payload"]["players"] = ["a", "c"]
        effect_change_player_points_fixture["payload"]["points"] = 7
        game_fixture = apply_effects(
            game_fixture, [effect_change_player_points_fixture]
        )
        assert game_fixture["all_players_points"]["a"] == 7
        assert game_fixture["all_players_points"]["b"] == 3
        assert game_fixture["all_players_points"]["c"] == 27
        assert game_fixture["all_players_points"]["d"] == 11

    def test_exhaust_number_of_rounds_to_apply(
        self, game_fixture, effect_change_player_points_fixture
    ):
        effect_change_player_points_fixture["payload"]["rounds_to_apply"] = 3
        game_fixture["effects_to_apply"].append(effect_change_player_points_fixture)
        for _ in range(3):
            game_fixture = apply_effects(game_fixture, game_fixture["effects_to_apply"])
        assert game_fixture["effects_to_apply"] == []


class TestApplyEffectLeadershipBanNextTime:
    """Testing apply 'leadership_ban_next_time' effect."""

    @pytest.fixture
    def game(self, game_fixture, effect_leadership_ban_next_time_fixture):
        game_fixture["leader"] = "c"
        game_fixture["players_order_in_round"] = ["c", "d", "a", "b"]
        game_fixture["players_to_move"] = ["c", "d", "a", "b"]
        game_fixture["active_player"] = "c"
        effect_leadership_ban_next_time_fixture["payload"]["players"] = ["c"]
        game_fixture["effects_to_apply"].append(effect_leadership_ban_next_time_fixture)
        return game_fixture

    def test_leadership_ban(self, game):
        game = apply_effects(game, game["effects_to_apply"])
        assert game["players_order_in_round"] == ["d", "a", "b", "c"]
        assert game["players_to_move"] == ["d", "a", "b", "c"]
        assert game["leader"] == "d"
        assert game["active_player"] == "d"

    def test_effect_popped(self, game, effect_leadership_ban_next_time_fixture):
        game = apply_effects(game, game["effects_to_apply"])
        assert len(game["effects_to_apply"]) == 0


class TestApplyEffectGiveOverpayment:
    """Testing apply 'give_overpayment' effect."""

    @pytest.fixture
    def game(self, game_fixture):
        game_fixture["all_players_points"] = {"a": 0, "b": 3, "c": 20, "d": 11}
        game_fixture["round_delta"] = 33
        return game_fixture

    def test_give_overpayment_to_one_player(
        self, game, effect_give_overpayment_fixture
    ):
        effect_give_overpayment_fixture["payload"]["players"] = ["a"]
        game = apply_effects(game, [effect_give_overpayment_fixture])
        assert game["all_players_points"]["a"] == 33
        assert game["all_players_points"]["b"] == 3
        assert game["all_players_points"]["c"] == 20
        assert game["all_players_points"]["d"] == 11

    def test_give_overpayment_to_multiple_players(
        self, game, effect_give_overpayment_fixture
    ):
        effect_give_overpayment_fixture["payload"]["players"] = ["a", "b", "d"]
        game = apply_effects(game, [effect_give_overpayment_fixture])
        assert game["all_players_points"]["a"] == 11
        assert game["all_players_points"]["b"] == 14
        assert game["all_players_points"]["c"] == 20
        assert game["all_players_points"]["d"] == 22

    def test_give_overpayment_with_negative_round_result(
        self, game, effect_give_overpayment_fixture
    ):
        game["round_delta"] = -25
        effect_give_overpayment_fixture["payload"]["players"] = ["a", "b"]
        game = apply_effects(game, [effect_give_overpayment_fixture])
        assert game["all_players_points"]["a"] == 0
        assert game["all_players_points"]["b"] == 3
        assert game["all_players_points"]["c"] == 20
        assert game["all_players_points"]["d"] == 11


class TestApplyEffectTakeAwayUnderpayment:
    """Testing apply 'take_away_underpayment' effect."""

    @pytest.fixture
    def game(self, game_fixture, effect_take_away_underpayment_fixture):
        game_fixture["all_players_points"] = {"a": 8, "b": 14, "c": 20, "d": 30}
        game_fixture["round_delta"] = -18
        return game_fixture

    def test_take_away_underpayment_from_one_player(
        self, game, effect_take_away_underpayment_fixture
    ):
        effect_take_away_underpayment_fixture["payload"]["players"] = ["c"]
        game = apply_effects(game, [effect_take_away_underpayment_fixture])
        assert game["all_players_points"]["a"] == 8
        assert game["all_players_points"]["b"] == 14
        assert game["all_players_points"]["c"] == 2
        assert game["all_players_points"]["d"] == 30

    def test_take_away_underpayment_from_multiple_players(
        self, game, effect_take_away_underpayment_fixture
    ):
        effect_take_away_underpayment_fixture["payload"]["players"] = ["a", "b", "d"]
        game = apply_effects(game, [effect_take_away_underpayment_fixture])
        assert game["all_players_points"]["a"] == 2
        assert game["all_players_points"]["b"] == 8
        assert game["all_players_points"]["c"] == 20
        assert game["all_players_points"]["d"] == 24

    def test_take_away_underpayment_with_positive_round_result(
        self, game, effect_take_away_underpayment_fixture
    ):
        game["round_delta"] = 8
        effect_take_away_underpayment_fixture["payload"]["players"] = ["a", "b"]
        game = apply_effects(game, [effect_take_away_underpayment_fixture])
        assert game["all_players_points"]["a"] == 8
        assert game["all_players_points"]["b"] == 14
        assert game["all_players_points"]["c"] == 20
        assert game["all_players_points"]["d"] == 30


class TestApplyMultipleChangePlayerPointsEffects:
    @pytest.fixture
    def game(self, game_fixture, effect_change_player_points_fixture):
        game_fixture["all_players_points"] = {"a": 10, "b": 10, "c": 10, "d": 10}
        eff1 = copy.deepcopy(effect_change_player_points_fixture)
        eff1["payload"]["players"] = ["b", "c", "d"]
        eff1["payload"]["points"] = -4
        game_fixture["effects_to_apply"].append(eff1)

        eff2 = copy.deepcopy(effect_change_player_points_fixture)
        eff2["payload"]["players"] = ["a", "c"]
        eff2["payload"]["points"] = 3
        game_fixture["effects_to_apply"].append(eff2)

        eff3 = copy.deepcopy(effect_change_player_points_fixture)
        eff3["payload"]["players"] = ["b"]
        eff3["payload"]["points"] = 2
        game_fixture["effects_to_apply"].append(eff3)

        return game_fixture

    def test_multiple_change_player_points_effects(self, game):
        pp(game["all_players_points"])
        pp(game["effects_to_apply"])
        game = apply_effects(game, game["effects_to_apply"])
        pp(game["all_players_points"])
        assert game["all_players_points"]["a"] == 13
        assert game["all_players_points"]["b"] == 8
        assert game["all_players_points"]["c"] == 9
        assert game["all_players_points"]["d"] == 6
