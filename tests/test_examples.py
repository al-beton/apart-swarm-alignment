# Implements: results/examples-folder, results/examples-listed, results/examples-small, results/examples-stay-true
"""The committed example games, which always show what the code does today."""

import shutil
from pathlib import Path

import pytest

from treasure_island import examples, saved_game, viewer

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "examples"
NAMES = sorted(examples.EXAMPLES)


def test_examples_folder_holds_at_least_three_different_games():
    assert len(NAMES) >= 3
    stories = {(FOLDER / name / "story.txt").read_bytes() for name in NAMES}
    assert len(stories) == len(NAMES)
    assert sorted(path.name for path in FOLDER.iterdir() if path.is_dir()) == NAMES


@pytest.mark.parametrize("name", NAMES)
def test_examples_folder_each_holds_what_the_game_wrote_and_a_gif(name):
    assert {path.name for path in (FOLDER / name).iterdir()} == {
        "config.json",
        "events.jsonl",
        "game.gif",
        "manifest.json",
        "pirates-log.txt",
        "replies.jsonl",
        "story.txt",
        "transcript.md",
    }


@pytest.mark.parametrize("name", NAMES)
def test_examples_listed_each_in_one_line_of_the_guide(name):
    guide = (FOLDER / "README.md").read_text().splitlines()
    assert len([line for line in guide if line.startswith(f"- **`{name}/`")]) == 1


@pytest.mark.parametrize("name", NAMES)
def test_examples_small_each_gif_is_under_2_mb(name):
    assert (FOLDER / name / "game.gif").stat().st_size < 2_000_000


@pytest.mark.parametrize("name", NAMES)
def test_examples_stay_true_every_log_replays_byte_identical(name):
    assert saved_game.differences(FOLDER / name) == [], examples.REMAKE


@pytest.mark.parametrize("name", NAMES)
def test_examples_stay_true_every_gif_matches_what_is_drawn_now(name):
    assert examples.problem(FOLDER / name) is None


def test_examples_stay_true_a_stale_example_says_how_to_remake_it(tmp_path):
    copy = tmp_path / NAMES[0]
    shutil.copytree(FOLDER / NAMES[0], copy)
    (copy / "game.gif").write_bytes(b"not this one")
    message = examples.problem(copy)
    assert "game.gif" in message
    assert "make examples" in message
    assert viewer.gif(copy) != b"not this one"


def test_examples_stay_true_a_stale_transcript_is_caught(tmp_path):
    copy = tmp_path / NAMES[0]
    shutil.copytree(FOLDER / NAMES[0], copy)
    (copy / "transcript.md").write_text("not this one")
    assert "transcript.md" in examples.problem(copy)
