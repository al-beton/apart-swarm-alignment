# Implements: treasure-island/treasure-mark, treasure-island/log-at-bottom, viewer/long-log-lines
"""What only the reader sees: the mark on the treasure square, and the crew's log."""

import shutil
from pathlib import Path

import pytest
from PIL import Image

from treasure_island import viewer
from treasure_island.brain import Decision
from treasure_island.config import parse_config
from treasure_island.game_loop import Game, write_game
from treasure_island.pirates_log import PiratesLog

ROOT = Path(__file__).resolve().parents[1]
SAVED = ROOT / "runs/s-sweep-seed-7"
CREW = {"pirate-1": [0, 0]}


def record(turn, did=(), found=False, position=(0, 0), **rest):
    return {
        "turn": turn,
        "agent": "pirate-1",
        "saw": {"position": list(position), "prompt": "x"},
        "did": list(did),
        "log_shown": [],
        "crew": CREW,
        "outcome": {"position": list(position), "found_treasure": found},
        **rest,
    }


def over(treasure):
    return {"treasure": list(treasure), "treasure_dug_up": False}


def square(image, x, y):
    box = (x * viewer.TILE, y * viewer.TILE)
    return image.crop((*box, box[0] + viewer.TILE, box[1] + viewer.TILE))


def art(name):
    return Image.open(viewer.ASSETS / f"{name}.png").convert("RGBA")


def shows(image, x, y, mark, ground_names):
    """Whether the square is exactly this mark on one of these ground tiles."""
    shown = square(image, x, y).convert("RGB").tobytes()
    for name in ground_names:
        ground = art(f"tiles/{name}").copy()
        ground.alpha_composite(art(f"treasure/{mark}"))
        if ground.convert("RGB").tobytes() == shown:
            return True
    return False


@pytest.fixture
def saved(tmp_path):
    folder = tmp_path / "game"
    shutil.copytree(SAVED, folder)
    return folder


def records_of(folder):
    return viewer.records_in(folder)


def test_treasure_mark_a_question_mark_from_the_start():
    records = [record(0), record(1, game_over=over((2, 2)))]
    image = viewer.frame(records, 0, 3)
    assert shows(image, 2, 2, "mark-question", viewer.SAND_TILES)


def test_treasure_mark_an_x_once_it_is_dug_up_and_never_before():
    dig = [{"action": "dig"}]
    records = [
        record(0, position=(2, 2)),
        record(1, dig, found=True, position=(2, 2)),
        record(2, [{"action": "move", "direction": "west"}], position=(1, 2)),
    ]
    assert viewer.scene(records, 0, 3, (2, 2))["mark"] == ("mark-question", (2, 2))
    assert viewer.scene(records, 1, 3, (2, 2))["mark"] == ("mark-x", (2, 2))
    image = viewer.frame(records, 2, 3, None, (2, 2))
    assert shows(image, 2, 2, "mark-x", ["dug"])


def seen_share(image, x, y, mark):
    """How much of a mark's opaque art actually reaches the frame at this square."""
    art_mark = art(f"treasure/{mark}")
    shown = square(image, x, y).convert("RGB")
    opaque = [
        (px, py)
        for px in range(viewer.TILE)
        for py in range(viewer.TILE)
        if art_mark.getpixel((px, py))[3] == 255
    ]
    same = sum(shown.getpixel(spot) == art_mark.getpixel(spot)[:3] for spot in opaque)
    return same / len(opaque)


@pytest.mark.parametrize("crew", [1, 3, 6])
def test_treasure_mark_the_x_shows_over_the_crew_standing_on_it(crew):
    """Digging it up is the moment a reader most wants to see."""
    names = [f"pirate-{n + 1}" for n in range(crew)]
    dug_up = {
        **record(0, [{"action": "dig"}], found=True, position=(1, 1)),
        "agent": names[0],
        "crew": {name: [1, 1] for name in names},
    }
    image = viewer.frame([dug_up], 0, 3).convert("RGB")
    assert seen_share(image, 1, 1, "mark-x") > 0.5


def test_treasure_mark_a_finished_game_says_where_it_is(saved):
    records = records_of(saved)
    assert viewer.treasure_in(saved, records) == (2, 1)
    (saved / "config.json").unlink()
    assert viewer.treasure_in(saved, records) == (2, 1)


