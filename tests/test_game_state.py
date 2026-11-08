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


def edge_of(size):
    """The edge squares in order from the top-left corner: down, along, up, along."""
    return (
        [(0, y) for y in range(size)]
        + [(x, size - 1) for x in range(1, size)]
        + [(size - 1, y) for y in range(size - 2, -1, -1)]
        + [(x, 0) for x in range(size - 2, 0, -1)]
    )


def test_grid_and_crew_pirates_start_spread_evenly_around_the_edge():
    for seed in range(50):
        state = game(grid_size=12, crew_size=6, seed=seed)
        edge = [square for square in edge_of(12) if square != state.treasure]
        places = [edge.index(square) for square in state.positions]
        after = places[1:] + places[:1]
        gaps = [(b - a) % len(edge) for a, b in zip(places, after, strict=True)]
        assert min(gaps) >= len(edge) // 6, (seed, gaps)
        assert max(gaps) <= len(edge) // 6 + 1, (seed, gaps)


def test_grid_and_crew_the_seed_picks_where_pirate_1_starts():
    firsts = {
        game(grid_size=12, crew_size=6, seed=seed).positions[0] for seed in range(50)
    }
    assert len(firsts) > 10
    assert (
        game(grid_size=12, crew_size=6, seed=4).positions
        == game(grid_size=12, crew_size=6, seed=4).positions
    )


def test_grid_and_crew_no_pirate_starts_on_the_treasure():
    for size, crew in [(6, 3), (3, 8), (4, 12), (12, 6)]:
        for seed in range(200):
            state = game(grid_size=size, crew_size=crew, seed=seed)
            assert state.treasure not in state.positions
            assert len(set(state.positions)) == crew


def test_grid_and_crew_a_crew_bigger_than_the_edge_fills_it_then_rings_further_in():
    for seed in range(20):
        state = game(grid_size=6, crew_size=22, seed=seed)
        edge = [square for square in edge_of(6) if square != state.treasure]
        assert set(edge) <= set(state.positions)
        inner = [square for square in state.positions if square not in edge]
        assert all(1 <= x <= 4 and 1 <= y <= 4 for x, y in inner)
        everyone = game(grid_size=6, crew_size=35, seed=seed)
        assert len(set(everyone.positions)) == 35
        assert everyone.treasure not in everyone.positions


def test_grid_and_crew_a_crew_bigger_than_the_grid_cannot_start():
    with pytest.raises(ValueError, match="9 pirates.*3 by 3"):
        game(grid_size=3, crew_size=9)


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
    state = game(crew_size=2, at=[(0, 0), (0, 1)])
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
    state = game(at=[(0, 0)])
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
    state = game(crew_size=2, at=[(0, 0), (0, 1)])
    state.step("east")
    assert (state.current_pirate, state.turn) == (1, 1)
    state.dig()
    assert (state.current_pirate, state.turn) == (0, 2)
    # The second pirate dug: the first hasn't moved again.
    assert state.positions == [(1, 0), (0, 1)]


def test_one_action_per_turn_an_action_elsewhere_still_ends_the_turn():
    state = game(crew_size=2, at=[(0, 0), (0, 1)])
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
