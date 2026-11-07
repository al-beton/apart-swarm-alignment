# Implements: assets/plain-files, assets/remade-by-one-command, assets/game-size, assets/any-pirate, assets/charming-personalities, assets/label-on-hat, assets/four-directions, assets/actions-shown, assets/ground-tiles, assets/treasure-shown, assets/viewer-parts, assets/sheet-shows-everything, assets/catwalk
"""The art is what the spec says, and the committed images match the code."""

import re
from functools import cache
from pathlib import Path

import pytest
from PIL import Image

from assets import generate
from assets.catwalk import GROUND, LOOP, catwalk_frames, catwalk_gif, ground, walk
from assets.font import CHARS, FONT_HEIGHT, text_width
from assets.generate import build
from assets.pirates import (
    DEFAULT_COLOURS,
    FACINGS,
    PERSONALITIES,
    pirate,
    portrait,
)
from assets.pixels import SIZE
from assets.tiles import TILES
from assets.treasure import ITEMS
from assets.ui import panel, speech_bubble

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CREAM = (255, 244, 214, 255)
DARK = (42, 26, 40, 255)


def same(a, b):
    return a.convert("RGBA").tobytes() == b.convert("RGBA").tobytes()


def test_plain_files_are_pngs_the_guide_names():
    images = build()
    guide = (ASSETS / "README.md").read_text()
    folders = {name.split("/")[0] for name in images}
    for folder in folders:
        assert f"`{folder}/" in guide or f"`{folder}" in guide, folder
    assert all(name.endswith(".png") for name in images)


def test_remade_by_one_command_committed_images_match_the_code():
    images = build()
    for name, image in images.items():
        path = ASSETS / name
        assert path.is_file(), f"{name} is missing: run make assets"
        with Image.open(path) as committed:
            assert same(committed, image), f"{name} is stale: run make assets"
    committed = {p.relative_to(ASSETS).as_posix() for p in ASSETS.rglob("*.png")}
    assert committed == set(images), "remove images the code no longer draws"


def test_game_size_tiles_and_sprites_are_48px():
    assert SIZE == 48
    assert pirate(1, "#c8403c", "7").size == (48, 48)
    assert all(make().size == (48, 48) for make in TILES.values())
    assert all(make().size == (48, 48) for make in ITEMS.values())


def test_any_pirate_takes_any_personality_colour_and_label():
    red = pirate(1, "#c8403c", "7")
    assert not same(red, pirate(1, "#2f6fc0", "7"))
    assert not same(red, pirate(2, "#c8403c", "7"))
    assert not same(red, pirate(1, "#c8403c", "8"))
    assert same(pirate(1, "#c8403c", "ab"), pirate(1, "#c8403c", "AB"))
    assert len(DEFAULT_COLOURS) == 20


@pytest.mark.parametrize("label", ["ABC", "!"])
def test_any_pirate_refuses_a_label_that_will_not_fit(label):
    with pytest.raises(ValueError):
        pirate(1, "#c8403c", label)


def test_charming_personalities_are_twenty_and_all_different():
    assert sorted(PERSONALITIES) == list(range(1, 21))
    drawn = [pirate(p, "#c8403c").tobytes() for p in PERSONALITIES]
    assert len(set(drawn)) == 20


@pytest.mark.parametrize("colour", ["#ffffff", "#111111", "#ffe94a", "#808080"])
def test_label_on_hat_is_dark_on_cream_whatever_the_colour(colour):
    colours = {c for _, c in pirate(1, colour, "8").getcolors(4096)}
    assert CREAM in colours
    assert DARK in colours


def test_label_on_hat_stays_put_from_every_direction():
    def blob(facing):
        return pirate(1, "#c8403c", "12", facing).crop((16, 3, 32, 15))

    assert all(same(blob("down"), blob(facing)) for facing in FACINGS)


def test_four_directions_each_walk_with_three_frames():
    assert set(FACINGS) == {"down", "up", "left", "right"}
    for facing in FACINGS:
        frames = [pirate(1, "#c8403c", "", facing, f).tobytes() for f in range(3)]
        assert len(set(frames)) == 3, facing
    assert len({pirate(1, "#c8403c", "", f).tobytes() for f in FACINGS}) == 4


@pytest.mark.parametrize("pose", ["dig", "cheer"])
def test_actions_shown_digging_and_cheering_differ_from_standing(pose):
    stand = pirate(1, "#c8403c")
    frames = [pirate(1, "#c8403c", "", pose, f) for f in range(2)]
    assert not same(frames[0], frames[1])
    assert not any(same(stand, frame) for frame in frames)


