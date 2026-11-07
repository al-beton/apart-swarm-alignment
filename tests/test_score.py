# Implements: treasure-island/score, treasure-island/score-numbers
"""What a finished game scores: the pirates in the cave, and their turns to spare."""

from treasure_island.score import score


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
