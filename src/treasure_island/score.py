"""What a finished game scores: one pure function of plain values.

The numbers are `treasure-island/score-numbers`, default, Al to confirm. Only the
caller can know `moves_remaining`, the turns left to the pirate who got there
last, so it's passed in; it only counts when the whole crew is on the treasure.

Implements: treasure-island/revealed-treasure, treasure-island/score, treasure-island/score-numbers
"""

EVERYONE_THERE = 100
PER_MOVE_REMAINING = 10
NOBODY_THERE = 10
_SHARE = EVERYONE_THERE - NOBODY_THERE


def score(positions, treasure, treasure_dug_up, moves_remaining=0):
    """The crew's score, from where each pirate stands at the end of the game."""
    crew = len(positions)
    there = sum(tuple(p) == tuple(treasure) for p in positions)
    if not treasure_dug_up or there == 0:
        return NOBODY_THERE
    if there == crew:
        return EVERYONE_THERE + PER_MOVE_REMAINING * moves_remaining
    return NOBODY_THERE + _SHARE * there // crew
