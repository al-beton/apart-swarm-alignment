# Implements: treasure-island/silent, treasure-island/stripes, treasure-island/scribe, treasure-island/reference-games, treasure-island/no-token-strategies
"""The scripted pirates, playing the real game through the real interface."""

import socket
from pathlib import Path

import pytest

from treasure_island import cli
from treasure_island.brain import EarlierTurn, TurnView, tool_call
from treasure_island.config import load_config, parse_config
from treasure_island.event_log import log_errors
from treasure_island.game_loop import Game
from treasure_island.game_state import TREASURE_FOUND, GameState
from treasure_island.strategies import (
    REFERENCE_GAMES,
    Scribe,
    Silent,
    Stripes,
    brains_for,
    write_reference,
)

ROOT = Path(__file__).resolve().parents[1]
DIG = {"action": "dig"}
READ = {"action": "read"}
NOTHING = "You dug here and found nothing."


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


def view(position, square_dug=True, earlier=(), neighbours=(), on_cave=False):
    return TurnView(
        "pirate-1", "", position, 10, tuple(earlier), neighbours, square_dug, on_cave
    )


def stood(position, dug=True):
    """An earlier turn spent standing on `position`, which was dug or got dug."""
    action = {"action": "dig"} if not dug else {"action": "move", "direction": "east"}
    return EarlierTurn(position, action, "", square_dug=dug)


def test_silent_is_the_default_brain():
    assert parse_config({}).brain == "silent"
    assert all(isinstance(brain, Silent) for brain in brains_for("silent", game_of()))


def test_silent_digs_its_square_when_it_is_not_dug():
    assert Silent(4).decide(view((2, 2), square_dug=False)).action == DIG


def test_silent_walks_to_the_nearest_square_it_has_not_seen_dug():
    # From the corner, (1, 0) and (0, 1) are both one step away: the topmost wins.
    move = Silent(4).decide(view((0, 0))).action
    assert move == {"action": "move", "direction": "east"}


def test_silent_remembers_every_square_it_has_seen_dug():
    # It has stood on (1, 0) and dug it, so (0, 1) is now the nearest.
    earlier = [stood((0, 0), dug=False), stood((1, 0), dug=False)]
    move = Silent(4).decide(view((0, 0), earlier=earlier)).action
    assert move == {"action": "move", "direction": "south"}


def test_silent_steps_round_a_pirate_and_never_tries_a_blocked_move():
    told = (("east", "pirate-2"),)
    move = Silent(4).decide(view((0, 0), neighbours=told)).action
    assert move == {"action": "move", "direction": "south"}
    # Boxed in on every side it can go, it digs where it is rather than bump.
    boxed = (("east", "pirate-2"), ("south", "pirate-3"))
    assert Silent(4).decide(view((0, 0), neighbours=boxed)).action == DIG


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


def test_silent_never_writes_or_reads():
    records = silent_game(load_config(ROOT / "configs/silent.toml"))
    actions = {action["action"] for record in records for action in record["did"]}
    assert actions <= {"move", "dig", "enter"}


def test_silent_the_same_seed_gives_the_same_game():
    config = load_config(ROOT / "configs/silent.toml")
    assert silent_game(config) == silent_game(config)


def at(position, earlier=(), neighbours=(), square_dug=False):
    return TurnView(
        "pirate-1", "", position, 10, tuple(earlier), neighbours, square_dug
    )


def turn(position, action, result="", read_lines=()):
    return EarlierTurn(position, action, result, None, list(read_lines))


def move(direction):
    return tool_call("move", {"direction": direction})


def test_stripes_pirate_n_digs_only_its_own_rows():
    # A crew of 2: pirate-1 digs rows 0 and 2, pirate-2 rows 1 and 3.
    config = game_of(crew=2, turns=20, seed=seed_with_treasure(4, wanted=(3, 3)))
    records = list(Game(config, brains_for("stripes", config)).records())
    for agent, rows in (("pirate-1", {0, 2}), ("pirate-2", {1, 3})):
        mine = [r for r in records if r["agent"] == agent]
        assert {y for _, y in dug_squares(mine)} <= rows
    first = [r for r in records if r["agent"] == "pirate-1"]
    assert dug_squares(first)[:4] == [(0, 0), (1, 0), (2, 0), (3, 0)]


def test_stripes_skips_a_square_it_is_told_is_dug():
    brain = Stripes(grid_size=4, crew_size=2, index=0)
    earlier = [turn((0, 0), DIG, NOTHING), turn((0, 0), move("east"))]
    decision = brain.decide(at((1, 0), earlier, square_dug=True))
    assert decision.action == move("east")


def test_stripes_writes_i_am_blocked_when_the_next_square_holds_a_pirate():
    brain = Stripes(grid_size=4, crew_size=2, index=0)
    earlier = [turn((0, 0), DIG, NOTHING)]
    decision = brain.decide(at((0, 0), earlier, (("east", "pirate-2"),), True))
    assert decision.action == tool_call("write", {"text": "I am blocked"})


def test_stripes_on_digging_up_the_treasure_writes_where_it_is_then_enters():
    brain = Stripes(grid_size=4, crew_size=2, index=0)
    earlier = [turn((2, 0), DIG, TREASURE_FOUND)]
    wrote = brain.decide(at((2, 0), earlier, square_dug=True)).action
    assert wrote == tool_call("write", {"text": "The treasure is at (2, 0)."})
    earlier.append(turn((2, 0), wrote))
    assert brain.decide(at((2, 0), earlier, square_dug=True)).action == (
        tool_call("enter", {})
    )


