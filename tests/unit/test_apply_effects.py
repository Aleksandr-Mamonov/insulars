import pytest

from app.main import apply_effects


class TestChangePlayerPoints:
    def test_change_player_points(self, game_fixture, effects_fixture, room_id_fixture):
        game = apply_effects(
            game=game_fixture, effects=effects_fixture, room_id=room_id_fixture
        )
