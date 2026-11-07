# Implements: treasure-island/side-panel, treasure-island/readable-at-once, viewer/frame-shows-the-swarm
"""A reader follows the game from the frame: who, what they did and why."""

from PIL import Image, ImageChops

from assets.pirates import portrait
from assets.ui import speech_bubble
from treasure_island import viewer
from treasure_island.brain import Decision
from treasure_island.config import parse_config
from treasure_island.game_loop import Game
from treasure_island.game_state import GameState

CREW = {"pirate-1": [0, 0], "pirate-2": [0, 0]}


def drawn_at(image, overlay, position):
    """Whether every solid pixel of `overlay` is in `image` at `position`."""
    x, y = position
    box = (x, y, x + overlay.width, y + overlay.height)
    here = image.crop(box).convert("RGB")
    solid = overlay.getchannel("A").point(lambda value: 255 if value == 255 else 0)
    wanted = Image.composite(overlay.convert("RGB"), here, solid)
    return ImageChops.difference(here, wanted).getbbox() is None


def record(turn, agent="pirate-1", **rest):
    """One record; `did`, `thinking`, `found`, `story` and `at` can be given."""
    at = rest.get("at", [0, 0])
    did = rest.get("did", [{"action": "dig"}])
    made = {
        "turn": turn,
        "agent": agent,
        "saw": {"position": at, "prompt": ""},
        "did": did,
        "log_shown": [],
        "crew": CREW,
        "outcome": {"position": at, "found_treasure": rest.get("found", False)},
    }
    for optional in ("thinking", "story", "happened"):
        if optional in rest:
            made[optional] = rest[optional]
    return made


def shown(records, turn=None):
    turn = len(records) - 1 if turn is None else turn
    return viewer.scene(records, turn, 4)


def panel_of(image, size=4):
    return image.crop((size * viewer.TILE, 0, image.width, image.height))


def test_side_panel_says_what_the_pirate_did_in_plain_words():
    made = record(0, happened="dug at (0, 0) and found nothing.")
    assert shown([made])["did"] == "dug at (0, 0) and found nothing."


def test_side_panel_falls_back_on_the_action_for_a_record_that_does_not_say():
    assert shown([record(0)])["did"] == "dig"


def test_side_panel_shows_a_trail_of_this_pirates_own_thoughts():
    records = [
        record(0, thinking="first"),
        record(1, agent="pirate-2", thinking="not mine"),
        record(2, thinking="second"),
        record(3, agent="pirate-2", thinking="also not mine"),
        record(4, thinking="third"),
        record(6, thinking="fourth"),
    ]
    assert shown(records)["thoughts"] == ["second", "third", "fourth"]


def test_side_panel_a_repeated_thought_shows_once():
    records = [record(0, thinking="same"), record(2, thinking="same")]
    assert shown(records)["thoughts"] == ["same"]


def test_side_panel_the_current_thought_is_always_last():
    thoughts = ["dig", "walk", "dig", "walk", "dig"]
    records = [record(2 * i, thinking=thought) for i, thought in enumerate(thoughts)]
    assert shown(records)["thoughts"] == ["dig", "walk", "dig"]


def test_side_panel_never_shows_a_thought_from_a_later_turn():
    records = [record(0, thinking="now"), record(2, thinking="later")]
    assert shown(records, 0)["thoughts"] == ["now"]


def test_side_panel_shows_the_pirates_portrait():
    look = (5, "#2f6fc0", "AN")
    pirates = {"pirate-1": look, "pirate-2": (6, "#c8403c", "MA")}
    image = viewer.frame([record(0)], 0, 4, pirates)
    x, y = viewer.PORTRAIT
    assert drawn_at(image, portrait(*look), (4 * viewer.TILE + x, y))


def test_side_panel_changes_as_the_thought_does():
    first = viewer.frame([record(0, thinking="one idea")], 0, 4)
    second = viewer.frame([record(0, thinking="another idea")], 0, 4)
    assert ImageChops.difference(panel_of(first), panel_of(second)).getbbox()


def test_side_panel_wraps_long_words_rather_than_cutting_them_off():
    long = "a thought that goes on for a very long way " * 3
    lines = viewer.wrapped(long)
    assert " ".join(lines) == " ".join(long.split())
    assert all(len(line) <= viewer.PANEL_COLUMNS for line in lines)


def test_side_panel_draws_text_the_pixel_font_does_not_have():
    records = [
        record(0, did=[{"action": "write", "text": "héllo 日本 🏴"}], thinking="é")
    ]
    assert viewer.frame(records, 0, 4).size


def test_side_panel_fits_whatever_is_said_inside_the_frame():
    wall = "word " * 200
    records = [record(0, thinking=wall, happened=f'wrote "{wall}".')]
    image = viewer.frame(records, 0, 1)
    assert image.height == viewer.frame([record(0)], 0, 1).height


def test_readable_at_once_the_winning_turn_says_so():
    found = record(0, found=True)
    assert shown([found])["bubble"] == "I found the treasure!"


def test_readable_at_once_a_note_is_the_pirates_own_words_in_a_bubble():
    note = record(0, did=[{"action": "write", "text": "Over here, crew!"}])
    assert shown([note])["bubble"] == "Over here, crew!"


def test_readable_at_once_the_bubble_is_the_art_not_a_shape():
    image = viewer.frame([record(0, found=True, at=[3, 3])], 0, 4)
    bubble = speech_bubble("I found the treasure!")
    assert drawn_at(image, bubble, viewer.bubble_box((3, 3), bubble.size, 4))


def test_readable_at_once_the_bubble_stays_on_the_board():
    for square in ((0, 0), (3, 0), (0, 3), (3, 3)):
        x, y = viewer.bubble_box(square, (150, 60), 4)
        assert 0 <= x and x + 150 <= 4 * viewer.TILE
        assert 0 <= y


def test_readable_at_once_a_bubble_with_no_room_above_goes_below_the_pirate():
    _, top = viewer.bubble_box((0, 0), (60, 30), 4)
    assert top == viewer.TILE + viewer.ARROW_ROOM + 2  # below the arrow under its feet
    _, top = viewer.bubble_box((0, 3), (60, 30), 4)
    assert top == 3 * viewer.TILE - viewer.ARROW_ROOM - 30  # above the turn arrow


def test_readable_at_once_a_real_game_tells_its_ending_in_the_frame():
    class Dig:
        def decide(self, view):
            return Decision({"action": "dig"}, "Digging right here.")

    # Seed 2 buries the treasure in the corner where the only pirate starts.
    assert GameState(5, 1, 2).treasure == (0, 0)
    config = parse_config({"grid_size": 5, "crew_size": 1, "seed": 2})
    records = list(Game(config, [Dig()]).records())
    last = shown(records)
    assert last["bubble"] == "I found the treasure!"
    assert "found the treasure" in last["did"]
    assert last["thoughts"] == ["Digging right here."]
