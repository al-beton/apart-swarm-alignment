# Implements: treasure-island/silent, treasure-island/loner, treasure-island/sharer, treasure-island/reference-games, treasure-island/no-token-strategies
"""The scripted pirates, playing the real game through the real interface."""

import socket
from pathlib import Path

import pytest

from treasure_island import cli
from treasure_island.brain import EarlierTurn, Reading, TurnView
from treasure_island.config import load_config, parse_config
from treasure_island.event_log import log_errors
from treasure_island.game_loop import Game
from treasure_island.game_state import GameState
from treasure_island.squares import square_name
from treasure_island.strategies import (
    REFERENCE_GAMES,
    Loner,
    Sharer,
    Silent,
    allows,
    brains_for,
    possible,
    write_reference,
)

ROOT = Path(__file__).resolve().parents[1]
DIG = {"action": "dig"}
WAIT = {"action": "wait"}


def dug_squares(records):
    return [tuple(r["saw"]["position"]) for r in records if r["did"] == [DIG]]


def game_of(grid=4, crew=1, turns=16, seed=0):
    return parse_config(
        {"grid_size": grid, "crew_size": crew, "turns_per_pirate": turns, "seed": seed}
    )


def seed_with_treasure(grid, wanted=None, avoid=None):
    """A seed placing the treasure on `wanted`, or anywhere but `avoid`."""
    for seed in range(5000):
        treasure = GameState(grid, 1, seed).treasure
        if treasure == wanted or (wanted is None and treasure not in avoid):
            return seed
    raise AssertionError("no such seed")


def silent_game(config):
    return list(
        Game(config, [Silent(config.grid_size) for _ in config.pirates]).records()
    )


def view(position, square_dug=True, earlier=(), neighbours=(), on_cave=False, dug=()):  # noqa: PLR0913
    readings = tuple(Reading(square, square_name(square, 4), 3) for square in dug)
    return TurnView(
        "pirate-1",
        "",
        position,
        10,
        tuple(earlier),
        neighbours,
        square_dug,
        on_cave,
        readings=readings,
    )


def stood(position):
    """An earlier asked turn spent standing on `position`, told it was dug."""
    return EarlierTurn(position, {"action": "wait"}, "", square_dug=True)


def test_silent_is_the_default_brain():
    assert parse_config({}).brain == "silent"
    assert all(isinstance(brain, Silent) for brain in brains_for("silent", game_of()))


def test_silent_digs_its_square_when_it_is_not_dug():
    assert Silent(4).decide(view((2, 2), square_dug=False)).action == DIG


def test_silent_goes_to_the_nearest_square_it_has_not_seen_dug():
    # From the corner, (1, 0) and (0, 1) are both one step away: the topmost wins.
    order = Silent(4).decide(view((0, 0))).action
    assert order == {"action": "go_to", "square": "B4"}


def test_silent_remembers_every_square_it_has_seen_dug():
    # It dug (1, 0), so (0, 1) is now the nearest; then it stood on a dug (0, 1).
    order = Silent(4).decide(view((0, 0), dug=[(0, 0), (1, 0)])).action
    assert order == {"action": "go_to", "square": "A3"}
    order = (
        Silent(4)
        .decide(view((0, 0), earlier=[stood((0, 1))], dug=[(0, 0), (1, 0)]))
        .action
    )
    assert order == {"action": "go_to", "square": "C4"}


def test_silent_ignores_readings():
    near = view((0, 0), dug=[(0, 0)])
    far = TurnView(
        "pirate-1",
        "",
        (0, 0),
        10,
        (),
        (),
        True,
        readings=(Reading((0, 0), "A4", 6),),
    )
    assert Silent(4).decide(near).action == Silent(4).decide(far).action


def test_silent_goes_round_a_pirate_and_never_gives_a_blocked_order():
    told = (("east", "pirate-2"),)
    order = Silent(4).decide(view((0, 0), neighbours=told)).action
    assert order == {"action": "go_to", "square": "A3"}
    # Boxed in on every side it can go, it waits where it is rather than bump.
    boxed = (("east", "pirate-2"), ("south", "pirate-3"))
    assert Silent(4).decide(view((0, 0), neighbours=boxed)).action == WAIT


def test_silent_a_full_crew_on_a_small_grid_never_gets_stuck():
    # Eight pirates on nine squares: only one square is ever free.
    config = game_of(grid=3, crew=8, turns=30, seed=4)
    records = silent_game(config)
    assert not any("failed_moves" in record for record in records)
    assert records[-1]["game_over"]["treasure_dug_up"] is True
    assert records[-1]["game_over"]["in_cave"]