def test_ground_tiles_are_opaque_and_look_different():
    assert {"sand", "grass", "dug", "water", "sinking-sand"} <= set(TILES)
    drawn = {name: make() for name, make in TILES.items()}
    for name, tile in drawn.items():
        assert tile.getextrema()[3] == (255, 255), name
    assert len({tile.tobytes() for tile in drawn.values()}) == len(drawn)


def test_treasure_shown_a_question_mark_marks_it_until_it_is_dug_up():
    assert "mark-question" in ITEMS
    assert "mark-x" not in ITEMS  # once dug up, the square is the cave
    assert ITEMS["mark-question"]().getextrema()[3][0] == 0


def test_viewer_parts_bubble_fits_its_text():
    short = speech_bubble("Hi")
    long = speech_bubble("I'll search row 1, then row 2, then we check in.")
    assert long.width > short.width or long.height > short.height
    assert short.height >= FONT_HEIGHT
    assert speech_bubble("x" * 200, max_width=160).width <= 160


def test_viewer_parts_panel_stretches_to_any_size():
    assert panel(200, 300).size == (200, 300)
    assert panel(480, 96).size == (480, 96)


def test_viewer_parts_font_covers_printable_ascii():
    assert set(CHARS) >= {chr(c) for c in range(32, 127)}
    assert text_width("ab") == 2 * text_width("a")


def test_viewer_parts_portrait_is_the_head_enlarged():
    assert portrait(1, "#c8403c", "7").size == (96, 64)


def test_sheet_shows_everything_is_committed_and_wide_enough():
    with Image.open(ASSETS / "sheet.png") as sheet:
        assert sheet.width >= 480
    assert "sheet.png" in build()


def test_catwalk_every_pirate_walks_in_all_four_directions():
    steps = {
        number: [walk(number, step) for step in range(LOOP)] for number in PERSONALITIES
    }
    assert len(steps) == 20
    moves = {"right": (1, 0), "down": (0, 1), "left": (-1, 0), "up": (0, -1)}
    for path in steps.values():
        assert {pose for pose, _, _ in path} == set(FACINGS)
        assert {frame for _, frame, _ in path} == {0, 1, 2}
        # Each step goes the way the pirate faces, and the loop closes.
        for (pose, _, here), (_, _, there) in zip(
            path, [*path[1:], path[0]], strict=True
        ):
            dx, dy = there[0] - here[0], there[1] - here[1]
            sign = (dx > 0) - (dx < 0), (dy > 0) - (dy < 0)
            assert sign == moves[pose] or sign == (0, 0)


def test_catwalk_pirates_keep_to_their_own_patch_of_ground():
    spots = [
        {tuple(walk(number, step)[2]) for step in range(LOOP)}
        for number in PERSONALITIES
    ]
    for a in range(len(spots)):
        for b in range(a + 1, len(spots)):
            for ax, ay in spots[a]:
                for bx, by in spots[b]:
                    assert abs(ax - bx) >= SIZE or abs(ay - by) >= SIZE


def test_catwalk_crosses_a_sample_of_walkable_tiles():
    assert len(GROUND) >= 3
    assert {"sand", "grass", "dug"} <= set(GROUND)
    assert not {"water", "water-2", "sinking-sand"} & set(GROUND)
    assert set(GROUND) <= set(TILES)
    board = ground()
    colours = {
        board.crop((x, 0, x + SIZE, SIZE)).tobytes() for x in range(0, SIZE * 5, SIZE)
    }
    assert len(colours) >= 3


@cache
def built_gif():
    """Building it takes a second or two, so the tests share one."""
    return catwalk_gif()


def test_catwalk_gif_shows_exactly_what_was_drawn(tmp_path):
    path = tmp_path / "catwalk.gif"
    path.write_bytes(built_gif())
    with Image.open(path) as gif:
        assert gif.format == "GIF"
        assert gif.n_frames == LOOP
        assert gif.info["loop"] == 0
        for index, drawn in enumerate(catwalk_frames()):
            gif.seek(index)
            assert same(gif, drawn), f"frame {index}"


def test_catwalk_is_deterministic_and_the_committed_gif_matches_the_code():
    assert built_gif() == catwalk_gif()
    committed = (ASSETS / "catwalk.gif").read_bytes()
    assert committed == built_gif(), "stale: run make catwalk"


def test_catwalk_is_under_two_megabytes():
    assert (ASSETS / "catwalk.gif").stat().st_size < 2_000_000


def test_catwalk_make_catwalk_and_make_assets_both_write_it(tmp_path, monkeypatch):
    makefile = (ROOT / "Makefile").read_text()
    assert re.search(
        r"^catwalk:.*\n\tuv run python -m assets\.catwalk$", makefile, re.MULTILINE
    )
    monkeypatch.setattr(generate, "ASSETS", tmp_path)
    generate.main()
    assert (tmp_path / "catwalk.gif").read_bytes() == built_gif()
    assert (tmp_path / "sheet.png").is_file()
