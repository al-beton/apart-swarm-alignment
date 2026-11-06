# Implements: viewer/slideshow-file, treasure-island/slideshow
"""A saved game as one HTML file that steps through its turns with no server."""

import base64
import json
import re
import shutil
import socket
from pathlib import Path

import pytest

from treasure_island import cli, viewer

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def saved(tmp_path, monkeypatch):
    """A copy of a committed game, in a folder of its own."""
    monkeypatch.chdir(tmp_path)
    shutil.copytree(ROOT / "runs/s-sweep-seed-7", tmp_path / "runs/s-sweep-seed-7")
    return tmp_path / "runs/s-sweep-seed-7"


def turns_in(page):
    """The turns the page holds, as its script will read them."""
    found = re.search(r"const TURNS = (.*?);\n", page, re.DOTALL)
    return json.loads(found.group(1))


def records_of(folder):
    lines = (folder / "events.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines]


def test_slideshow_file_one_command_writes_it_next_to_the_run(saved, capsys):
    assert cli.main(["slideshow", str(saved)]) == 0
    written = saved.with_suffix(".html")
    assert written.is_file()
    assert str(written) in capsys.readouterr().out
    assert not (saved / "slideshow.html").exists()


def test_slideshow_file_writes_where_asked(saved, tmp_path):
    out = tmp_path / "elsewhere" / "game.html"
    assert cli.main(["slideshow", str(saved), "--out", str(out)]) == 0
    assert out.is_file()


def test_slideshow_file_holds_the_renderer_s_frame_for_every_turn(saved):
    turns = turns_in(viewer.slideshow_page(saved))
    assert len(turns) == len(records_of(saved))
    for number, turn in enumerate(turns):
        assert base64.b64decode(turn["frame"]) == viewer.frame_png(saved, number)


def test_slideshow_file_holds_every_turn_s_story(saved):
    turns = turns_in(viewer.slideshow_page(saved))
    assert [t["story"] for t in turns] == [r["story"] for r in records_of(saved)]


def test_slideshow_file_a_run_without_stories_still_steps(saved):
    records = records_of(saved)
    for record in records:
        del record["story"]
    (saved / "events.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    assert {t["story"] for t in turns_in(viewer.slideshow_page(saved))} == {""}


def test_slideshow_file_the_arrow_keys_step_through_it(saved):
    page = viewer.slideshow_page(saved)
    assert '"ArrowLeft"' in page
    assert '"ArrowRight"' in page
    assert 'addEventListener("keydown"' in page


def test_slideshow_file_needs_no_server_or_network(saved):
    page = viewer.slideshow_page(saved)
    assert "fetch(" not in page
    assert "<link" not in page
    assert not re.search(r"""(src|href)=["'](?!data:)""", page)
    without_data = re.sub(r"const TURNS = .*?;\n", "", page, flags=re.DOTALL)
    assert "http" not in without_data


def test_slideshow_file_writing_it_opens_no_socket(saved, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("the slideshow opened a socket")

    monkeypatch.setattr(socket, "socket", no_network)
    assert viewer.slideshow(saved).is_file()


@pytest.mark.parametrize(
    "words",
    [
        "</script><script>alert(1)</script> & <b>bold</b>",
        "<!-- <script>",  # an HTML parser would never close the page's own script
    ],
)
def test_slideshow_file_a_pirate_s_words_cannot_break_out_of_the_page(saved, words):
    records = records_of(saved)
    records[0]["story"] = words
    (saved / "events.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    page = viewer.slideshow_page(saved)
    data = re.search(r"const TURNS = (.*?);\n", page, re.DOTALL).group(1)
    assert "<" not in data
    assert turns_in(page)[0]["story"] == words
    # The script puts the story in as text, never as markup.
    assert "innerHTML" not in page


def test_slideshow_file_the_same_game_writes_the_same_bytes(saved):
    assert viewer.slideshow_page(saved) == viewer.slideshow_page(saved)
