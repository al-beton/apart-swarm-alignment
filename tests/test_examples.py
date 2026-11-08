# Implements: results/examples-folder, results/examples-listed, results/examples-small, results/examples-stay-true
"""The committed example games, which always show what the code does today."""

import base64
import io
import json
import re
import shutil
from pathlib import Path

import pytest
from PIL import Image

from treasure_island import examples, replay, saved_game, viewer

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "examples"
NAMES = sorted(examples.EXAMPLES)
SAME_ISLAND = ("grid_size", "crew_size", "turns_per_pirate", "seed")


def test_examples_folder_holds_an_llm_game_and_stripes_on_the_same_island():
    assert list(examples.EXAMPLES) == ["llm-crew", "stripes"]
    assert sorted(path.name for path in FOLDER.iterdir() if path.is_dir()) == NAMES
    llm, stripes = (
        json.loads((FOLDER / name / "config.json").read_text())
        for name in ("llm-crew", "stripes")
    )
    assert {key: llm[key] for key in SAME_ISLAND} == {
        key: stripes[key] for key in SAME_ISLAND
    }
    assert all(pirate.get("model") for pirate in llm["pirates"])
    assert stripes["brain"] == "stripes"


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
        "game.html",
    }


@pytest.mark.parametrize("name", NAMES)
def test_examples_listed_each_in_one_line_of_the_guide(name):
    guide = (FOLDER / "README.md").read_text().splitlines()
    assert len([line for line in guide if line.startswith(f"- **`{name}/`")]) == 1


def test_examples_listed_in_the_order_they_are_shown_llm_first():
    guide = (FOLDER / "README.md").read_text().splitlines()
    listed = [
        line.split("`")[1].rstrip("/") for line in guide if line.startswith("- **`")
    ]
    assert listed == list(examples.EXAMPLES)


@pytest.mark.parametrize("name", NAMES)
def test_examples_small_each_gif_is_under_2_mb(name):
    assert (FOLDER / name / "game.gif").stat().st_size < 2_000_000


@pytest.mark.parametrize("name", NAMES)
def test_examples_stay_true_every_log_replays_byte_identical(name):
    if name in examples.PLAYED_BY_MODELS:
        # Played by real models: checked by its recorded actions, never re-asked.
        assert replay.problem(FOLDER / name) is None
    else:
        assert saved_game.differences(FOLDER / name) == [], examples.REMAKE


def test_examples_stay_true_a_stale_game_page_is_caught(tmp_path):
    copy = tmp_path / "stripes"
    shutil.copytree(FOLDER / "stripes", copy)
    (copy / "game.html").write_text("not this one")
    assert "game.html" in examples.problem(copy)


def test_examples_stay_true_a_page_differing_only_in_png_bytes_is_the_same(tmp_path):
    # Another machine's zlib packs the same frames into different PNG bytes.
    copy = tmp_path / "stripes"
    shutil.copytree(FOLDER / "stripes", copy)
    page = (copy / "game.html").read_text()

    def repack(match):
        image = Image.open(io.BytesIO(base64.b64decode(match.group(1))))
        out = io.BytesIO()
        image.save(out, format="PNG", compress_level=1)
        return f'"frame": "{base64.b64encode(out.getvalue()).decode()}"'

    repacked = re.sub(r'"frame": "([A-Za-z0-9+/=]+)"', repack, page)
    assert repacked != page
    (copy / "game.html").write_text(repacked)
    assert examples.problem(copy) is None
    examples.draw(copy)
    assert (copy / "game.html").read_text() == repacked  # left alone, not rewritten


def test_examples_stay_true_the_llm_game_is_redrawn_not_replayed(tmp_path, monkeypatch):
    shutil.copytree(FOLDER / "llm-crew", tmp_path / "examples/llm-crew")
    (tmp_path / "examples/llm-crew/game.gif").write_bytes(b"old")
    monkeypatch.setattr(
        saved_game, "write_saved", lambda *a, **k: pytest.fail("asked models")
    )
    folder = examples.remake("llm-crew", tmp_path)
    assert (folder / "game.gif").read_bytes() == viewer.gif(folder)
    assert examples.problem(folder) is None


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
