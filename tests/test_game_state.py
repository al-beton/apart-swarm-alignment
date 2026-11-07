# Implements: treasure-island/pirates-and-treasure, treasure-island/grid-and-crew, treasure-island/shared-squares, treasure-island/failed-move, treasure-island/failed-move-cost, treasure-island/actions, treasure-island/one-action-per-turn, treasure-island/turn-order
"""The game's rules, played directly with plain values."""

import pytest

from treasure_island.game_state import GameState


def game(grid_size=5, crew_size=1, seed=0, at=None):
    """A game, with its crew moved to the squares `at` if given."""
    state = GameState(grid_size, crew_size, seed)
    if at is not None:
        state.positions = list(at)
    return state


def on_treasure(crew_size=1):
    """A game whose first pirate stands on the treasure, the rest beside it."""
    x, y = game(seed=7).treasure
    rest = [((x + step) % 5, (y + 1) % 5) for step in range(crew_size - 1)]
    return game(crew_size=crew_size, seed=7, at=[(x, y), *rest])


def off_treasure(crew_size=1):
    """A game whose first pirate stands anywhere but the treasure."""
    x, y = game(seed=7).treasure
    return game(crew_size=crew_size, seed=7, at=[((x + 1) % 5, y)])


def test_pirates_and_treasure_the_same_seed_places_it_on_the_same_square():
    assert game(seed=3).treasure == game(seed=3).treasure


def test_pirates_and_treasure_the_seed_decides_where_it_is():
    assert len({game(seed=seed).treasure for seed in range(50)}) > 1


def test_pirates_and_treasure_it_is_always_on_the_grid():
    for seed in range(200):
        x, y = game(grid_size=4, seed=seed).treasure
        assert 0 <= x < 4 and 0 <= y < 4


def test_grid_and_crew_each_pirate_starts_one_below_the_last_down_the_left_edge():
    assert game(crew_size=3).positions == [(0, 0), (0, 1), (0, 2)]


def test_grid_and_crew_a_crew_longer_than_the_edge_carries_on_round_it():
    # Down the left edge, along the bottom, up the right side, along the top.
    edge = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)]
    assert game(grid_size=3, crew_size=8).positions == edge


def test_grid_and_crew_then_spirals_inward_onto_every_square():
    assert game(grid_size=3, crew_size=9).positions[-1] == (1, 1)
    squares = game(grid_size=6, crew_size=36).positions
    assert sorted(squares) == [(x, y) for x in range(6) for y in range(6)]
    assert squares[20:24] == [(1, 1), (1, 2), (1, 3), (1, 4)]


def test_grid_and_crew_a_crew_bigger_than_the_grid_cannot_start():
    with pytest.raises(ValueError, match="10 pirates.*3 by 3"):
        game(grid_size=3, crew_size=10)


@pytest.mark.parametrize(
    "direction,expected",
    [
        ("north", (2, 1)),
        ("east", (3, 2)),
        ("south", (2, 3)),
        ("west", (1, 2)),
    ],
)
def test_actions_a_move_goes_one_square_in_any_of_four_directions(direction, expected):
    state = game(at=[(2, 2)])
    assert state.move(direction).ok is True
    assert state.positions == [expected]


def test_actions_digging_says_nothing_found_off_the_treasure():
    result = off_treasure().dig()
    assert (result.ok, result.found_treasure) == (True, False)


def test_actions_digging_says_treasure_on_the_treasure():
    state = on_treasure()
    result = state.dig()
    assert (result.ok, result.found_treasure) == (True, True)
    assert state.treasure_dug_up is True


def test_actions_a_dug_up_treasure_stays_dug_up():
    state = on_treasure(crew_size=2)
    state.dig()
    state.move("east")
    assert state.treasure_dug_up is True
    assert state.dig().found_treasure is True
    assert state.treasure_dug_up is True


def test_actions_digging_elsewhere_digs_nothing_up():
    state = off_treasure()
    state.dig()
    assert state.treasure_dug_up is False


def test_actions_a_dig_reports_only_to_the_pirate_that_dug():
    # What one pirate learns comes back to it alone: nothing about the others'
    # results is kept where another pirate's turn could read it.
    state = on_treasure(crew_size=2)
    assert state.dig().found_treasure is True
    answer = state.move("east")
    assert answer.found_treasure is False
    assert "treasure" not in answer.message.lower()


@pytest.mark.parametrize("direction", ["north", "east", "south", "west"])
def test_shared_squares_a_move_onto_another_pirate_is_refused_and_says_who(direction):
    x, y = {"north": (2, 1), "east": (3, 2), "south": (2, 3), "west": (1, 2)}[direction]
    state = game(crew_size=2, at=[(2, 2), (x, y)])
    result = state.move(direction)
    assert result.ok is False
    assert result.blocked_by == 1
    assert direction in result.message
    assert "pirate" in result.message
    assert state.positions == [(2, 2), (x, y)]


def test_shared_squares_a_square_a_pirate_left_is_free_again():
    state = game(crew_size=2, at=[(0, 0), (0, 1)])
    state.move("east")
    assert state.move("north").ok is True
    assert state.positions == [(1, 0), (0, 0)]


def test_shared_squares_no_two_pirates_ever_stand_together():
    state = game(grid_size=3, crew_size=8)
    for direction in ["east", "north", "west", "south"] * 20:
        state.move(direction)
        assert len(set(state.positions)) == 8


@pytest.mark.parametrize(
    "square,direction",
    [
        ((0, 2), "west"),
        ((4, 2), "east"),
        ((2, 0), "north"),
        ((2, 4), "south"),
    ],
)
def test_failed_move_off_any_edge_fails_and_says_why(square, direction):
    state = game(at=[square])
    result = state.move(direction)
    assert result.ok is False
    assert direction in result.message
    assert "edge" in result.message
    assert state.positions == [square]


def test_failed_move_an_unknown_direction_fails_and_says_why():
    state = game()
    result = state.move("sideways")
    assert result.ok is False
    assert "sideways" in result.message
    assert state.positions == [(0, 0)]


@pytest.mark.parametrize("direction", ["west", "south"])
def test_failed_move_cost_a_failed_move_leaves_the_turn_with_the_pirate(direction):
    # West is off the edge; south is onto pirate 2.
    state = game(crew_size=2, at=[(0, 0), (0, 1)])
    assert state.move(direction).ok is False
    assert (state.current_pirate, state.turn) == (0, 0)
    assert state.move("east").ok is True
    assert state.positions == [(1, 0), (0, 1)]


def test_one_action_per_turn_each_action_ends_the_turn():
    state = game(crew_size=2)
    state.move("east")
    assert (state.current_pirate, state.turn) == (1, 1)
    state.dig()
    assert (state.current_pirate, state.turn) == (0, 2)
    # The second pirate dug: the first hasn't moved again.
    assert state.positions == [(1, 0), (0, 1)]


def test_one_action_per_turn_an_action_elsewhere_still_ends_the_turn():
    state = game(crew_size=2)
    state.pass_turn()
    assert (state.current_pirate, state.turn) == (1, 1)
    assert state.positions == [(0, 0), (0, 1)]


def test_turn_order_is_fixed_and_comes_round_again():
    state = game(crew_size=3)
    order = []
    for _ in range(7):
        order.append(state.current_pirate)
        state.dig()
    assert order == [0, 1, 2, 0, 1, 2, 0]
