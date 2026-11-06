# Implements: treasure-island/pirates-and-treasure, treasure-island/grid-and-crew, treasure-island/shared-squares, treasure-island/failed-move, treasure-island/failed-move-cost, treasure-island/actions, treasure-island/one-action-per-turn, treasure-island/turn-order
"""The game's rules, played directly with plain values."""

import pytest

from treasure_island.game_state import GameState


def game(grid_size=5, crew_size=1, landing_square=(2, 2), seed=0):
    return GameState(grid_size, crew_size, landing_square, seed)


def on_treasure(crew_size=1):
    """A game whose whole crew lands on the treasure."""
    treasure = game(seed=7).treasure
    return game(crew_size=crew_size, landing_square=treasure, seed=7)


def off_treasure(crew_size=1):
    """A game whose whole crew lands anywhere but the treasure."""
    x, y = game(seed=7).treasure
    return game(crew_size=crew_size, landing_square=((x + 1) % 5, y), seed=7)


def test_pirates_and_treasure_the_same_seed_places_it_on_the_same_square():
    assert game(seed=3).treasure == game(seed=3).treasure


def test_pirates_and_treasure_the_seed_decides_where_it_is():
    assert len({game(seed=seed).treasure for seed in range(50)}) > 1


def test_pirates_and_treasure_it_is_always_on_the_grid():
    for seed in range(200):
        x, y = game(grid_size=4, landing_square=(0, 0), seed=seed).treasure
        assert 0 <= x < 4 and 0 <= y < 4


def test_grid_and_crew_every_pirate_lands_on_the_same_square():
    assert game(crew_size=3).positions == [(2, 2), (2, 2), (2, 2)]


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
    state = game()
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
    state.move("north")
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
    answer = state.move("north")
    assert answer.found_treasure is False
    assert "treasure" not in answer.message.lower()


def test_shared_squares_any_number_of_pirates_can_stand_together():
    state = game(crew_size=20)
    for _ in range(20):
        assert state.move("north").ok is True
    assert state.positions == [(2, 1)] * 20


@pytest.mark.parametrize(
    "landing,direction",
    [
        ((0, 2), "west"),
        ((4, 2), "east"),
        ((2, 0), "north"),
        ((2, 4), "south"),
    ],
)
def test_failed_move_off_any_edge_fails_and_says_why(landing, direction):
    state = game(landing_square=landing)
    result = state.move(direction)
    assert result.ok is False
    assert direction in result.message
    assert "edge" in result.message
    assert state.positions == [landing]


def test_failed_move_an_unknown_direction_fails_and_says_why():
    state = game()
    result = state.move("sideways")
    assert result.ok is False
    assert "sideways" in result.message
    assert state.positions == [(2, 2)]


def test_failed_move_cost_it_costs_the_turn():
    state = game(crew_size=2, landing_square=(0, 0))
    assert state.move("west").ok is False
    assert state.current_pirate == 1
    assert state.turn == 1


def test_one_action_per_turn_each_action_ends_the_turn():
    state = game(crew_size=2)
    state.move("north")
    assert (state.current_pirate, state.turn) == (1, 1)
    state.dig()
    assert (state.current_pirate, state.turn) == (0, 2)
    # The second pirate dug: the first hasn't moved again.
    assert state.positions == [(2, 1), (2, 2)]


def test_turn_order_is_fixed_and_comes_round_again():
    state = game(crew_size=3)
    order = []
    for _ in range(7):
        order.append(state.current_pirate)
        state.dig()
    assert order == [0, 1, 2, 0, 1, 2, 0]
