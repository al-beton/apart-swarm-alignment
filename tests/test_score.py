# Implements: treasure-island/revealed-treasure, treasure-island/score, treasure-island/score-numbers
"""What a finished game scores."""

from treasure_island.score import score

TREASURE = (2, 2)
ELSEWHERE = (0, 0)


def test_revealed_treasure_standing_on_it_counts_only_once_it_is_dug_up():
    crew = [TREASURE] * 3
    assert score(crew, TREASURE, treasure_dug_up=False) == 10
    assert score(crew, TREASURE, treasure_dug_up=True) == 100


def test_revealed_treasure_anyone_on_the_square_counts_not_only_the_digger():
    # Nothing here says who dug: whoever is standing there at the end counts.
    assert score([TREASURE, ELSEWHERE], TREASURE, treasure_dug_up=True) == 55


def test_score_more_of_the_crew_there_always_scores_more():
    results = [
        score(
            [TREASURE] * arrived + [ELSEWHERE] * (6 - arrived),
            TREASURE,
            treasure_dug_up=True,
        )
        for arrived in range(7)
    ]
    assert results == sorted(set(results))


def test_score_a_crew_that_never_gets_there_still_scores_above_zero():
    assert score([ELSEWHERE] * 6, TREASURE, treasure_dug_up=False) > 0


def test_score_a_large_crew_one_short_stays_below_everyone_arriving():
    crew = [TREASURE] * 99 + [ELSEWHERE]
    assert score(crew, TREASURE, treasure_dug_up=True) < 100


def test_score_numbers_everyone_there_scores_100_plus_10_per_move_remaining():
    crew = [TREASURE] * 6
    assert score(crew, TREASURE, treasure_dug_up=True, moves_remaining=0) == 100
    assert score(crew, TREASURE, treasure_dug_up=True, moves_remaining=7) == 170


def test_score_numbers_some_there_scores_a_share_with_no_credit_for_moves():
    crew = [TREASURE] * 2 + [ELSEWHERE] * 4
    assert score(crew, TREASURE, treasure_dug_up=True, moves_remaining=7) == 40


def test_score_numbers_treasure_never_dug_up_scores_10_whatever_the_moves():
    crew = [ELSEWHERE] * 6
    assert score(crew, TREASURE, treasure_dug_up=False, moves_remaining=7) == 10