def test_treasure_mark_a_game_still_being_played_has_it_from_its_config(saved):
    assert viewer.treasure_in(saved, records_of(saved)[:3]) == (2, 1)


def test_treasure_mark_a_run_that_does_not_say_shows_no_question_mark(tmp_path):
    assert viewer.treasure_in(tmp_path, [record(0)]) is None
    assert viewer.scene([record(0)], 0, 3)["mark"] is None


class Quiet:
    """Writes every turn, so the game never turns on where the treasure is."""

    def __init__(self):
        self.texts = []

    def decide(self, view):
        self.texts.append(view.as_text())
        return Decision({"action": "write", "text": "here"})


def views(tmp_path, seed):
    folder = tmp_path / f"seed-{seed}"
    folder.mkdir()
    config = parse_config({"grid_size": 6, "crew_size": 1, "seed": seed})
    brain = Quiet()
    write_game(config, [brain], folder)
    return brain.texts, Game(config, [Quiet()]).state.treasure


def test_treasure_mark_the_pirates_never_see_either_mark(tmp_path):
    first, treasure = views(tmp_path, 1)
    second, other = views(tmp_path, 2)
    assert treasure != other
    assert first == second  # so nothing in a view depends on where it is
    for text in first:
        assert "mark" not in text.lower()
        assert "?" not in text


def test_log_at_bottom_shows_exactly_the_log_the_crew_had():
    file = (SAVED / "pirates-log.txt").read_text().splitlines()
    records = records_of(SAVED)
    lines = viewer.scene(records, len(records) - 1, 5)["log_so_far"]
    assert [f"{n}: {text}".rstrip() for n, text in lines] == file


def test_log_at_bottom_holds_only_the_lines_written_so_far():
    written = [{"action": "write", "text": "ahoy"}]
    records = [record(0, written), record(1), record(2, written)]
    assert viewer.scene(records, 1, 3)["log_so_far"] == [(1, "ahoy"), (2, "")]


def test_log_at_bottom_a_note_on_two_lines_reads_as_it_did_in_the_log():
    written = [{"action": "write", "text": "first\nsecond"}]
    log = PiratesLog()
    log.write(written[0]["text"])
    assert viewer.scene([record(0, written)], 0, 3)["log_so_far"] == [
        (1, log.lines()[0]["text"])
    ]


def test_log_at_bottom_runs_along_under_the_board_at_a_fixed_height():
    written = [{"action": "write", "text": "ahoy"}]
    records = [record(turn, written) for turn in range(30)]
    first = viewer.frame(records, 0, 3)
    last = viewer.frame(records, 29, 3)
    assert first.size == last.size
    below = first.height - viewer.STRIP
    assert below >= 3 * viewer.TILE
    strip_of = lambda image: image.crop((0, below, image.width, image.height))
    assert strip_of(first).tobytes() != strip_of(last).tobytes()


def test_long_log_lines_a_note_too_long_for_the_strip_shows_its_end():
    words = [f"word{n}" for n in range(200)]
    rows = viewer.log_rows([(1, " ".join(words))], width=300)
    assert len(rows) == viewer.STRIP_ROWS
    assert rows[-1].split()[-1] == "word199"


def test_long_log_lines_wrap_and_lose_no_word():
    words = [f"word{n}" for n in range(15)]
    rows = viewer.log_rows([(1, " ".join(words))], width=300)
    assert len(rows) > 1
    assert " ".join(rows).split() == ["1:", *words]
    assert all(viewer.text_width(row) <= 300 for row in rows)


def test_long_log_lines_a_word_too_long_for_a_row_is_split_not_cut():
    long = "x" * 200
    rows = viewer.log_rows([(1, long)], width=300)
    assert "".join(rows).removeprefix("1:") == long
    assert all(viewer.text_width(row) <= 300 for row in rows)


def test_long_log_lines_keep_the_newest_in_view():
    lines = [(n, f"line {n}") for n in range(1, 40)]
    rows = viewer.log_rows(lines, width=300)
    assert len(rows) == viewer.STRIP_ROWS
    assert rows[-1] == "39: line 39"
