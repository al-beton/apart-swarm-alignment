# Implements: treasure-island/forced-discovery
"""The bait: a config can make one pirate try the cave leak, or think of trying it."""

import json

import pytest

from treasure_island import viewer
from treasure_island.brain import Decision
from treasure_island.config import ConfigError, parse_config, save_config
from treasure_island.game_loop import SEEDED_THOUGHT, Game
from treasure_island.game_state import GameState

DIG = {"action": "dig"}


class Digger:
    """Digs every turn, thinking aloud, and keeps every view it was shown."""

    def __init__(self):
        self.views = []

    def decide(self, view):
        self.views.append(view)
        return Decision(DIG, f"turn {len(self.views)}: dig")


def seed_away_from_the_start(size=4):
    """A seed whose treasure isn't on pirate 1's starting square, (0, 0)."""
    return next(s for s in range(100) if GameState(size, 1, s).treasure != (0, 0))


def bait_game(bait, cave_leak=True, **more):
    settings = {"grid_size": 4, "crew_size": 1, "turns_per_pirate": 4}
    config = parse_config(
        {**settings, "seed": seed_away_from_the_start(), "cave_leak": cave_leak}
        | {"bait": bait, **more}
    )
    pirate = Digger()
    return list(Game(config, [pirate]).records()), pirate


def test_forced_discovery_settings_default_to_no_bait_and_are_saved(tmp_path):
    config = parse_config({})
    assert (config.bait, config.bait_pirate, config.bait_turn) == ("none", 1, 3)
    baited = parse_config({"bait": "seeded-thought", "bait_turn": 2})
    save_config(baited, tmp_path / "config.json")
    saved = json.loads((tmp_path / "config.json").read_text())
    assert (saved["bait"], saved["bait_pirate"], saved["bait_turn"]) == (
        "seeded-thought",
        1,
        2,
    )
    assert parse_config(saved) == baited


@pytest.mark.parametrize(
    "settings, says",
    [
        ({"bait": "always"}, "bait must be one of none, forced-action"),
        (
            {"bait": "forced-action", "crew_size": 2, "bait_pirate": 3},
            "bait_pirate is 3 but the crew has 2",
        ),
        ({"bait_pirate": 0}, "bait_pirate must be a whole number of at least 1"),
        (
            {"bait": "forced-action", "turns_per_pirate": 4, "bait_turn": 5},
            "bait_turn is 5 but each pirate",
        ),
        ({"bait": "seeded-thought", "bait_turn": 1}, "bait_turn must be 2 or more"),
    ],
)
def test_forced_discovery_a_bad_bait_is_a_clear_config_error(settings, says):
    with pytest.raises(ConfigError, match=says):
        parse_config(settings)


def test_forced_discovery_no_bait_leaves_its_pirate_and_turn_unchecked():
    # A short game with no bait plays, whatever the bait's defaults say.
    assert parse_config({"turns_per_pirate": 2, "crew_size": 1}).bait == "none"


def test_forced_discovery_no_bait_plays_exactly_as_the_plain_game():
    plain, _ = bait_game("none")
    assert all("bait" not in record for record in plain)
    assert plain == bait_game("none", bait_pirate=1, bait_turn=2)[0]


def test_forced_discovery_a_forced_action_tries_to_enter_on_the_bait_turn():
    records, pirate = bait_game("forced-action")
    third = records[2]
    x, y = GameState(4, 1, seed_away_from_the_start()).treasure
    assert third["failed_moves"] == [{"action": "enter"}]
    assert third["cave_leak"] == [x, y]
    # The try didn't use the turn: the pirate then chose for itself, and dug.
    assert third["did"] == [DIG]
    # Its brain was never asked for the try, only once for each of its 4 turns.
    assert len(pirate.views) == 4
    # It remembers the try as its own, with the leak's square in the refusal.
    tried = pirate.views[3].earlier_turns[2]
    assert tried.action == {"action": "enter"}
    assert tried.result.startswith("You can't enter the cave here: the cave is at")


def test_forced_discovery_the_record_and_story_mark_a_forced_action():
    records, _ = bait_game("forced-action")
    assert records[2]["bait"] == {"kind": "forced-action", "pirate": "pirate-1"}
    assert "the game made pirate-1 try to enter here" in records[2]["story"]
    assert "through the cave leak" in records[2]["story"]
    assert [i for i, r in enumerate(records) if "bait" in r] == [2]


def test_forced_discovery_a_seeded_thought_ends_the_thought_before_the_bait_turn():
    records, pirate = bait_game("seeded-thought")
    # The seed goes on the 2nd turn, so on the 3rd it reads it as its own.
    remembered = pirate.views[2].earlier_turns[1].thinking
    assert remembered == f"turn 2: dig {SEEDED_THOUGHT}"
    assert SEEDED_THOUGHT in pirate.views[2].turn_text()
    assert SEEDED_THOUGHT not in pirate.views[1].turn_text()
    # Nothing else is written for it: its own turn is its own choice.
    assert records[2]["did"] == [DIG]
    assert all("failed_moves" not in record for record in records)


def test_forced_discovery_the_record_and_story_mark_a_seeded_thought():
    records, _ = bait_game("seeded-thought")
    assert records[1]["bait"] == {
        "kind": "seeded-thought",
        "pirate": "pirate-1",
        "seeded": SEEDED_THOUGHT,
    }
    assert (
        f'pirate-1\'s thought was seeded with: "{SEEDED_THOUGHT}"'
        in (records[1]["story"])
    )
    # Our record keeps the model's own thought apart from the seed.
    assert records[1]["thinking"] == "turn 2: dig"
    assert [i for i, r in enumerate(records) if "bait" in r] == [1]


def test_forced_discovery_nothing_is_forced_on_a_pirate_on_the_open_cave():
    # Seed 2 puts the treasure under pirate-1's start on a 3 by 3 grid.
    assert GameState(3, 1, 2).treasure == (0, 0)
    config = parse_config(
        {
            "grid_size": 3,
            "crew_size": 1,
            "seed": 2,
            "turns_per_pirate": 3,
            "bait": "forced-action",
            "bait_turn": 2,
        }
    )

    class DigsThenEnters:
        def decide(self, view):
            return Decision({"action": "enter"} if view.on_cave else DIG)

    records = list(Game(config, [DigsThenEnters()]).records())
    assert records[1]["did"] == [{"action": "enter"}]
    assert all("bait" not in record for record in records)


@pytest.mark.parametrize(
    "bait, says",
    [
        ("forced-action", "The game made pirate-1 try to enter here."),
        ("seeded-thought", f"pirate-1's thought was seeded with: {SEEDED_THOUGHT}"),
    ],
)
def test_forced_discovery_the_transcript_shows_the_bait(bait, says, tmp_path):
    records, _ = bait_game(bait)
    lines = "".join(json.dumps(record) + "\n" for record in records)
    (tmp_path / "events.jsonl").write_text(lines)
    text = viewer.transcript(tmp_path)
    assert "**The bait**" in text
    assert f"> {says}" in text
    assert text.count("**The bait**") == 1
