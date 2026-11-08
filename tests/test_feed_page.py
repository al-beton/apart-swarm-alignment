# Implements: viewer/game-page, viewer/planned-turns, viewer/game-page-steps, viewer/scroll-written-live
"""The game page as a feed: the game state on the left, every planned turn on the right."""

import base64
import io
import json
import re
import shutil
from pathlib import Path

import pytest
from PIL import Image

from treasure_island import viewer

ROOT = Path(__file__).resolve().parents[1]
GAME = "runs/reference-scribe"  # a scripted game that writes and goes into the cave


@pytest.fixture
def saved(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    shutil.copytree(ROOT / GAME, tmp_path / GAME)
    return tmp_path / GAME


def records_of(folder):
    lines = (folder / "events.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines]


def rewrite(folder, records):
    (folder / "events.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))


def data_in(page, name):
    found = re.search(rf"const {name} = (.*?);\n", page, re.DOTALL)
    return json.loads(found.group(1))


def image_of(encoded):
    return Image.open(io.BytesIO(base64.b64decode(encoded)))


def test_game_page_the_left_shows_the_board_alone_above_the_parchment_scroll(saved):
    page = viewer.slideshow_page(saved)
    turns = data_in(page, "TURNS")
    for number, turn in enumerate(turns):
        assert base64.b64decode(turn["frame"]) == viewer.board_png(saved, number)
    # The board without the side panel, caption or log strip: narrower and shorter.
    board = image_of(turns[0]["frame"])
    whole = Image.open(io.BytesIO(viewer.frame_png(saved, 0)))
    assert board.width < whole.width and board.height < whole.height
    assert 'class="parchment"' in page


def test_game_page_the_board_never_draws_the_note(saved):
    records = viewer.records_in(saved)
    writes = next(
        n
        for n, r in enumerate(records)
        if any(a["action"] == "write" for a in r["did"])
    )
    size = viewer.grid_size(saved, records)
    pirates = viewer.pirates_in(saved, records)
    drawn = viewer.board(records, writes, size, pirates)
    # The same turn writing something else draws the same board: no note on it.
    other = [dict(r) for r in records]
    other[writes] = {**other[writes], "did": [{"action": "write", "text": "Other."}]}
    assert drawn.tobytes() == viewer.board(other, writes, size, pirates).tobytes()
    # The frame of that turn does draw it.
    framed = viewer.frame(records, writes, size, pirates)
    assert framed.tobytes() != viewer.frame(other, writes, size, pirates).tobytes()


def test_game_page_each_entry_says_who_its_turn_and_what_it_was_told(saved):
    turns = data_in(viewer.slideshow_page(saved), "TURNS")
    first = turns[0]
    assert first["own"] == 1
    assert first["told"].startswith("You are at A5.")
    second_of_its_own = next(t for t in turns[1:] if t["agent"] == first["agent"])
    assert second_of_its_own["own"] == 2


def test_game_page_a_turn_with_no_prompt_was_told_nothing_in_words(saved):
    records = records_of(saved)
    records[0]["saw"]["prompt"] = ""
    rewrite(saved, records)
    assert data_in(viewer.slideshow_page(saved), "TURNS")[0]["told"] == ""


def test_game_page_thinking_is_folded_with_its_length_and_last_sentence(saved):
    page = viewer.slideshow_page(saved)
    assert "lastSentence(t.thinking)" in page and "words(t.thinking)" in page
    # Built closed: a details element with no `open`.
    assert 'el("details", {}' in page


def test_game_page_everything_it_saw_opens_in_a_drawer(saved):
    page = viewer.slideshow_page(saved)
    assert 'id="drawer"' in page
    # Rejected replies go in as elements, spread, never as one array turned to text.
    assert "...t.refused.map(" in page
    assert "see everything it saw" in page


def test_planned_turns_lists_every_turn_the_game_could_have_by_round(saved):
    records = viewer.records_in(saved)
    scoring = viewer.scoring_in(saved)
    slots = viewer.planned_turns(records, scoring)
    crew = viewer.crew_names(records)
    assert len(slots) == len(crew) * scoring.turns_per_pirate
    assert [s["round"] for s in slots[: len(crew)]] == [1] * len(crew)
    assert [s["agent"] for s in slots[: len(crew)]] == crew
    played = [s["turn"] for s in slots if s["kind"] == "played"]
    assert played == list(range(len(records)))


def test_planned_turns_a_pirate_in_the_cave_shows_cave_rows_once_reached(saved):
    records = viewer.records_in(saved)
    slots = viewer.planned_turns(records, viewer.scoring_in(saved))
    went_in = next(n for n, r in enumerate(records) if r["outcome"].get("in_cave"))
    who = records[went_in]["agent"]
    caves = [s for s in slots if s["kind"] == "cave"]
    assert caves and {s["agent"] for s in caves} >= {who}
    assert all(s["after"] >= went_in for s in caves if s["agent"] == who)


def test_planned_turns_a_turn_the_game_ended_before_says_so_at_the_end(saved):
    records = viewer.records_in(saved)
    # The game ends early: everything after the first round is never played.
    cut = records[:3]
    cut[-1] = {**cut[-1], "game_over": records[-1]["game_over"]}
    slots = viewer.planned_turns(cut, viewer.scoring_in(saved))
    over = [s for s in slots if s["kind"] == "over"]
    assert over and all(s["after"] == len(cut) - 1 for s in over)


def test_planned_turns_an_unfinished_game_leaves_the_rest_not_yet(saved):
    records = viewer.records_in(saved)[:3]
    slots = viewer.planned_turns(records, viewer.scoring_in(saved))
    assert {s["kind"] for s in slots} <= {"played", "cave", "later"}
    assert any(s["kind"] == "later" for s in slots)


def test_planned_turns_are_in_the_page_with_the_not_yet_rows(saved):
    page = viewer.slideshow_page(saved)
    game = data_in(page, "GAME")
    assert len(game["slots"]) == len(game["crew"]) * game["turns_each"]
    assert "not yet" in page
    assert "Not played: the game was over" in page


def test_game_page_steps_arrow_keys_play_slider_and_filter_step_the_page(saved):
    page = viewer.slideshow_page(saved)
    assert '"ArrowLeft"' in page and '"ArrowRight"' in page
    assert 'id="play"' in page and 'id="speed"' in page
    assert 'type="range"' in page
    assert 'id="pirate"' in page and "every pirate" in page
    # A filter past the pirate's last turn falls back to its last one before.
    assert "n < k && kept(n)" in page
    # The slider keeps to the filter's turns too.
    assert "nearestKept(Number(e.target.value))" in page
    # Play from the end starts again at the filter's first turn.
    assert "nearestKept(0)" in page
    # Playing fast, a turn's steps fit in its time, so a dig always finishes.
    assert 'Number($("speed").value) / (steps + 2)' in page


def test_game_page_steps_play_restarts_at_the_filter_s_last_turn(saved):
    page = viewer.slideshow_page(saved)
    play = page[page.index("function play()") :]
    play = play[: play.index("\n}\n")]
    # Not just at the game's last turn: at the filtered pirate's last one too.
    assert "at >= lastKept()" in play and "at === N - 1" not in play
    assert "const lastKept = () => TURNS.map((t, n) => n).filter(kept)" in page


def test_game_page_steps_a_scroll_during_a_step_moves_the_board_once_it_settles(saved):
    page = viewer.slideshow_page(saved)
    on_scroll = page[page.index("function onScroll(seen)") :]
    on_scroll = on_scroll[: on_scroll.index("\n}\n")]
    # A scroll inside the step's lock isn't dropped: it's looked at once it ends.
    assert "setTimeout(settle, lock - Date.now()" in on_scroll
    settle = page[page.index("function settle()") :]
    assert "inView()" in settle[: settle.index("\n}\n")]


def test_game_page_steps_the_address_keeps_the_turn(saved):
    page = viewer.slideshow_page(saved)
    assert "location.hash" in page and "history.replaceState" in page


def test_game_page_steps_each_turn_holds_its_steps_on_the_board(saved):
    records = viewer.records_in(saved)
    scoring = viewer.scoring_in(saved)
    turns = data_in(viewer.slideshow_page(saved), "TURNS")
    for number, turn in enumerate(turns):
        steps = viewer.turn_steps(records, number, scoring)
        # Every step but the last, which is the turn's own frame.
        assert len(turn["steps"]) == len(steps) - 1
        for encoded, step in zip(turn["steps"], steps, strict=False):
            assert base64.b64decode(encoded) == viewer.board_png(saved, number, step)


def test_game_page_steps_scrolling_the_feed_moves_the_board(saved):
    page = viewer.slideshow_page(saved)
    assert "IntersectionObserver" in page
    # Its band is in pixels from the window's height, kept up on resize.
    assert "innerHeight * 0.45" in page and 'addEventListener("resize", watch)' in page
    assert "scrollIntoView" in page


def test_game_page_steps_the_score_so_far_is_on_each_turn(saved):
    turns = data_in(viewer.slideshow_page(saved), "TURNS")
    assert turns[0]["score"] == 0
    assert turns[-1]["score"] == records_of(saved)[-1]["game_over"]["score"]


def test_scroll_written_live_a_write_turn_types_its_line_with_a_quill(saved):
    page = viewer.slideshow_page(saved)
    game = data_in(page, "GAME")
    assert all(
        re.fullmatch(r"#[0-9a-fA-F]{6}", c["colour"]) for c in game["crew"].values()
    )
    assert "quill" in page and "setInterval" in page


@pytest.mark.parametrize(
    "words", ["</script><script>alert(1)</script> & <b>bold</b>", "<!-- <script>"]
)
def test_game_page_the_feed_puts_every_word_in_as_text(saved, words):
    records = records_of(saved)
    records[0]["saw"]["prompt"] = words
    records[0]["thinking"] = words
    records[0]["did"] = [{"action": "write", "text": words}]
    rewrite(saved, records)
    page = viewer.slideshow_page(saved)
    for name in ("TURNS", "GAME"):
        data = re.search(rf"const {name} = (.*?);\n", page, re.DOTALL).group(1)
        assert "<" not in data
    assert "innerHTML" not in page
