"""What a finished game scores: one pure function of plain values.

Each pirate in the cave scores `IN_CAVE` plus `PER_TURN_LEFT` for every turn it
had left after the turn it went in on, a pirate that never gets in scores 0, and
the crew scores the sum. Only the game knows each pirate's turns left, so it
passes them in.

Implements: treasure-island/score, treasure-island/score-numbers
"""

IN_CAVE = 100
PER_TURN_LEFT = 10


def score(turns_left_in_cave):
    """The crew's score, from the turns each pirate in the cave had left."""
    return sum(IN_CAVE + PER_TURN_LEFT * left for left in turns_left_in_cave)
