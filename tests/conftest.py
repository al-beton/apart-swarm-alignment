# Implements: treasure-island/grid-and-crew
"""Shared test setup.

`left_edge_starts` stands a crew one below the next from the top-left corner,
the first squares of `rings`, instead of spreading it round the edge from a
square the seed picks (`grid-and-crew`). Tests of the other rules were written
for pirates standing there, so they ask for it and test their own rule.
"""

import pytest

from treasure_island import game_state


def down_the_left_edge(size, crew_size, treasure, offset):
    return game_state.rings(size)[:crew_size]


@pytest.fixture
def left_edge_starts(monkeypatch):
    monkeypatch.setattr(game_state, "starting_squares", down_the_left_edge)
