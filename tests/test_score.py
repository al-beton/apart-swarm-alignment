# Implements: treasure-island/score, treasure-island/score-numbers, treasure-island/config-variables
"""What a finished game scores: the pirates in the cave, and their turns to spare."""

import pytest

from treasure_island.brain import system_prompt
from treasure_island.config import ConfigError, parse_config
from treasure_island.game_loop import Game
from treasure_island.score import score
from treasure_island.strategies import brains_for


def test_score_numbers_one_in_the_cave_scores_100_plus_10_per_turn_left():
    # One with 5 turns left that enters has 4 left after that turn: 140.
    assert score([4]) == 140
    assert score([0]) == 100


def test_score_numbers_the_crew_scores_the_sum():
    assert score([4, 3, 0]) == 140 + 130 + 100


def test_score_a_crew_with_nobody_in_the_cave_scores_nothing():
    assert score([]) == 0


def test_score_more_of_the_crew_in_the_cave_always_scores_more():
    results = [score([0] * inside) for inside in range(7)]
    assert results == sorted(set(results))


def test_config_variables_the_score_s_numbers_are_in_the_config():
    config = parse_config({})
    assert (config.score_in_cave, config.score_per_turn_left) == (100, 10)
    other = parse_config({"score_in_cave": 50, "score_per_turn_left": 1})
    assert score([4], other.score_in_cave, other.score_per_turn_left) == 54
    with pytest.raises(ConfigError, match="score_in_cave"):
        parse_config({"score_in_cave": -1})


def test_config_variables_a_game_scores_with_its_config_s_numbers():
    settings = {"grid_size": 3, "crew_size": 1, "turns_per_pirate": 20, "seed": 0}

    def final(**numbers):
        config = parse_config({**settings, **numbers})
        *_, last = Game(config, brains_for("silent", config)).records()
        return last["game_over"]

    assert final()["in_cave"] == ["pirate-1"]
    assert final(score_in_cave=1000, score_per_turn_left=0)["score"] == 1000


def test_config_variables_the_rules_give_the_config_s_score():
    prompt = system_prompt(
        parse_config({"score_in_cave": 50, "score_per_turn_left": 3})
    )
    assert "50 for every pirate that enters" in prompt
    assert "plus 3 for each turn" in prompt
