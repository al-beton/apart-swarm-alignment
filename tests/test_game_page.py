# Implements: viewer/game-page, viewer/score-counter
"""The slideshow as a full game page: the board beside every turn's whole record."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from treasure_island import cli, viewer

ROOT = Path(__file__).resolve().parents[1]
GAME = "runs/reference-scribe"  # a scripted game that writes to the scroll


@pytest.fixture
def saved(tmp_path, monkeypatch):
    """A copy of a committed game that writes, in a folder of its own."""
    monkeypatch.chdir(tmp_path)
    shutil.copytree(ROOT / GAME, tmp_path / GAME)
    return tmp_path / GAME


def records_of(folder):
    lines = (folder / "events.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines]


def rewrite(folder, records):
    (folder / "events.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))


def turns_in(page):
    found = re.search(r"const TURNS = (.*?);\n", page, re.DOTALL)
    return json.loads(found.group(1))


def as_llm_game(folder):
    """The game as an LLM crew might have played it: long prompts, thinking, refusals."""
    records = records_of(folder)
    for record in records:
        record["saw"]["prompt"] = "You are a pirate. " * 400 + "\n\nWhat do you do?"
        record["thinking"] = "I should think this through. " * 200
    records[1]["refused"] = [
        {"reply": "I'd rather dig", "why": "that wasn't a tool call"}
    ]
    rewrite(folder, records)
    return records


def test_game_page_both_commands_write_it(saved, capsys):
    for command in (["slideshow", str(saved)], ["show", str(saved)]):
        saved.with_suffix(".html").unlink(missing_ok=True)
        assert cli.main(command) == 0
        page = saved.with_suffix(".html").read_text()
        assert 'id="feed"' in page
        assert str(saved.with_suffix(".html")) in capsys.readouterr().out


def test_game_page_is_built_from_the_event_log_alone(saved, tmp_path):
    alone = tmp_path / "alone"
    alone.mkdir()
    shutil.copy(saved / "events.jsonl", alone / "events.jsonl")
    turns = turns_in(viewer.slideshow_page(alone))
    assert [t["agent"] for t in turns] == [r["agent"] for r in records_of(saved)]
    # The last frame counts up to the recorded score, by the log's own numbers.
    records = viewer.records_in(alone)
    scoring, last = viewer.scoring_in(alone), len(records) - 1
    final = viewer.turn_steps(records, last, scoring)[-1]
    size = viewer.grid_size(alone, records)
    shown = viewer.scene(records, last, size, step=final, scoring=scoring)
    assert shown["score"] == records[-1]["game_over"]["score"]


def test_game_page_holds_each_turn_s_whole_record(saved):
    turns = turns_in(viewer.slideshow_page(saved))
    for turn, record in zip(turns, records_of(saved), strict=True):
        assert turn["turn"] == record["turn"]
        assert turn["agent"] == record["agent"]
        assert turn["prompt"] == record["saw"]["prompt"]
        assert turn["thinking"] == record.get("thinking", "")
        assert turn["did"] == record["did"]
        assert turn["result"] == record["result"]


def test_game_page_an_llm_turn_keeps_its_prompt_thinking_and_refused_replies(saved):
    records = as_llm_game(saved)
    turns = turns_in(viewer.slideshow_page(saved))
    assert turns[0]["prompt"] == records[0]["saw"]["prompt"]  # whole, never cut
    assert turns[0]["thinking"] == records[0]["thinking"]
    assert turns[1]["refused"] == records[1]["refused"]
    assert turns[0]["refused"] == []


def test_game_page_a_scripted_turn_with_no_thinking_still_shows(saved):
    records = records_of(saved)
    for record in records:
        record.pop("thinking", None)
        record["saw"]["prompt"] = ""
    rewrite(saved, records)
    turns = turns_in(viewer.slideshow_page(saved))
    assert {t["thinking"] for t in turns} == {""}
    assert {t["prompt"] for t in turns} == {""}


def test_game_page_the_scroll_so_far_is_rebuilt_newest_last(saved):
    turns = turns_in(viewer.slideshow_page(saved))
    written = [line for turn in turns for line in turn["wrote"]]
    assert written, "the game should write to the scroll"
    as_saved = (saved / "pirates-log.txt").read_text().splitlines()
    assert [f"{w['line']} {w['by']}: {w['text']}" for w in written] == as_saved
    # Each line belongs to the turn that wrote it, so the page shows only those so far.
    for turn in turns:
        writes = [a["text"] for a in turn["did"] if a["action"] == "write"]
        assert [w["text"] for w in turn["wrote"]] == writes


def test_game_page_a_note_written_over_lines_shows_on_one_as_the_scroll_keeps_it(saved):
    # A pirate writes its first note across two lines; the scroll joins them.
    records = records_of(saved)
    turn = next(r for r in records if any(a["action"] == "write" for a in r["did"]))
    note = next(a for a in turn["did"] if a["action"] == "write")
    note["text"] = note["text"].replace(" ", "\n", 1)
    assert "\n" in note["text"]
    rewrite(saved, records)
    turns = turns_in(viewer.slideshow_page(saved))
    written = [line for shown in turns for line in shown["wrote"]]
    as_saved = (saved / "pirates-log.txt").read_text().splitlines()
    assert [f"{w['line']} {w['by']}: {w['text']}" for w in written] == as_saved
    # What the pirate did stays exactly as it wrote it.
    first = next(shown for shown in turns if shown["wrote"])
    assert "\n" in next(a["text"] for a in first["did"] if a["action"] == "write")


def test_game_page_long_text_wraps_inside_its_column(saved):
    page = viewer.slideshow_page(saved)
    assert "white-space: pre-wrap" in page
    assert "overflow-wrap: anywhere" in page
    assert "min-width: 0" in page  # a grid column can shrink instead of overflowing


@pytest.mark.parametrize(
    "words", ["</script><script>alert(1)</script> & <b>bold</b>", "<!-- <script>"]
)
def test_game_page_nothing_a_pirate_wrote_or_saw_breaks_out_of_the_page(saved, words):
    records = records_of(saved)
    records[0]["saw"]["prompt"] = words
    records[0]["thinking"] = words
    records[0]["result"] = words
    records[0]["did"] = [{"action": "write", "text": words}]
    rewrite(saved, records)
    page = viewer.slideshow_page(saved)
    data = re.search(r"const TURNS = (.*?);\n", page, re.DOTALL).group(1)
    assert "<" not in data
    turn = turns_in(page)[0]
    assert (turn["prompt"], turn["thinking"], turn["result"]) == (words,) * 3
    assert "innerHTML" not in page


@pytest.mark.skipif(
    shutil.which("node") is None, reason="needs node to parse the script"
)
def test_game_page_its_script_parses(saved, tmp_path):
    script = re.search(
        r"<script>(.*)</script>", viewer.slideshow_page(saved), re.DOTALL
    )
    path = tmp_path / "page.js"
    path.write_text(script.group(1))
    subprocess.run(["node", "--check", str(path)], check=True)


def test_game_page_shows_the_reasoning_tokens_a_turn_spent(saved):
    records = records_of(saved)
    records[0]["reasoning_tokens"] = 812
    rewrite(saved, records)
    page = viewer.slideshow_page(saved)
    turns = turns_in(page)
    assert turns[0]["reasoned"] == "Its model spent 812 tokens reasoning."
    assert turns[1]["reasoned"] == ""
    assert 'id="reasoned"' in page
