# Implements: treasure-island/looks-are-cosmetic, treasure-island/graphics-elsewhere
"""A pirate's looks pick its sprite, and nothing else."""

from pathlib import Path

import pytest

from treasure_island.brain import Decision
from treasure_island.config import parse_config
from treasure_island.game_loop import write_game

SETTINGS = {"grid_size": 4, "turns_per_pirate": 6, "seed": 3}
PLAIN_CREW = [
    {"personality": 1, "head_text": "Anne Bonny", "colour": [200, 0, 0]},
    {"personality": 2, "head_text": "Mary Read", "colour": [0, 0, 200]},
]
OTHER_CREW = [
    {"personality": 19, "head_text": "Calico Jack", "colour": [1, 200, 1]},
    {"personality": 20, "head_text": "Blackbeard", "colour": [9, 9, 9]},
]
SOURCE = Path(__file__).resolve().parents[1] / "src/treasure_island"


class Busy:
    """A strategy that walks, digs, writes and reads, noting every view's text."""

    def __init__(self):
        self.actions = [
            {"action": "write", "text": "starting here"},
            {"action": "move", "direction": "east"},
            {"action": "dig"},
            {"action": "read"},
        ]
        self.texts = []

    def decide(self, view):
        self.texts.append(view.as_text())
        return Decision(self.actions[len(self.texts) % len(self.actions)])


def played(crew, folder):
    brains = [Busy(), Busy()]
    config = parse_config({**SETTINGS, "pirates": crew})
    write_game(config, brains, folder)
    return brains, {path.name: path.read_bytes() for path in folder.iterdir()}


@pytest.fixture
def games(tmp_path):
    (tmp_path / "plain").mkdir()
    (tmp_path / "other").mkdir()
    return played(PLAIN_CREW, tmp_path / "plain"), played(
        OTHER_CREW, tmp_path / "other"
    )


def test_looks_are_cosmetic_the_same_seed_gives_identical_logs(games):
    (_, plain), (_, other) = games
    assert "events.jsonl" in plain
    assert plain == other


def test_looks_are_cosmetic_a_turn_view_is_the_same_whatever_the_looks(games):
    (plain_brains, _), (other_brains, _) = games
    assert plain_brains[0].texts
    for plain, other in zip(plain_brains, other_brains, strict=True):
        assert plain.texts == other.texts


def test_looks_are_cosmetic_head_text_never_appears_in_a_view_or_a_log(games):
    (brains, files), _ = games
    shown = "".join(text for brain in brains for text in brain.texts)
    written = b"".join(files.values()).decode()
    for pirate in PLAIN_CREW:
        assert pirate["head_text"] not in shown
        assert pirate["head_text"] not in written


@pytest.mark.parametrize(
    "module",
    ["game_loop.py", "game_state.py", "brain.py", "pirates_log.py", "score.py"],
)
def test_graphics_elsewhere_the_game_itself_draws_nothing(module):
    code = (SOURCE / module).read_text()
    for art in ("PIL", "assets", "viewer"):
        assert art not in code, art


def test_graphics_elsewhere_the_config_says_what_each_pirate_is():
    config = parse_config({**SETTINGS, "pirates": PLAIN_CREW})
    assert [pirate.head_text for pirate in config.pirates] == [
        "Anne Bonny",
        "Mary Read",
    ]
    assert [pirate.personality for pirate in config.pirates] == [1, 2]
    assert config.pirates[0].colour == (200, 0, 0)
