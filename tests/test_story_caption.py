# Implements: viewer/story-caption, treasure-island/readable-at-once
"""Each frame carries its turn's line of the story, word for word."""

import io
import json
from pathlib import Path

import pytest
from PIL import Image, ImageChops

from treasure_island import viewer

ROOT = Path(__file__).resolve().parents[1]
GAMES = ["examples/silent", "examples/stripes", "examples/small-crew"]
CREW = {"pirate-1": [0, 0], "pirate-2": [0, 0]}


def record(turn, story=None):
    made = {
        "turn": turn,
        "agent": "pirate-1",
        "saw": {"position": [0, 0], "prompt": ""},
        "did": [{"action": "dig"}],
        "log_shown": [],
        "crew": CREW,
        "outcome": {"position": [0, 0], "found_treasure": False},
    }
    if story:
        made["story"] = story
    return made


def records_of(game):
    return viewer.records_in(ROOT / game)


def width_of(game):
    records = records_of(game)
    return viewer.frame(records, 0, viewer.grid_size(ROOT / game, records)).width


@pytest.mark.parametrize("game", GAMES)
def test_story_caption_each_turn_holds_its_story_line_word_for_word(game):
    lines = (ROOT / game / "story.txt").read_text().splitlines()
    records = records_of(game)
    width = width_of(game)
    for record_, line in zip(records, lines, strict=False):
        assert " ".join(viewer.caption_rows(record_["story"], width)) == line


@pytest.mark.parametrize("game", GAMES)
def test_story_caption_the_longest_line_fits_and_the_frame_stays_one_size(game):
    records = records_of(game)
    folder = ROOT / game
    size = viewer.grid_size(folder, records)
    sizes = {viewer.frame(records, turn, size).size for turn in range(len(records))}
    assert len(sizes) == 1
    longest = max(len(viewer.caption_rows(r["story"], width_of(game))) for r in records)
    assert viewer.caption_height(records, width_of(game)) >= viewer.rows_height(longest)
    gif = Image.open(io.BytesIO(viewer.gif(folder)))
    assert gif.size == sizes.pop()


def test_story_caption_a_very_long_note_is_shown_in_full_by_a_taller_caption():
    wall = " ".join(["word"] * 300)
    records = [record(0, f'Turn 0: pirate-1 wrote "{wall}".'), record(1, "short")]
    tall = viewer.frame(records, 1, 4)
    assert viewer.frame(records, 0, 4).size == tall.size
    plain = viewer.frame([record(0, "short"), record(1, "short")], 1, 4)
    assert tall.height > plain.height
    rows = viewer.caption_rows(records[0]["story"], tall.width)
    assert " ".join(rows) == records[0]["story"]


def test_story_caption_a_long_thought_shows_its_first_and_last_words():
    thought = " ".join(f"w{n}" for n in range(1, 101))
    story = f"Turn 0: pirate-1 at A1. It thought: {thought} Then it dug at A1."
    line = viewer.caption_line(story)
    first = " ".join(f"w{n}" for n in range(1, 13))
    last = " ".join(f"w{n}" for n in range(89, 101))
    assert line == f"Turn 0: pirate-1 at A1. It thought: {first} … {last} Then it dug at A1."


def test_story_caption_a_short_thought_and_the_rest_stay_word_for_word():
    thought = " ".join(["hmm"] * 30)
    story = f"Turn 0: pirate-1 at A1. It thought: {thought} Then it dug at A1."
    assert viewer.caption_line(story) == story
    assert viewer.caption_line("Turn 1: pirate-1 at A1, dug at A1.") == (
        "Turn 1: pirate-1 at A1, dug at A1."
    )


def test_story_caption_a_long_thought_keeps_frames_short():
    thought = " ".join(["word"] * 2000)
    long_ = record(0, f"Turn 0: pirate-1 at A1. It thought: {thought} Then it dug.")
    short = record(1, "Turn 1: pirate-1 at A1, dug.")
    tall = viewer.frame([long_, short], 0, 4)
    plain = viewer.frame([record(0, "Turn 0: short"), short], 0, 4)
    assert tall.height - plain.height < 100


def test_story_caption_changes_with_the_story():
    first = viewer.frame([record(0, "one line of the story")], 0, 4)
    second = viewer.frame([record(0, "another line of the story")], 0, 4)
    assert ImageChops.difference(first, second).getbbox()


def test_story_caption_a_run_with_no_story_still_draws():
    assert viewer.frame([record(0)], 0, 4).size


def test_story_caption_the_page_and_the_gif_show_the_same_frame():
    folder = ROOT / "examples/small-crew"
    png = Image.open(io.BytesIO(viewer.frame_png(folder, 0))).convert("RGB")
    gif = Image.open(io.BytesIO(viewer.gif(folder)))
    gif.seek(0)
    assert png.size == gif.size
    assert json.loads((folder / "events.jsonl").read_text().splitlines()[0])["story"]
