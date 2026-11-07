"""What a finished game scores: one pure function of plain values.

Each pirate in the cave scores `in_cave` plus `per_turn_left` for every turn it
had left after the turn it went in on, a pirate that never gets in scores 0, and
the crew scores the sum. The numbers are the config's `score_in_cave` and
`score_per_turn_left` (default 100 and 10). Only the game knows each pirate's
turns left, so it passes them in.

Implements: treasure-island/score, treasure-island/score-numbers, treasure-island/config-variables
"""


def score(turns_left_in_cave, in_cave=100, per_turn_left=10):
    """The crew's score, from the turns each pirate in the cave had left."""
    return sum(in_cave + per_turn_left * left for left in turns_left_in_cave)
