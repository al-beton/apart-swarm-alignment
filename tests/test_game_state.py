# Implements: treasure-island/pirates-and-treasure, treasure-island/grid-and-crew, treasure-island/shared-squares, treasure-island/failed-move, treasure-island/failed-move-cost, treasure-island/actions, treasure-island/one-action-per-turn, treasure-island/turn-order, treasure-island/go-to, treasure-island/wait
"""The game's rules, played directly with plain values."""

import pytest

from treasure_island.game_state import CAVE_HERE, GameState, first_step


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
def test_go_to_a_step_goes_one_square_in_any_of_four_directions(direction, expected):
    state = game(at=[(2, 2)])
    assert state.step(direction).ok is True
    assert state.positions == [expected]


@pytest.mark.parametrize(
    "here,there,way",
    [
        ((0, 0), (3, 3), "east"),
        ((3, 0), (0, 3), "west"),
        ((2, 4), (2, 0), "north"),
        ((2, 0), (2, 4), "south"),
    ],
)
def test_go_to_steps_along_the_row_first_then_the_column(here, there, way):
    assert first_step(here, there) == way


def test_actions_digging_says_nothing_found_off_the_treasure():
    result = off_treasure().dig()
    assert (result.ok, result.found_treasure) == (True, False)
    assert result.reading is not None


def test_actions_digging_says_treasure_on_the_treasure():
    state = on_treasure()
    result = state.dig()
    assert (result.ok, result.found_treasure) == (True, True)
    assert state.treasure_dug_up is True


def test_actions_a_dug_up_treasure_stays_dug_up():
    state = on_treasure(crew_size=2)
    state.dig()
    state.wait()
    assert state.treasure_dug_up is True
    again = state.dig()  # digging the open cave says so, and finds nothing new
    assert (again.found_treasure, again.message) == (False, CAVE_HERE)
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
    answer = state.wait()
    assert answer.found_treasure is False
    assert "treasure" not in answer.message.lower()


def test_wait_keeps_the_pirate_where_it_is_and_ends_its_turn():
    state = game(crew_size=2)
    result = state.wait()
    assert result.ok is True
    assert result.message == "You waited at A5."
    assert state.positions == [(0, 0), (0, 1)]
    assert (state.current_pirate, state.turn) == (1, 1)


@pytest.mark.parametrize("direction", ["north", "east", "south", "west"])
def test_shared_squares_a_go_to_onto_another_pirate_is_refused_and_says_who(direction):
    x, y = {"north": (2, 1), "east": (3, 2), "south": (2, 3), "west": (1, 2)}[direction]
    far = {"north": "C5", "east": "E3", "south": "C1", "west": "A3"}[direction]
    state = game(crew_size=2, at=[(2, 2), (x, y)])
    result = state.go_to_refusal(far)
    assert result.ok is False
    assert result.blocked_by == 1
    assert direction in result.message
    assert "pirate-2" in result.message
    assert state.positions == [(2, 2), (x, y)]


def test_shared_squares_a_square_a_pirate_left_is_free_again():
    state = game(crew_size=2, at=[(0, 0), (0, 1)])
    state.step("east")
    assert state.step("north").ok is True
    assert state.positions == [(1, 0), (0, 0)]


def test_shared_squares_a_step_onto_a_pirate_is_never_taken():
    state = game(crew_size=2, at=[(0, 0), (0, 1)])
    with pytest.raises(ValueError):
        state.step("south")
    assert state.positions == [(0, 0), (0, 1)]


@pytest.mark.parametrize(
    "name,says",
    [
        ("A5", "already at A5"),
        ("F2", "no square F2 on the island"),
        ("A9", "no square A9 on the island"),
        ("sideways", "isn't a square's name"),
        ("", "isn't a square's name"),
    ],
)
def test_failed_move_a_go_to_that_cannot_happen_fails_and_says_why(name, says):
    state = game()
    result = state.go_to_refusal(name)
    assert result.ok is False
    assert says in result.message
    assert state.positions == [(0, 0)]
    assert (state.current_pirate, state.turn) == (0, 0)


def test_failed_move_a_go_to_anywhere_free_is_not_refused():
    state = game(crew_size=2, at=[(0, 0), (4, 4)])
    assert state.go_to_refusal("E1") is None
    assert state.go_to_refusal("b5") is None


def test_one_action_per_turn_each_action_ends_the_turn():
    state = game(crew_size=2)
    state.step("east")
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