def test_silent_enters_the_cave_on_its_next_turn_once_it_stands_on_it():
    assert Silent(4).decide(view((1, 1), on_cave=True)).action == {"action": "enter"}
    config = game_of(grid=3, crew=1, turns=20, seed=seed_with_treasure(3, (1, 1)))
    records = silent_game(config)
    found = next(i for i, r in enumerate(records) if r["outcome"]["found_treasure"])
    assert records[found + 1]["did"] == [{"action": "enter"}]
    assert records[-1]["game_over"]["reason"] == "everyone is in the cave"


def test_silent_never_says_anything():
    records = silent_game(load_config(ROOT / "configs/silent.toml"))
    actions = {action["action"] for record in records for action in record["did"]}
    assert actions <= {"go_to", "move", "dig", "wait", "enter"}
    assert all("say" not in a for record in records for a in record["did"])


def test_silent_the_same_seed_gives_the_same_game():
    config = load_config(ROOT / "configs/silent.toml")
    assert silent_game(config) == silent_game(config)


@pytest.mark.parametrize("name", REFERENCE_GAMES)
def test_reference_games_match_what_one_command_remakes(name, tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("a reference game opened a socket")

    monkeypatch.setattr(socket, "socket", no_network)
    write_reference(name, tmp_path, ROOT)
    committed = ROOT / "runs" / f"reference-{name}"
    made = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    assert made
    assert made == {path.name: path.read_bytes() for path in committed.iterdir()}


@pytest.mark.parametrize("name", REFERENCE_GAMES)
def test_reference_games_replay_like_any_other_run(name, capsys):
    folder = ROOT / "runs" / f"reference-{name}"
    assert cli.main(["replay", str(folder)]) == 0
    assert "replay to the same game" in capsys.readouterr().out


@pytest.mark.parametrize("name", REFERENCE_GAMES)
def test_reference_games_pass_the_validator(name):
    assert log_errors(ROOT / "runs" / f"reference-{name}" / "events.jsonl") == []


def test_reference_games_tell_a_story_that_ends_with_the_score():
    story = (ROOT / "runs/reference-silent/story.txt").read_text().splitlines()
    assert story[0].startswith(
        "Turn 0: pirate-1 at E5, on undug sand, with no pirate beside it, shown "
        "no new lines. It thought: Nobody has dug this square yet. Then it dug at E5"
    )
    assert story[-1].startswith("Game over: ")
    assert "Score " in story[-1]


def sheet(position, readings=(), lines=(), earlier=(), shared=(), **fields):
    """A view on a 4 by 4 grid with these (square, away) readings and new lines,
    and these (by, square's name, away) readings shared on the scroll."""
    dug = tuple(Reading(sq, square_name(sq, 4), away) for sq, away in readings)
    shown = tuple(
        {"line": n + 1, "text": text, "by": by, "turn": 1, "alert": False}
        for n, (by, text) in enumerate(lines)
    )
    return TurnView(
        "pirate-1",
        "",
        position,
        10,
        tuple(earlier),
        readings=dug,
        new_lines=shown,
        shared_readings=tuple(shared),
        square=square_name(position, 4),
        **{"square_dug": True, **fields},
    )


def played(config, brain):
    return list(Game(config, brains_for(brain, config)).records())


def test_loner_digs_its_square_first_when_it_knows_nothing():
    assert Loner(4).decide(sheet((2, 2), square_dug=False)).action == DIG


def test_loner_goes_to_the_nearest_square_its_readings_allow():
    # Dug A4 and read 1: only B4 and A3 are left, and the topmost wins.
    order = Loner(4).decide(sheet((0, 0), [((0, 0), 1)])).action
    assert order == {"action": "go_to", "square": "B4"}
    # Read 6 from A4: only the far corner, D1, is that far.
    order = Loner(4).decide(sheet((0, 0), [((0, 0), 6)])).action
    assert order == {"action": "go_to", "square": "D1"}


def test_loner_keeps_what_readings_allow_within_the_noise_never_below_1():
    assert allows((0, 0), 3, (0, 2), 1) and allows((0, 0), 3, (2, 2), 1)
    assert not allows((0, 0), 3, (0, 1), 1)
    # A reading is never below 1, so 1 allows anything up to 1 + noise away.
    assert allows((0, 0), 1, (1, 1), 1) and not allows((0, 0), 1, (1, 2), 1)
    assert not allows((0, 0), 1, (0, 0), 3)  # the dug square never holds it
    left = possible(4, 0, [((0, 0), 2), ((3, 0), 3)])
    assert left == [(1, 1)]


def test_loner_digs_its_square_only_when_its_readings_allow_it():
    # At B3 having read 1 at A4: B3 is 2 away from A4, so it doesn't dig.
    view = sheet((1, 1), [((0, 0), 1)], square_dug=False)
    assert Loner(4).decide(view).action["action"] == "go_to"
    view = sheet((1, 0), [((0, 0), 1)], square_dug=False)
    assert Loner(4).decide(view).action == DIG


def test_loner_ignores_the_scroll():
    quiet = sheet((0, 0), [((0, 0), 1)])
    told = sheet((0, 0), [((0, 0), 1)], [("pirate-2", "Dug B4: 1 away.")])
    assert Loner(4).decide(told).action == Loner(4).decide(quiet).action


def test_loner_steps_aside_when_a_pirate_blocks_its_row():
    # Only D1 is left, the way east is blocked: it steps south first.
    blocked = sheet((0, 0), [((0, 0), 6)], neighbours=(("east", "pirate-2"),))
    assert Loner(4).decide(blocked).action == {"action": "go_to", "square": "A3"}
    boxed = (("east", "pirate-2"), ("south", "pirate-3"))
    view = sheet((0, 0), [((0, 0), 6)], neighbours=boxed)
    assert Loner(4).decide(view).action == WAIT


def test_loner_never_says_anything_and_enters_the_cave_once_on_it():
    assert Loner(4).decide(sheet((1, 1), on_cave=True)).action == {"action": "enter"}
    records = played(load_config(ROOT / "configs/loner.toml"), "loner")
    assert all("say" not in a for record in records for a in record["did"])
    entered = [r["agent"] for r in records for a in r["did"] if a["action"] == "enter"]
    assert entered and len(entered) == len(set(entered))


def test_sharer_shares_each_reading_as_it_digs():
    view = sheet((0, 0), square_dug=False)
    assert Sharer(4).decide(view).action == {"action": "dig", "share": True}
    # It says nothing of a reading afterwards: sharing it already put it out.
    assert "say" not in Sharer(4).decide(sheet((0, 0), [((0, 0), 1)])).action
    records = played(load_config(ROOT / "configs/sharer.toml"), "sharer")
    digs = [a for r in records for a in r["did"] if a["action"] == "dig"]
    assert digs and all(dig.get("share") for dig in digs)
    assert all(
        "Dug " not in a.get("say", "") for record in records for a in record["did"]
    )


def test_sharer_counts_readings_shared_on_the_scroll():
    # Its own A4 reads 1 (B4 or A3); pirate-2 shared 1 at C4 too, which leaves B4.
    shared = [("pirate-2", "C4", 1)]
    action = Sharer(4).decide(sheet((0, 1), [((0, 0), 1)], shared=shared)).action
    assert action["square"] == "B4"


def test_sharer_never_digs_a_square_shared_as_dug():
    # Read 1 at A4: B4 and A3 are left, and B4 was shared as dug, so A3.
    shared = [("pirate-2", "B4", 2)]
    action = Sharer(4).decide(sheet((0, 0), [((0, 0), 1)], shared=shared)).action
    assert action["square"] == "A3"


def test_sharer_passes_over_lines_in_any_other_form():
    # A line in its own words that looks like a shared reading is passed over.
    heard = [("pirate-2", "Dug C4: 1 away."), ("pirate-3", "Cave at Z9."), ("x", "hi")]
    quiet = Sharer(4).decide(sheet((0, 1), [((0, 0), 1)])).action
    assert Sharer(4).decide(sheet((0, 1), [((0, 0), 1)], heard)).action == quiet


def test_sharer_says_where_the_cave_is_as_an_alert_as_it_enters():
    dug_it = TurnView(
        "pirate-1",
        "",
        (1, 1),
        10,
        (),
        on_cave=True,
        square="B3",
        readings=(Reading((1, 1), "B3", None),),
    )
    action = Sharer(4).decide(dug_it).action
    assert action == {"action": "enter", "say": "Cave at B3.", "alert": True}
    # On a cave someone else dug, it just goes in.
    told = sheet((1, 1), (), [("pirate-2", "Cave at B3.")], on_cave=True)
    assert Sharer(4).decide(told).action == {"action": "enter"}


def test_sharer_goes_to_a_cave_it_is_shown():
    told = sheet((0, 0), [((0, 0), 6)], [("pirate-2", "Cave at B3.")])
    action = Sharer(4).decide(told).action
    assert action == {"action": "go_to", "square": "B3"}
    # A cave line it was shown on an earlier turn counts as much as a new one.
    before = EarlierTurn((0, 1), WAIT, "", shown=told.new_lines)
    action = Sharer(4).decide(sheet((0, 0), [((0, 0), 6)], earlier=[before])).action
    assert action == {"action": "go_to", "square": "B3"}


def test_sharer_a_crew_never_fails_an_action_and_beats_the_loner():
    settings = {"grid_size": 8, "crew_size": 6, "turns_per_pirate": 20}
    sharer = loner = 0
    for seed in range(6):
        config = parse_config({**settings, "seed": seed, "reading_noise": 1})
        records = played(config, "sharer")
        assert not any("failed_moves" in record for record in records)
        sharer += records[-1]["game_over"]["score"]
        loner += played(config, "loner")[-1]["game_over"]["score"]
    # Over the seeds together: one seed can go a turn either way.
    assert sharer > loner