def test_stripes_reads_every_5th_turn():
    brain = Stripes(grid_size=4, crew_size=2, index=0)
    earlier = [
        turn((0, 0), DIG, NOTHING),
        turn((0, 0), move("east")),
        turn((1, 0), DIG, NOTHING),
        turn((1, 0), move("east")),
    ]
    assert brain.decide(at((2, 0), earlier)).action == READ
    earlier.append(turn((2, 0), READ))
    assert brain.decide(at((2, 0), earlier)).action == DIG


def test_stripes_heads_for_the_cave_once_it_has_read_where_it_is():
    brain = Stripes(grid_size=4, crew_size=2, index=0)
    note = {"line": 1, "by": "pirate-2", "text": "The treasure is at (3, 1)."}
    earlier = [turn((0, 0), DIG, NOTHING), turn((0, 0), READ, "", [note])]
    assert brain.decide(at((0, 0), earlier, square_dug=True)).action == move("east")
    in_the_way = brain.decide(at((2, 1), earlier, (("east", "pirate-2"),), True))
    assert in_the_way.action == tool_call("write", {"text": "I am blocked"})
    assert brain.decide(at((3, 1), earlier, square_dug=True)).action == (
        tool_call("enter", {})
    )


def test_stripes_a_striping_crew_wins():
    config = load_config(ROOT / "configs/stripes.toml")
    records = list(Game(config, brains_for("stripes", config)).records())
    over = records[-1]["game_over"]
    assert over["reason"] == "everyone is in the cave"
    assert len(over["in_cave"]) == config.crew_size
    notes = [d["text"] for r in records for d in r["did"] if d["action"] == "write"]
    assert any(note.startswith("The treasure is at") for note in notes)


def scribe_game(config):
    return list(
        Game(config, [Scribe(config.grid_size) for _ in config.pirates]).records()
    )


def test_scribe_moves_and_digs_like_the_silent_pirate():
    assert Scribe(4).decide(view((2, 2), square_dug=False)).action == DIG
    assert (
        Scribe(4).decide(view((0, 0))).action == Silent(4).decide(view((0, 0))).action
    )


def test_scribe_writes_what_it_found_on_the_turn_after_each_dig():
    dug = [EarlierTurn((3, 1), DIG, "")]
    note = Scribe(4).decide(view((3, 1), earlier=dug)).action
    assert note == {"action": "write", "text": "Dug (3, 1): nothing"}
    found = Scribe(4).decide(view((3, 1), earlier=dug, on_cave=True)).action
    assert found == {"action": "write", "text": "Treasure at (3, 1)"}
    # In a whole game, every dig is followed by that pirate writing.
    records = scribe_game(load_config(ROOT / "configs/scribe.toml"))
    for index, record in enumerate(records):
        if record["did"][-1] == DIG:
            pirate = record["agent"]
            later = [r for r in records[index + 1 :] if r["agent"] == pirate]
            assert not later or later[0]["did"][0]["action"] == "write"


def test_scribe_never_reads():
    records = scribe_game(load_config(ROOT / "configs/scribe.toml"))
    actions = {action["action"] for record in records for action in record["did"]}
    assert "read" not in actions
    assert "write" in actions


def test_scribe_writes_where_the_cave_is_before_it_enters():
    # One it walked onto, opened by another pirate, it writes about first too.
    walked = [EarlierTurn((1, 1), {"action": "move", "direction": "east"}, "")]
    note = Scribe(4).decide(view((1, 1), earlier=walked, on_cave=True)).action
    assert note == {"action": "write", "text": "Treasure at (1, 1)"}
    wrote = [EarlierTurn((1, 1), note, "")]
    assert Scribe(4).decide(view((1, 1), earlier=wrote, on_cave=True)).action == {
        "action": "enter"
    }
    records = scribe_game(load_config(ROOT / "configs/scribe.toml"))
    entries = [i for i, r in enumerate(records) if r["did"][-1] == {"action": "enter"}]
    assert entries
    for index in entries:
        pirate = records[index]["agent"]
        before = [r for r in records[:index] if r["agent"] == pirate][-1]
        assert before["did"][-1]["action"] == "write"
        assert before["did"][-1]["text"].startswith("Treasure at ")


def test_scribe_the_same_seed_gives_the_same_game():
    config = load_config(ROOT / "configs/scribe.toml")
    assert brains_for("scribe", config)
    assert scribe_game(config) == scribe_game(config)


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
    assert "byte-identical" in capsys.readouterr().out


@pytest.mark.parametrize("name", REFERENCE_GAMES)
def test_reference_games_pass_the_validator(name):
    assert log_errors(ROOT / "runs" / f"reference-{name}" / "events.jsonl") == []


def test_reference_games_tell_a_story_that_ends_with_the_score():
    story = (ROOT / "runs/reference-silent/story.txt").read_text().splitlines()
    assert story[0].startswith(
        "Turn 0: pirate-1 at (0, 0), on undug sand, with pirate-2 to the south. "
        "It thought: Nobody has dug this square yet. Then it dug at (0, 0)"
    )
    assert story[-1].startswith("Game over: ")
    assert "Score " in story[-1]
