"""Drawing a run: one renderer behind the browser page and the GIF.

Everything visual reads `events.jsonl` and nothing else, so a frame can be
drawn while the game is still writing. `scene` turns the records up to a turn
into what a frame shows: the grid size, where every pirate stands (from the
turn's `crew`, so pirates that haven't acted yet are there too), whose turn
it is, what it said and the log lines it saw, and under the board the turn's line of
the story, word for word, so a frame and the log can be matched up. `frame` draws that scene with
Pillow. The browser page asks for `/frame/<turn>.png` and the GIF strings the
same PNGs together, which is what keeps the two from ever disagreeing.

Tiles and marks are the PNGs in `assets/`, and a pirate is `pirate()` from the art,
since a config can ask for any colour. There is no plain shape to fall back on, so
missing art is an error. A pirate's looks come from the run's `config.json`, or the
default crew's when it doesn't say. They only pick the sprite: the game never sees
them.

The side panel is the art's parchment with the acting pirate's portrait, what it did
in plain words and a trail of its recent thoughts, all wrapped to fit: a reader should
be able to follow the game from the frames alone.

A pirate that moves walks there: its turn gets `WALK_FRAMES` frames, steps 1 to
`WALK_FRAMES`, with the pirate a step further along each, and the last step is the
turn's own frame. A dig plays out over `DIG_STEPS` the same way, and a pirate going
into the cave over `ENTER_STEPS`. `turn_steps` says which steps a turn has, and the
GIF and the page both draw exactly those.

The board is drawn in board pixels and set into the art's wooden frame at
`(EDGE_LEFT, 0)`, whose letters and numbers name the squares like a chessboard.

The game page (`slideshow_page`) is a feed: on the left `board`, the board alone
with no note, and the scroll as parchment; on the right one entry for every turn
`planned_turns` lists, each played turn's steps drawn ahead so stepping onto it
plays them.

Implements: viewer/board-pinned, viewer/autoplay, viewer/game-page-intro, viewer/leak-marked, viewer/reasoning-gist, viewer/scroll-heading, viewer/scroll-numbers, treasure-island/asked-why, treasure-island/old-scroll, treasure-island/end-report, viewer/planned-turns, viewer/game-page-steps, viewer/scroll-written-live, viewer/cave-drawn, treasure-island/cave, viewer/turn-marked, viewer/story-caption, treasure-island/side-panel, treasure-island/readable-at-once, event-log/crew-positions, viewer/one-renderer, viewer/frame-shows-the-swarm, viewer/watch-live, viewer/render-gif, viewer/art-folder, viewer/sprite-from-definition, viewer/sprite-follows-action, viewer/walks-between-squares, treasure-island/pokemon-style, viewer/slideshow-file, viewer/game-page, viewer/scroll-steps, viewer/score-counter, viewer/transcript, viewer/board-framed, viewer/dig-steps, viewer/enter-steps, treasure-island/slideshow, viewer/long-log-lines, treasure-island/treasure-mark, treasure-island/log-at-bottom, runs/same-in-every-process, treasure-island/square-names, treasure-island/forced-discovery, treasure-island/free-talk
"""

import base64
import io
import json
import re
from functools import cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageChops, ImageDraw

import assets
from assets.board import EDGE_BOTTOM, EDGE_LEFT, board_edges
from assets.cave import ENTER_STEPS, entering, hat_stack
from assets.dig import DIG_STEPS, dig_ground, digging
from assets.font import draw_text, text_width, wrap
from assets.pirates import pirate, portrait
from assets.pixels import DARK
from assets.ui import panel, scroll_note
from treasure_island.config import DEFAULTS, parse_config
from treasure_island.game_state import GameState
from treasure_island.judge import exploit_turns
from treasure_island.looks import sprite_values
from treasure_island.old_scroll import FORCED_READ, OFFSET
from treasure_island.pirates_log import one_line, written
from treasure_island.prompts import NONE, ROOT

ASSETS = Path(assets.__file__).parent
SAND_TILES = ("sand", "sand-2", "sand-3")
TILE = 48
# Where a label sits on a sprite: (left, top, right, bottom).
_LABEL_BOX = (14, 2, 34, 16)
# The gap a note keeps above a pirate's hat, so it never covers the label.
ARROW_ROOM = 14
_FACING = {"north": "up", "south": "down", "east": "right", "west": "left"}
PANEL = 260
PANEL_COLUMNS = 38
PANEL_HEIGHT = 320
PORTRAIT = (14, 32)
_PANEL_LEFT = 14
_TEXT_LEFT = 118
THOUGHTS = 3
LINE = 12
_DID_LINES = 3
THOUGHT_ROWS = 6  # the panel's rows for thinking, at the font's normal size
ACTION_INK = DARK  # what a pirate did is the strongest text in the panel
THOUGHT_INK = "#78727a"  # its thinking, softer (the art's muted grey; Al to confirm)
_NOTE_CHARACTERS = 90
STRIP_TITLE = "The scroll"
STRIP_ROWS = 5
STRIP = 24 + (STRIP_ROWS + 1) * LINE + 4  # the parchment's edges, a heading and rows
_STRIP_LEFT = 14
_CAPTION_ROWS = 2  # the least a caption keeps room for
FRAME_MS = 600
WALK_FRAMES = 4  # frames a move takes, its landing included (default, Al to confirm)
WALK_MS = 120  # how long each in-between frame shows
_PLACES_THE_TREASURE = ("grid_size", "crew_size", "seed")


def records_in(folder):
    """Every record in the run's event log so far."""
    lines = (Path(folder) / "events.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def grid_size(folder, records):
    """The grid size from config.json, or the widest position seen plus one."""
    config = Path(folder) / "config.json"
    if config.exists():
        return json.loads(config.read_text())["grid_size"]
    spots = [r["saw"]["position"] for r in records]
    spots += [r["outcome"]["position"] for r in records]
    return max((max(x, y) for x, y in spots), default=0) + 1


def crew_names(records):
    """Every pirate's name, in crew order."""
    names = list(records[0].get("crew", {})) if records else []
    for record in records:
        if record["agent"] not in names:
            names.append(record["agent"])
    return names


def _default_pirates(names):
    crew = parse_config({"crew_size": len(names)}).pirates
    return {name: sprite_values(p) for name, p in zip(names, crew, strict=True)}


def pirates_in(folder, records):
    """What each pirate's sprite is made from, as `pirate()` takes it."""
    names = crew_names(records)
    config = Path(folder) / "config.json"
    saved = json.loads(config.read_text()).get("pirates") if config.exists() else None
    if saved is None:
        return _default_pirates(names)
    crew = parse_config({"pirates": saved}).pirates
    return {name: sprite_values(p) for name, p in zip(names, crew, strict=True)}


def _poses(records, turn):
    """Each pirate's (pose, walking frame) on this turn."""
    facing = {}
    for record in records[: turn + 1]:
        for action in record["did"]:
            if action["action"] == "move":
                facing[record["agent"]] = _FACING[action["direction"]]
    poses = {agent: (pose, 0) for agent, pose in facing.items()}
    current = records[turn]
    # Its own turns, not the game's: a pirate's every turn may be even in a crew of two.
    step = sum(r["agent"] == current["agent"] for r in records[: turn + 1]) - 1
    done = {action["action"] for action in current["did"]}
    if "move" in done:
        poses[current["agent"]] = (facing[current["agent"]], 1 + step % 2)
    elif "dig" in done:
        found = current["outcome"]["found_treasure"]
        poses[current["agent"]] = ("cheer" if found else "dig", step % 2)
    for name in crew_names(records):
        poses.setdefault(name, ("down", 0))
    return poses


def _dug(records, turn):
    return {
        tuple(record["saw"]["position"])
        for record in records[: turn + 1]
        if any(action["action"] == "dig" for action in record["did"])
    }


def _note(record):
    """What a pirate wrote on its turn, or None: only writing is drawn over a pirate."""
    words = [a["text"] for a in record["did"] if a["action"] == "write"]
    return " ".join(words) if words else None


def _reading(record):
    """Whether the turn read the scroll; what it read is never drawn."""
    return any(action["action"] == "read" for action in record["did"])


def _said(record):
    """A turn in plain words, for a record that doesn't say what happened."""
    if record["outcome"]["found_treasure"]:
        return "I found the treasure!"
    words = [a["text"] for a in record["did"] if a["action"] == "write"]
    if words:
        return " ".join(words)
    actions = []
    for action in record["did"]:
        if action["action"] == "move":
            actions.append(f"move {action['direction']}")
        elif action["action"] == "read":
            actions.append("read the scroll")
        else:
            actions.append(action["action"])
    return ", ".join(actions) or "..."


def _did(record):
    """What the turn did in plain words, as the game says it."""
    return record.get("happened") or _said(record)


def _thoughts(records, turn):
    """This pirate's own latest thoughts, oldest first, the current one last.

    Only a thought repeated turn after turn collapses: one it comes back to counts again.
    """
    agent = records[turn]["agent"]
    thoughts = []
    for record in records[: turn + 1]:
        thought = record.get("thinking")
        if record["agent"] == agent and thought:
            thought = " ".join(thought.split())
            if not thoughts or thoughts[-1] != thought:
                thoughts.append(thought)
    return thoughts[-THOUGHTS:]


def treasure_in(folder, records):
    """The treasure's square for the reader's mark, or None if the run doesn't say.

    A finished game's last record says. A game still being played has it from its
    config, since the seed places it. Only the viewer asks: pirates never see it.
    """
    game_over = records[-1].get("game_over") if records else None
    if game_over:
        return tuple(game_over["treasure"])
    path = Path(folder) / "config.json"
    saved = json.loads(path.read_text()) if path.exists() else {}
    if any(field not in saved for field in _PLACES_THE_TREASURE):
        return None
    return GameState(*(saved[field] for field in _PLACES_THE_TREASURE)).treasure


def _log_so_far(records, turn, first=1):
    """The scroll as it stands after `turn`: only a note adds a line to it."""
    return [
        (line["line"], f"{line['by']}: {line['text']}")
        for wrote in _scroll_writes(records[: turn + 1], first)
        for line in wrote
    ]


def _mark(records, treasure, found):
    """What the reader sees on the treasure's square: the cave once dug, else a `?`."""
    if found:
        return ("cave", tuple(found))
    known = treasure
    if known is None and records and records[-1].get("game_over"):
        known = tuple(records[-1]["game_over"]["treasure"])
    return ("mark-question", tuple(known)) if known else None


def _walk(record):
    """Where a turn's pirate walked from and to, or None if it stayed put."""
    start, end = record["saw"]["position"], record["outcome"]["position"]
    moved = any(action["action"] == "move" for action in record["did"])
    return (start, end) if moved and list(start) != list(end) else None


SCROLL_STEPS = {"read": 2, "write": 3}  # frames of the reading and writing poses


def _motion(record):
    """What a turn plays out and in how many steps: a walk, a dig, going in, or none."""
    if _walk(record):
        return "walk", WALK_FRAMES
    if record["outcome"].get("in_cave"):
        return "enter", ENTER_STEPS
    if any(action["action"] == "dig" for action in record["did"]):
        return "dig", DIG_STEPS
    for kind, steps in SCROLL_STEPS.items():  # the held scroll's frames (assets)
        if any(action["action"] == kind for action in record["did"]):
            return kind, steps
    return None, 1


def turn_steps(records, turn, scoring=None):
    """The steps a turn is drawn in: 1 to N for a walk, dig, read, write or going in.

    The last turn of a finished game that still owes pirates inside their turns
    plays them out first: after its own steps, one step per round, then its own frame.
    """
    steps = _motion(records[turn])[1]
    owed = len(_owed_rounds(records, turn, scoring))
    if not owed:
        return list(range(1, steps + 1)) if steps > 1 else [None]
    return [*range(1, steps + owed), None]  # its last step plays the first round out


def _walking(shown, record, step):
    """Put the turn's pirate `step` of the way along its walk, on its walking feet."""
    (sx, sy), (ex, ey) = _walk(record)
    part = step / WALK_FRAMES
    agent = record["agent"]
    shown["positions"][agent] = [sx + (ex - sx) * part, sy + (ey - sy) * part]
    pose, feet = shown["poses"][agent]
    # Feet alternate frame by frame and land on the turn's own.
    shown["poses"][agent] = (pose, feet if (WALK_FRAMES - step) % 2 == 0 else 3 - feet)
    return shown


class Scoring(NamedTuple):
    """The run's numbers from its config: the score's, as the counter needs them,
    and the scroll's first line number (`scroll-numbers`)."""

    turns_per_pirate: int
    in_cave: int
    per_turn_left: int
    first_line: int = 1


_DEFAULT_SCORING = Scoring(
    DEFAULTS["turns_per_pirate"],
    DEFAULTS["score_in_cave"],
    DEFAULTS["score_per_turn_left"],
)
SCORE_INK = "#ffd23f"  # what the crew earns, in the cave's gold (Al to confirm)


def scoring_in(folder):
    """The run's score numbers: as its event log records them, else as config.json
    says, else the defaults it would have had.

    A finished game's last record holds them, so a run viewed from its event log
    alone counts by them too; a game still being played has a config beside it.
    """
    fields = ("turns_per_pirate", "score_in_cave", "score_per_turn_left")
    events = Path(folder) / "events.jsonl"
    records = records_in(folder) if events.exists() else []
    recorded = (
        records[-1].get("game_over", {}).get("score_numbers") if records else None
    )
    path = Path(folder) / "config.json"
    saved = json.loads(path.read_text()) if path.exists() else {}
    first = OFFSET if saved.get("old_scroll") else 1
    if recorded:
        return Scoring(*(recorded[field] for field in fields), first)
    return Scoring(*(saved.get(field, DEFAULTS[field]) for field in fields), first)


def _passed(seat, before, now, crew):
    """Whether the turn order went past `seat` going from seat `before` to `now`."""
    gap = (now - before) % crew or crew  # the same seat again is a whole round
    return 0 < (seat - before) % crew < gap


def score_gains(records, scoring):
    """The points each turn earned, and the rounds of points still owed at the end.

    A pirate going in earns `in_cave`. After that, each time the turn order passes
    its seat it earns `per_turn_left`, for as many turns as it had left. A game that
    ends first still owes it the rest, which the last turn plays out in rounds.
    """
    seats = {name: index for index, name in enumerate(crew_names(records))}
    used, owed, gains, before = {}, {}, [], None
    for record in records:
        name, earned = record["agent"], []
        for inside, left in owed.items():
            if left and _passed(seats[inside], before, seats[name], len(seats)):
                owed[inside] -= 1
                earned.append(scoring.per_turn_left)
        used[name] = used.get(name, 0) + 1  # every record is one turn used
        if record["outcome"].get("in_cave"):
            owed[name] = max(scoring.turns_per_pirate - used[name], 0)
            earned.append(scoring.in_cave)
        gains.append(earned)
        before = seats[name]
    rounds = []
    while any(owed.values()):
        rounds.append([scoring.per_turn_left for left in owed.values() if left])
        owed = {inside: max(left - 1, 0) for inside, left in owed.items()}
    return gains, rounds


def _owed_rounds(records, turn, scoring):
    """The rounds the last turn of a finished game plays out, else none."""
    if turn != len(records) - 1 or not records[turn].get("game_over"):
        return []
    return score_gains(records, scoring or _DEFAULT_SCORING)[1]


def _score_now(records, turn, step, scoring):
    """The count on this step of this turn, and the gains rising from the cave."""
    gains, rounds = score_gains(records, scoring)
    score = sum(sum(earned) for earned in gains[: turn + 1])
    labels = gains[turn]
    if _owed_rounds(records, turn, scoring):
        steps = _motion(records[turn])[1]
        played = len(rounds) if step is None else step - (steps - 1)
        if played > 0:
            score += sum(sum(owed) for owed in rounds[:played])
            labels = rounds[played - 1] if step is not None else labels
    return score, [f"+{points}" for points in labels]


# One argument over the limit: `scoring` sits beside the others every caller passes.
def scene(records, turn, size, treasure=None, step=None, scoring=None):  # noqa: PLR0913
    """What the frame for `turn` shows, from the records up to and including it.

    `step`, one of `turn_steps`, is how far along its walk, dig or way into the cave
    the turn's pirate is drawn.
    """
    positions = dict(records[turn].get("crew", {}))
    for record in records:
        positions.setdefault(record["agent"], record["saw"]["position"])
    found = None
    for record in records[: turn + 1]:
        positions[record["agent"]] = record["outcome"]["position"]
        if record["outcome"]["found_treasure"]:
            found = record["outcome"]["position"]
    inside = []  # who has gone into the cave before this turn, first in first
    for record in records[:turn]:
        if record["outcome"].get("in_cave"):  # gone in: it has left the board
            positions.pop(record["agent"], None)
            inside.append(record["agent"])
    current = records[turn]
    going = current["agent"] if current["outcome"].get("in_cave") else None
    shown = {
        "size": size,
        "turn": turn,
        "positions": positions,
        "acting": current["agent"],
        "note": _note(current),
        "did": _did(current),
        "thoughts": _thoughts(records, turn),
        "reading": _reading(current),
        "treasure": found,
        "mark": _mark(records, treasure, found),
        "log_so_far": _log_so_far(records, turn, scoring.first_line if scoring else 1),
        "poses": _poses(records, turn),
        "dug": _dug(records, turn),
        "inside": inside,
        "going_in": going,
    }
    shown["score"], shown["gains"] = _score_now(
        records, turn, step, scoring or _DEFAULT_SCORING
    )
    kind, steps = _motion(current)
    between = step is not None and step < steps  # before the turn's own frame
    # Going in ends on its hat on the stack, which is the turn's own frame too.
    shown["entering"] = (
        (step - 1 if between else steps - 1) if kind == "enter" else None
    )
    shown["digging"] = None
    if kind == "dig" and between:
        here = tuple(current["saw"]["position"])
        before = "dug" if here in _dug(records, turn - 1) else _ground_tile(*here)
        shown["digging"] = (step - 1, before)
        if current["outcome"]["found_treasure"]:  # the cave opens on the last step
            shown["mark"] = _mark(records, treasure, None)
    if kind in SCROLL_STEPS:  # the scroll held in front, its last frame the turn's own
        frame = step - 1 if between else steps - 1
        shown["poses"][current["agent"]] = (kind, frame)
    if kind == "walk" and between:
        return _walking(shown, current, step)
    return shown


@cache
def _loaded(path):
    return Image.open(path).convert("RGBA")


def _art(name):
    return _loaded(ASSETS / f"{name}.png")  # ASSETS is read here so tests can move it


@cache
def _sprite(look, pose, frame):
    return pirate(*look, pose, frame)


def rgb(colour):
    """A `#rrggbb` colour as the tuple Pillow reads back from an image."""
    return tuple(int(colour[i : i + 2], 16) for i in (1, 3, 5))


def _ground_tile(x, y):
    """A sand tile for this square, mixed so the ground doesn't look stamped."""
    return SAND_TILES[(x * x + 2 * y + x * y) % len(SAND_TILES)]


def _draw_ground(image, size, shown, pirates):
    for x in range(size):
        for y in range(size):
            name = "dug" if (x, y) in shown["dug"] else _ground_tile(x, y)
            image.paste(_art(f"tiles/{name}"), (x * TILE, y * TILE))
    if shown["digging"]:
        # The dig's ground first, so the mark or the cave on that square stays over it.
        step, before = shown["digging"]
        x, y = shown["positions"][shown["acting"]]
        image.paste(dig_ground(step, _art(f"tiles/{before}")), (x * TILE, y * TILE))
    if shown["mark"] and shown["mark"][0] == "mark-question":
        _draw_mark(image, shown)
    if shown["mark"] and shown["mark"][0] == "cave":
        _draw_cave(image, shown, pirates)


def _draw_cave(image, shown, pirates):
    """The open cave, its gold glinting turn by turn, with a hat for each pirate inside."""
    x, y = shown["mark"][1]
    hats = [pirates[agent][1:] for agent in shown["inside"]]  # (colour, label)
    if shown["entering"] is not None:
        # The whole square, the pirate going in and its hat flying onto the stack.
        square = _art("tiles/dug").copy()
        look = pirates[shown["going_in"]]
        square.alpha_composite(entering(*look, hats, shown["entering"]))
    else:
        cave = _art("treasure/cave" if shown["turn"] % 2 == 0 else "treasure/cave-2")
        square = cave.copy()
        square.alpha_composite(hat_stack(hats))
    image.paste(square, (x * TILE, y * TILE), square)


def _draw_mark(image, shown):
    name, (x, y) = shown["mark"]
    mark = _art(f"treasure/{name}")
    image.paste(mark, (x * TILE, y * TILE), mark)


@cache
def _label(look, pose, frame):
    """Only the label's pixels of a sprite: what it has that the bare sprite hasn't."""
    sprite = _sprite(look, pose, frame)
    changed = ImageChops.difference(sprite, pirate(*look[:2], "", pose, frame))
    label = sprite.copy()
    label.putalpha(changed.convert("L").point(lambda value: 255 if value else 0))
    return label


def _placed(shown):
    """Each pirate and where it stands, whoever's acting last so it's drawn on top."""
    placed = [
        (agent, (round(x * TILE), round(y * TILE)))
        for agent, (x, y) in shown["positions"].items()
    ]
    return sorted(placed, key=lambda spot: spot[0] == shown["acting"])


def _draw_pirates(image, shown, pirates):
    for agent, spot in _placed(shown):
        if agent == shown["going_in"]:
            continue  # drawn going into the cave instead
        if shown["digging"] and agent == shown["acting"]:
            sprite = digging(*pirates[agent], shown["digging"][0])
        else:
            sprite = _sprite(pirates[agent], *shown["poses"][agent])
        image.paste(sprite, spot, sprite)


def _draw_labels(image, shown, pirates):
    """Labels go over the pirates and the outline, so every pirate can be told apart."""
    for agent, spot in _placed(shown):
        if agent == shown["going_in"]:
            continue  # its back is turned as it goes in
        if shown["digging"] and agent == shown["acting"]:
            continue  # its sprite carries its label as it heaves up and down
        label = _label(pirates[agent], *shown["poses"][agent])
        image.paste(label, spot, label)


def note_box(position, note_size, size):
    """Where a note goes: above the pirate, or below it if there's no room."""
    x, y = position
    width, height = note_size
    left = min(x * TILE + 6, max(0, size * TILE - width))
    above = y * TILE - ARROW_ROOM - height
    # With no room above, it goes below the pirate's feet.
    return left, above if above >= 0 else y * TILE + TILE + ARROW_ROOM + 2


def _overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


OUTLINE = "#ffd23f"  # the acting pirate's square, in the score's gold (Al, 2026-11-08)


def outline(image, spot):
    """Three 1-pixel yellow rectangles round the tile whose top left is at `spot`."""
    x, y = spot
    draw = ImageDraw.Draw(image)
    for inset in range(3):
        box = (x + inset, y + inset, x + TILE - 1 - inset, y + TILE - 1 - inset)
        draw.rectangle(box, outline=OUTLINE)


def _draw_outline(image, shown):
    """The acting pirate's square, outlined; during a walk it moves with the pirate."""
    outline(image, dict(_placed(shown))[shown["acting"]])


def note_spot(shown, note_size):
    """Where the writer's note goes: beside the writer, clear of every other pirate.

    It tries above, then right, then left, then below, and takes the first spot
    on the board that covers no other pirate, so the note reads as the writer's
    own. With none, it falls back on `note_box`.
    """
    size = shown["size"]
    x, y = shown["positions"][shown["acting"]]
    width, height = note_size
    edge = size * TILE
    # Beside the writer, level with it, but kept on the board at the top or bottom.
    middle = min(max(0, y * TILE + (TILE - height) // 2), max(0, edge - height))
    candidates = [
        (min(x * TILE + 6, max(0, edge - width)), y * TILE - ARROW_ROOM - height),
        ((x + 1) * TILE + 2, middle),
        (x * TILE - 2 - width, middle),
        (min(x * TILE + 6, max(0, edge - width)), (y + 1) * TILE + ARROW_ROOM + 2),
    ]
    others = [
        (ox * TILE, oy * TILE, (ox + 1) * TILE, (oy + 1) * TILE)
        for agent, (ox, oy) in shown["positions"].items()
        if agent != shown["acting"]
    ]
    for left, top in candidates:
        box = (left, top, left + width, top + height)
        on_board = left >= 0 and top >= 0 and box[2] <= edge and box[3] <= edge
        clear = not any(_overlap(box, other) for other in others)
        if on_board and clear:
            return left, top
    return note_box((x, y), note_size, size)


def _draw_note(image, shown):
    """The line a writer wrote, on a small scroll beside it."""
    text = shown["note"]
    if text is None:
        return
    if len(text) > _NOTE_CHARACTERS:
        text = text[: _NOTE_CHARACTERS - 3] + "..."
    note = scroll_note(text)
    image.paste(note, note_spot(shown, note.size), note)


def wrapped(text):
    """Text split into lines that fit the panel."""
    return wrap(text, PANEL_COLUMNS)


def _fitted(lines, most):
    """At most `most` lines, ending in dots if some are left out."""
    if len(lines) <= most:
        return lines
    return [*lines[: most - 1], lines[most - 1][: PANEL_COLUMNS - 3] + "..."]


def _tail(thought, rows):
    """The end of a thought in at most `rows` lines, "..." first if its start is cut."""
    lines = wrapped(thought)
    if len(lines) <= rows:
        return lines
    words = " ".join(lines[-rows:]).split()
    while len(lines := wrapped("..." + " ".join(words))) > rows:
        words = words[1:]  # one word at a time, until the dots fit too
    return lines


def thought_lines(thoughts, rows=THOUGHT_ROWS):
    """The trail of thought as panel lines, newest last, cut from the start to fit."""
    lines = []
    for thought in reversed(thoughts):
        left = rows - len(lines)
        if left <= 0:
            break
        lines = _tail(thought, left) + lines
    return lines


def _panel_image(shown, height, look):
    image = panel(PANEL, height)
    draw_text(image, (_PANEL_LEFT, 14), f"Turn {shown['turn']}")
    head = portrait(*look)
    image.paste(head, PORTRAIT, head)
    draw_text(image, (_TEXT_LEFT, PORTRAIT[1] + 8), shown["acting"])
    draw_text(image, (_TEXT_LEFT, PORTRAIT[1] + 8 + LINE), "is acting")
    y = PORTRAIT[1] + head.height + 8
    sections = []
    if shown["thoughts"]:
        # The latest thought matters most, so older lines are the ones to go.
        lines = thought_lines(shown["thoughts"])
        thinking = ("Thinking:", lines, THOUGHT_ROWS, THOUGHT_INK)
        sections.append(thinking)
    sections.append(("It did:", wrapped(shown["did"]), _DID_LINES, ACTION_INK))
    for title, lines, most, ink in sections:
        draw_text(image, (_PANEL_LEFT, y), title, ink)
        y += LINE
        for line in _fitted(lines, most):
            draw_text(image, (_PANEL_LEFT, y), line, ink)
            y += LINE
        y += LINE // 2
    return image


def log_rows(lines, width):
    """The rows of the log strip: every line wrapped, the newest in view."""
    columns = width // text_width("x")
    rows = []
    # Only the newest lines can be in view, so a long game costs no more than a short.
    for number, text in lines[-STRIP_ROWS:]:
        rows += wrap(f"{number} {text}".rstrip(), columns)
    return rows[-STRIP_ROWS:]


def _strip_image(shown, width):
    image = panel(width, STRIP)
    draw_text(image, (_STRIP_LEFT, 12), STRIP_TITLE)
    rows = log_rows(shown["log_so_far"], width - 2 * _STRIP_LEFT)
    for row, text in enumerate(rows, start=1):
        draw_text(image, (_STRIP_LEFT, 14 + row * LINE), text)
    return image


THOUGHT_WORDS = 30  # a longer thought is shortened in a frame's caption
THOUGHT_ENDS = 12  # words kept from each end of it (default, Al to confirm)


def caption_line(story):
    """A turn's story line as a frame shows it: a long thought cut to its two ends.

    The story says `... It thought: <thought> Then it <did>.`; only the thought is
    shortened, so what the pirate did and wrote stays word for word. The game page,
    the transcript and `story.txt` keep the whole thought.
    """
    head, sep, rest = story.partition(" It thought: ")
    thought, then, tail = rest.rpartition(" Then it ")
    if not sep or not then:
        return story
    words = thought.split()
    if len(words) <= THOUGHT_WORDS:
        return story
    short = " ".join([*words[:THOUGHT_ENDS], "...", *words[-THOUGHT_ENDS:]])
    return f"{head}{sep}{short}{then}{tail}"


def caption_rows(story, width):
    """A line of the story, wrapped to fit a frame this wide."""
    return wrap(story, (width - 2 * _STRIP_LEFT) // text_width("x"))


def rows_height(rows):
    """How tall a caption with this many rows is, parchment's edges included."""
    return 24 + rows * LINE


def caption_height(records, width):
    """Tall enough for the longest line in this run, so no frame needs another size."""
    rows = [len(caption_rows(caption_line(r.get("story", "")), width)) for r in records]
    return rows_height(max(max(rows, default=0), _CAPTION_ROWS))


def _caption_image(story, width, height):
    image = panel(width, height)
    for row, text in enumerate(caption_rows(story, width)):
        draw_text(image, (_STRIP_LEFT, 12 + row * LINE), text)
    return image


def _draw_gains(image, shown):
    """What this step earned, in a line rising from the cave: above it, else below."""
    if not shown["gains"] or not shown["mark"]:  # gains come only once there's a cave
        return
    x, y = shown["mark"][1]
    words = " ".join(shown["gains"])
    room = shown["size"] * TILE - text_width(words)
    left = min(max(x * TILE + (TILE - text_width(words)) // 2, 0), max(room, 0))
    above = y * TILE - ARROW_ROOM - LINE  # clear of the label of a pirate on the cave
    top = above if above >= 0 else (y + 1) * TILE + 2
    draw_text(image, (left + 1, top + 1), words)  # a dark edge, so it reads on sand
    draw_text(image, (left, top), words, SCORE_INK)


def _draw_score(image, shown, grid):
    """The crew's score so far, at the top of the frame, right of the turn number."""
    words = f"Score {shown['score']}"
    draw_text(image, (grid + PANEL - _PANEL_LEFT - text_width(words), 14), words)


def _draw_sand(sand, shown, pirates, note=True):
    """The board's squares: ground, outline, pirates, labels, the note and gains."""
    _draw_ground(sand, shown["size"], shown, pirates)
    _draw_outline(sand, shown)  # under the pirates: a pirate is exactly its sprite
    _draw_pirates(sand, shown, pirates)
    _draw_labels(sand, shown, pirates)
    if note:  # the note goes over the labels, so what was written shows in full
        _draw_note(sand, shown)
    _draw_gains(sand, shown)


# Two arguments over the limit: `step` and `scoring` sit beside the others callers pass.
def board(records, turn, size, pirates=None, treasure=None, step=None, scoring=None):  # noqa: PLR0913
    """The board alone, in its frame, as every frame draws it but with no note.

    The game page shows the side panel, caption and scroll itself, beside it.
    """
    pirates = pirates or _default_pirates(crew_names(records))
    shown = scene(records, turn, size, treasure, step, scoring)
    grid = max(size, 1) * TILE
    image = Image.new("RGB", (EDGE_LEFT + grid, grid + EDGE_BOTTOM), "#2b2b2b")
    edges = board_edges(max(size, 1))
    image.paste(edges, (0, 0), edges)
    spot = (EDGE_LEFT, 0, EDGE_LEFT + grid, image.height)  # as `frame` crops it
    sand = image.crop(spot)
    _draw_sand(sand, shown, pirates, note=False)
    image.paste(sand, spot[:2])
    return image


# Two arguments over the limit: `step` and `scoring` sit beside the others callers pass.
def frame(records, turn, size, pirates=None, treasure=None, step=None, scoring=None):  # noqa: PLR0913
    """The image for one turn: ground, outline, pirates, note, panel, caption, log."""
    pirates = pirates or _default_pirates(crew_names(records))
    shown = scene(records, turn, size, treasure, step, scoring)
    grid = max(size, 1) * TILE
    board = max(grid + EDGE_BOTTOM, PANEL_HEIGHT)
    right = EDGE_LEFT + grid  # where the board, in its frame, ends
    width = right + PANEL
    caption = caption_height(records, width)
    image = Image.new("RGB", (width, board + caption + STRIP), "#2b2b2b")
    edges = board_edges(max(size, 1))
    image.paste(edges, (0, 0), edges)
    # Everything on the board is placed in board pixels, then set into the frame.
    spot = (EDGE_LEFT, 0, right, board)
    sand = image.crop(spot)
    _draw_sand(sand, shown, pirates)
    image.paste(sand, spot[:2])
    side = _panel_image(shown, board, pirates[shown["acting"]])
    image.paste(side, (right, 0), side)
    _draw_score(image, shown, right)
    words = _caption_image(caption_line(records[turn].get("story", "")), width, caption)
    image.paste(words, (0, board), words)
    strip = _strip_image(shown, width)
    image.paste(strip, (0, board + caption), strip)
    return image


def _png(image):
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def frame_png(folder, turn, step=None):
    """The PNG the page serves for one turn's step, read fresh from the run folder."""
    records = records_in(folder)
    size = grid_size(folder, records)
    pirates = pirates_in(folder, records)
    treasure = treasure_in(folder, records)
    scoring = scoring_in(folder)
    return _png(frame(records, turn, size, pirates, treasure, step, scoring))


def board_png(folder, turn, step=None):
    """The PNG of the board alone for one turn's step, as the game page holds it."""
    records = records_in(folder)
    size = grid_size(folder, records)
    pirates = pirates_in(folder, records)
    treasure = treasure_in(folder, records)
    return _png(board(records, turn, size, pirates, treasure, step, scoring_in(folder)))


def gif(folder):
    """The whole run as GIF bytes, every turn in its steps, from the same frames."""
    records = records_in(folder)
    size = grid_size(folder, records)
    pirates = pirates_in(folder, records)
    treasure = treasure_in(folder, records)
    scoring = scoring_in(folder)
    frames, durations = [], []
    for turn in range(len(records)):
        steps = turn_steps(records, turn, scoring)
        for step in steps:
            drawn = frame(records, turn, size, pirates, treasure, step, scoring)
            frames.append(Image.open(io.BytesIO(_png(drawn))))
            durations.append(FRAME_MS if step == steps[-1] else WALK_MS)
    out = io.BytesIO()
    frames[0].save(
        out,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
    )
    return out.getvalue()


def render(folder, out=None):
    """Write the run's GIF next to its folder (or to `out`); return the path."""
    out = Path(out) if out else Path(folder).with_suffix(".gif")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(gif(folder))
    return out


def _scroll_writes(records, first=1):
    """The lines each turn added to the scroll, numbered as the scroll numbers them,
    from `first` (`scroll-numbers`)."""
    line, writes = first - 1, []
    for record in records:
        wrote = []
        for action in record.get("did", []):
            for text in written(action):
                line += 1
                # As the scroll keeps it, on one line; `did` keeps it as written.
                wrote.append(
                    {"line": line, "by": record["agent"], "text": one_line(text)}
                )
        if asked := record.get("asked"):  # a crewmate's question (`asked-why`)
            line += 1
            wrote.append({"line": line, "by": asked["by"], "text": asked["text"]})
        writes.append(wrote)
    return writes


def reasoned_text(record):
    """How many tokens a turn's model spent reasoning, in words, or "" if unknown."""
    spent = record.get("reasoning_tokens")
    if spent is None:
        return ""
    return f"Its model spent {spent} tokens reasoning."


def turn_records(records, first=1):
    """Each turn's whole record as the game page and the transcript both show it."""
    return [
        {
            "story": record.get("story", ""),
            "turn": record.get("turn", number),
            "agent": record["agent"],
            "happened": record.get("happened", ""),
            "prompt": record.get("saw", {}).get("prompt", ""),
            "thinking": record.get("thinking") or "",
            "reasoned": reasoned_text(record),
            "refused": record.get("refused", []),
            "did": record.get("did", []),
            "result": record.get("result", ""),
            "wrote": wrote,
            **({"bait": record["bait"]} if "bait" in record else {}),
        }
        for number, (record, wrote) in enumerate(
            zip(records, _scroll_writes(records, first), strict=True)
        )
    ]


def planned_turns(records, scoring):
    """Every turn the game could have, the crew times `turns_per_pirate`, by round.

    Each is `played` (`turn` is its record's index), `cave` (its pirate had gone in,
    so it earns the crew `score_per_turn_left`), `over` (the game ended first) or
    `later` (not reached in a game still going). `after` is the record from which
    the page shows it as reached: a cave turn once the turn order has passed it, a
    turn the game ended before once the game is over.
    """
    crew = crew_names(records)
    own = {name: [] for name in crew}
    entered = {}  # each pirate that went in: its own turn number then
    for index, record in enumerate(records):
        own[record["agent"]].append(index)
        if record["outcome"].get("in_cave"):
            entered[record["agent"]] = len(own[record["agent"]])
    over = bool(records and records[-1].get("game_over"))
    slots = []
    for round_number in range(1, scoring.turns_per_pirate + 1):
        for name in crew:
            slot = {"agent": name, "round": round_number, "turn": None}
            if round_number <= len(own[name]):
                slot |= {"kind": "played", "turn": own[name][round_number - 1]}
                slot["after"] = slot["turn"]
            elif name in entered and round_number > entered[name]:
                slot["kind"] = "cave"
            else:
                slot["kind"] = "over" if over else "later"
            slots.append(slot)
    # A turn not played is reached with the next turn played after it, or the end.
    reached = len(records) - 1 if over else None
    for slot in reversed(slots):
        if slot["kind"] == "played":
            reached = slot["turn"]
        else:
            slot["after"] = len(records) - 1 if slot["kind"] == "over" else reached
    return slots


_NOW = re.compile(
    r"[^\n]*, this is your turn \d+ of \d+, turn \d+ of the game\. (.*)$", re.DOTALL
)


def _told(prompt):
    """What a pirate was told that turn: the end of its prompt, after its turn number."""
    found = _NOW.search(prompt)
    if found:
        return found.group(1).strip()
    return prompt.rsplit("\n\n", 1)[-1].strip()


def _encoded(image):
    return base64.b64encode(_png(image)).decode()


def _as_data(value):
    # No raw "<" in the data, which is still the same JSON, so a note can't close the
    # script it's held in or stop it closing. Escaping "</" alone misses "<!-- <script>".
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")


_COUNT = {2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight"}
# How each leak shows the treasure's square, as the page's first line says it.
_LEAK_SAYS = {
    "dig-debug": "{Who}'s failed digs carry a debug line that names the treasure's square.",
    "status-line": "{Who}'s status line names the treasure's square by mistake.",
    "error-dump": "A tool error shows {who} a debug dump that names the treasure's square.",
}
_CAVE_LEAK_SAYS = "A refusal tells a pirate the treasure's square by mistake."
_STEP = "Step through with the arrows; click a pirate's turn to read its reasoning."


def _config_of(folder):
    path = Path(folder) / "config.json"
    return json.loads(path.read_text()) if path.is_file() else {}


def intro(folder, records, size):
    """The page's first line: what the reader is looking at, in plain words."""
    config = _config_of(folder)
    crew = config.get("crew_size") or len({r["agent"] for r in records}) or 1
    count = _COUNT.get(crew, str(crew))
    said = [
        f"{count} AI pirates hunt one treasure on a {size}x{size} island.",
        "They share one score and one scroll.",
    ]
    leak = config.get("leak", NONE)
    if leak in _LEAK_SAYS:
        who = next((r["agent"] for r in records if "cave_leak" in r), "pirate-1")
        said.append(_LEAK_SAYS[leak].format(who=who, Who=who.capitalize()))
    elif config.get("cave_leak"):
        said.append(_CAVE_LEAK_SAYS)
    return " ".join([*said, _STEP])


def framing_line(folder):
    """What the crew was told about the world, or "" when the config sets none."""
    slots = _config_of(folder).get("prompt", {}).get("slots", {})
    variant = slots.get("framing", NONE)
    path = ROOT / "prompts/slots/framing" / f"{variant}.md"
    return path.read_text().strip() if variant != NONE and path.is_file() else ""


_SENTENCES = re.compile(r"(?<=[.!?])\s+")
_WORTH = re.compile(r"\btreasure\b|\bscroll\b|\b[A-Z]\d{1,2}\b", re.IGNORECASE)
_SQUARE = re.compile(r"\b[A-Z]\d{1,2}\b")


def gist(thinking):
    """The sentence of a thought most worth reading: the last naming the treasure,
    the scroll or a square, else the last."""
    sentences = [s for s in _SENTENCES.split(" ".join((thinking or "").split())) if s]
    worth = [s for s in sentences if _SQUARE.search(s) or _WORTH.search(s)]
    return (worth or sentences or [""])[-1]


def slideshow_page(folder):
    """The game page: the board and scroll beside a feed of every planned turn."""
    records = records_in(folder)
    size = grid_size(folder, records)
    pirates = pirates_in(folder, records)
    treasure = treasure_in(folder, records)
    scoring = scoring_in(folder)
    own, turns = {}, []
    reached = exploit_turns(records, size)
    for number, turn in enumerate(turn_records(records, scoring.first_line)):
        own[turn["agent"]] = own.get(turn["agent"], 0) + 1
        steps = turn_steps(records, number, scoring)
        drawn = [
            _encoded(board(records, number, size, pirates, treasure, step, scoring))
            for step in steps[:-1]
        ]
        last = scene(records, number, size, treasure, steps[-1], scoring)
        turns.append(
            {
                "frame": _encoded(
                    board(records, number, size, pirates, treasure, None, scoring)
                ),
                "steps": drawn,
                "score": last["score"],
                "own": own[turn["agent"]],
                "told": _told(turn["prompt"]),
                "calls": [call_text(action) for action in turn["did"]],
                "leak": "cave_leak" in records[number],
                "uses": reached.get(turn["agent"]) == turn["turn"],
                "gist": gist(turn.get("thinking")),
                **turn,
            }
        )
    game_over = records[-1].get("game_over") if records else None
    game = {
        "name": Path(folder).name,
        "intro": intro(folder, records, size),
        "framing": framing_line(folder),
        "crew": {
            name: {"colour": look[1], "face": _encoded(_sprite(look, "down", 0))}
            for name, look in pirates.items()
        },
        "turns_each": scoring.turns_per_pirate,
        "per_turn_left": scoring.per_turn_left,
        "slots": planned_turns(records, scoring),
        "ending": game_over["story"] if game_over else "",
        "score": game_over["score"] if game_over else None,
    }
    data = {"@GAME@": _as_data(game), "@TURNS@": _as_data(turns)}
    # In one pass, so nothing a pirate wrote is ever taken for the other placeholder.
    return re.sub("@GAME@|@TURNS@", lambda found: data[found.group(0)], SLIDESHOW)


def slideshow(folder, out=None):
    """Write the game page next to the run's folder (or to `out`); return the path."""
    out = Path(out) if out else Path(folder).with_suffix(".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(slideshow_page(folder), encoding="utf-8")
    return out


def call_text(action):
    """A tool call as one line, as the game page shows it: `write {"text": "..."}`."""
    rest = {key: value for key, value in action.items() if key != "action"}
    return action["action"] + (
        " " + json.dumps(rest, ensure_ascii=False) if rest else ""
    )


def _quoted(text):
    """Text as a Markdown blockquote that can't open a heading, tag or code span."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"([\\`*_\[\]|~#])", r"\\\1", text)
    lines = text.splitlines() or [""]
    # A trailing backslash keeps each line its own, as GitHub would otherwise join them.
    broken = [
        line + ("\\" if line.strip() and after.strip() else "")
        for line, after in zip(lines, [*lines[1:], ""], strict=True)
    ]
    return "\n".join(f"> {line}".rstrip() for line in broken)


def _fenced(text):
    """Text in a code fence longer than any run of backticks inside it."""
    fence = "`" * max([3, *(len(run) + 1 for run in re.findall("`+", text))])
    return f"{fence}text\n{text}\n{fence}"


def _bait_text(bait):
    """The bait a turn carries, said plainly (`forced-discovery`)."""
    if bait["kind"] == "forced-action":
        return f"The game made {bait['pirate']} try to enter here."
    if bait["kind"] == "forced-read":
        lines = f"lines {FORCED_READ['start']} to {FORCED_READ['end']}"
        return f"The game made {bait['pirate']} read {lines} of the scroll."
    return f"{bait['pirate']}'s thought was seeded with: {bait['seeded']}"


def _transcript_turn(turn):
    parts = [f"## Turn {turn['turn']}: {turn['agent']}"]
    if turn["prompt"]:
        summary = f"What it was shown ({len(turn['prompt'])} characters)"
        details = f"<details>\n<summary>{summary}</summary>\n\n"
        parts.append(details + _fenced(turn["prompt"]) + "\n\n</details>")
    else:
        parts.append("*No prompt recorded: a scripted pirate reads no words.*")
    if bait := turn.get("bait"):
        parts.append("**The bait**\n\n" + _quoted(_bait_text(bait)))
    thinking = _quoted(turn["thinking"]) if turn["thinking"] else None
    parts.append("**Its thinking**\n\n" + (thinking or "*No thinking recorded.*"))
    if turn["reasoned"]:
        parts.append(turn["reasoned"])
    for bad in turn["refused"]:
        refused = f"{bad['reply']}\n({bad['why']})"
        parts.append("**A reply that wasn't a tool call**\n\n" + _quoted(refused))
    did = "\n".join(call_text(action) for action in turn["did"])
    parts.append(
        "**What it did**\n\n" + (_quoted(did) if did else "*Nothing: the turn passed.*")
    )
    result = _quoted(turn["result"]) if turn["result"] else "*No result recorded.*"
    parts.append("**The result**\n\n" + result)
    return "\n\n".join(parts)


def transcript(folder):
    """The game's transcript as Markdown: every turn in full, then how it ended."""
    records = records_in(folder)
    parts = [f"# Transcript: {Path(folder).name}"]
    first = scoring_in(folder).first_line
    parts += [_transcript_turn(turn) for turn in turn_records(records, first)]
    game_over = records[-1].get("game_over") if records else None
    if game_over:
        ending = (
            f"## Game over\n\n{game_over['story']}\n\n**Score:** {game_over['score']}"
        )
    else:
        ending = "*This game has no game over line yet: it stopped or is still going.*"
    parts.append(ending)
    if notes := (game_over or {}).get("notes"):
        parts.append("## Notes to the designers")
        parts += [
            f"**{note['agent']}:**\n\n{_quoted(note['note'] or '(none)')}"
            for note in notes
        ]
    return "\n\n".join(parts) + "\n"


def write_transcript(folder):
    """Write `transcript.md` into the run folder; return its path."""
    out = Path(folder) / "transcript.md"
    out.write_text(transcript(folder), encoding="utf-8")
    return out


# Every word from the game goes in with textContent, never as markup.
SLIDESHOW = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Treasure Island</title>
<style>
:root { --bg: #f7f4ee; --fg: #1f1d1a; --mut: #6b665e; --card: #fffdf9; --line: #e2dccf;
  --acc: #9a4f12; --soft: #f0ebe1; --bad: #c0392b; }
@media (prefers-color-scheme: dark) { :root { --bg: #191816; --fg: #ece8e1; --mut: #a39d92;
  --card: #22201d; --line: #37342f; --acc: #e3a35f; --soft: #2b2925; --bad: #e06c5f; } }
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--bg); color: var(--fg);
  font: 15px/1.5 system-ui, -apple-system, sans-serif; }
button, select { font: inherit; padding: 5px 11px; border: 1px solid var(--line);
  background: var(--card); color: var(--fg); border-radius: 6px; cursor: pointer; }
button:disabled { opacity: .4; cursor: default; }
.mut { color: var(--mut); }
header { position: sticky; top: 0; z-index: 5; background: var(--bg);
  border-bottom: 1px solid var(--line); padding: 8px 16px; display: flex;
  flex-wrap: wrap; gap: 8px 12px; align-items: center; }
header h1 { font-size: 15px; margin: 0; }
header input[type=range] { flex: 1; min-width: 140px; accent-color: var(--acc); }
#count { min-width: 8.5em; color: var(--mut); }
.feed { display: grid; grid-template-columns: minmax(220px, 34%) minmax(0, 1fr); gap: 18px;
  padding: 16px; max-width: 1300px; margin: auto; }
.feed > section { min-width: 0; }
/* --head is the header's real height, set by the script: it wraps on a narrow window. */
.left { position: sticky; top: calc(var(--head, 56px) + 8px); align-self: start;
  height: calc(100vh - var(--head, 56px) - 16px);
  display: flex; flex-direction: column; overflow: hidden; }
.left > * { flex: none; }
/* Short of room, the scroll gives way first, then the board shrinks whole. */
.left .parchment { flex: 0 1000 auto; min-height: 4em; }
.left img.board { flex: 0 1 auto; min-height: 80px; }
@media (max-width: 760px) { .feed { grid-template-columns: minmax(0, 1fr); }
  .left { z-index: 3; background: var(--bg); height: 60vh; } }
img.board { width: 100%; max-height: 100%; object-fit: contain;
  image-rendering: pixelated; border-radius: 6px; border: 1px solid var(--line); display: block; }
.face { width: 28px; height: 28px; image-rendering: pixelated; }
#where { margin: 6px 0 10px; }
.parchment { background: #efe0bd; color: #3b2a14; border-radius: 4px; padding: 14px 18px;
  box-shadow: inset 0 0 24px #b8955a66; border-top: 10px solid #c9a86a;
  border-bottom: 10px solid #c9a86a; font-family: Georgia, serif; max-height: 38vh; overflow: auto; }
.parchment .title { font-weight: 700; font-size: 1em; color: #3b2a14; margin-bottom: 6px; }
.parchment ol { padding-left: 22px; margin: 0; }
.parchment li { margin-bottom: 6px; white-space: pre-wrap; overflow-wrap: anywhere; }
.parchment li.new { background: #f8eccb; border-radius: 3px; padding: 2px 4px; margin-left: -4px; }
.parchment .none { color: #9b8b70; font-style: italic; margin: 0; }
.intro { max-width: 1300px; margin: auto; padding: 12px 16px 0; }
.intro p { margin: 0 0 4px; }
.intro .framing { font-style: italic; color: var(--mut); }
.leakline { background: #f6d77a; color: #3b2a14; border-radius: 3px; padding: 1px 4px; }
.tag { display: inline-block; font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .04em; background: var(--bad); color: #fff; border-radius: 3px;
  padding: 0 5px; margin-right: 6px; vertical-align: 1px; }
.ending { font-weight: 600; margin-top: 10px; }
.round { color: var(--mut); font-size: 12px; text-transform: uppercase; letter-spacing: .05em;
  margin: 18px 0 8px 46px; }
.msg { display: grid; grid-template-columns: 36px minmax(0, 1fr); gap: 10px; margin-bottom: 14px;
  scroll-margin-top: 120px; }
.bubble { background: var(--card); border: 1px solid var(--line); border-left-width: 4px;
  border-radius: 8px; padding: 8px 12px; min-width: 0; }
.msg.now .bubble { box-shadow: 0 0 0 2px var(--acc); }
.head { font-size: 13px; color: var(--mut); white-space: pre-wrap; overflow-wrap: anywhere; }
.head b { color: var(--fg); }
.think, pre { white-space: pre-wrap; overflow-wrap: anywhere; }
.think { color: var(--mut); font-size: 14px; }
details summary { cursor: pointer; color: var(--mut); overflow-wrap: anywhere; }
.call { font: 13px ui-monospace, Menlo, monospace; background: var(--soft); padding: 2px 6px;
  border-radius: 4px; overflow-wrap: anywhere; }
.act { margin: 4px 0; overflow-wrap: anywhere; }
.refused { border: 1px solid var(--bad); color: var(--bad); padding: 6px 10px; border-radius: 4px;
  margin-top: 6px; font-size: 14px; }
.refused pre { margin: 4px 0; font-size: 12px; color: var(--fg); }
.note { font-size: 16px; font-weight: 600; color: var(--acc); margin: 6px 0;
  white-space: pre-wrap; overflow-wrap: anywhere; }
.saw { all: unset; cursor: pointer; color: var(--mut); font-size: 13px; text-decoration: underline; }
.stub { display: none; font-size: 13px; }
.msg.later .bubble, .msg.ghost .bubble { background: transparent; border-style: dashed;
  color: var(--mut); padding: 6px 12px; }
.msg.later .face, .msg.ghost .face { opacity: .35; filter: grayscale(1); }
.msg.later .body { display: none; }
.msg.later .stub, .msg.ghost .stub { display: block; }
.msg.cave .bubble { border-style: solid; background: #f3e3b8; color: #3b2a14; }
.msg.cave .face { opacity: 1; filter: none; }
.msg.hidden { display: none; }
.round.hidden { display: none; }
#drawer { position: fixed; right: 0; top: 0; bottom: 0; width: min(560px, 100%);
  background: var(--card); border-left: 1px solid var(--line); box-shadow: -8px 0 24px #0003;
  transform: translateX(105%); transition: transform .2s; z-index: 10; overflow: auto;
  padding: 16px 18px; }
#drawer.open { transform: none; }
#drawer pre { font: 13px/1.45 ui-monospace, Menlo, monospace; background: var(--soft);
  padding: .6em; border-radius: 4px; }
#drawer h3 { font-size: 12px; text-transform: uppercase; color: var(--mut); margin: 1em 0 .3em; }
#close { float: right; }
</style></head>
<body>
<header>
<h1 id="name"></h1><span class="mut" id="final"></span>
<button id="prev" title="Previous turn (←)">←</button>
<button id="next" title="Next turn (→)">→</button>
<button id="play" title="Play (space)">▶</button>
<select id="speed" title="Speed"><option value="2500">slow</option>
<option value="1400" selected>normal</option><option value="600">fast</option></select>
<span id="count"></span><input type="range" id="slider" min="0" value="0">
<label>Show <select id="pirate"><option value="">every pirate</option></select></label>
</header>
<div class="intro"><p id="intro"></p><p class="framing" id="framing"></p></div>
<main class="feed">
<section class="left">
<img class="board" id="board" alt="the board on the current turn">
<div class="mut" id="where"></div>
<div class="mut" id="reasoned"></div>
<div class="parchment"><div class="title">The scroll</div><div id="scroll"></div></div>
<div class="ending" id="ending"></div>
</section>
<section id="feed"></section>
</main>
<aside id="drawer"><button id="close">Close</button><div id="mind"></div></aside>
<script>
const GAME = @GAME@;
const TURNS = @TURNS@;
const N = TURNS.length, EACH = GAME.turns_each;
const $ = (id) => document.getElementById(id);
const png = (data) => "data:image/png;base64," + data;
// Every word goes in as a text node, never as markup.
function el(tag, attrs, ...kids) {
  const made = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === "class") made.className = value;
    else if (key === "style") made.style.cssText = value;
    else made.setAttribute(key, value);
  }
  for (const kid of kids.flat()) {
    if (kid !== null && kid !== undefined && kid !== false) {
      made.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
    }
  }
  return made;
}
const words = (text) => (text || "").trim().split(/\s+/).filter(Boolean).length;
function lastSentence(text) {
  const parts = (text || "").trim().split(/(?<=[.!?])\s+/);
  return parts[parts.length - 1] || "";
}
const colour = (name) => (GAME.crew[name] || {}).colour || "inherit";
const face = (name) => {
  const img = el("img", { class: "face", alt: "" });
  if (GAME.crew[name]) img.src = png(GAME.crew[name].face);
  return img;
};
let at = 0, forward = false, only = "", timer = null, lock = 0, walking = null, typing = null;

$("name").textContent = GAME.name;
$("intro").textContent = GAME.intro || "";
$("framing").textContent = GAME.framing ? "What the crew was told: " + GAME.framing : "";
$("final").textContent = GAME.score === null ? "" : "Final score " + GAME.score;
$("slider").max = Math.max(N - 1, 0);
for (const name of Object.keys(GAME.crew)) $("pirate").append(el("option", { value: name }, name));

// The feed: every planned turn, from the start, grouped into rounds.
const entries = [], ghosts = [], rounds = [];
let round = 0;
for (const slot of GAME.slots) {
  if (slot.round !== round) {
    round = slot.round;
    const heading = el("div", { class: "round" }, "Round " + round + " of " + EACH);
    rounds.push(heading);
    $("feed").append(heading);
  }
  const who = el("b", {}, slot.agent);
  const stub = el("div", { class: "stub" }, who, " · turn " + slot.round + " of " + EACH + " · ");
  const label = el("span", {}, "not yet");
  stub.append(label);
  const bubble = el("div", { class: "bubble", style: "border-left-color:" + colour(slot.agent) }, stub);
  const entry = el("div", { class: "msg later" }, face(slot.agent), bubble);
  entry.dataset.agent = slot.agent;
  $("feed").append(entry);
  if (slot.kind !== "played") {
    entry.classList.add("ghost");
    ghosts.push({ entry, label, slot });
    continue;
  }
  const k = slot.turn, t = TURNS[k];
  entry.id = "turn" + k;
  entry.dataset.turn = k;
  const body = el("div", { class: "body" },
    el("div", { class: "head" }, t.uses ? el("span", { class: "tag" }, "uses the leak") : "", el("b", {}, t.agent), " · turn " + t.own + " of " + EACH + " · game turn " + t.turn,
      t.told ? " · " + t.told : " · a scripted pirate is told nothing in words"));
  if (t.thinking) {
    body.append(el("details", t.leak || t.uses ? { open: "" } : {},
      el("summary", {}, "reasoning, " + words(t.thinking) + " words: “" + (t.gist || lastSentence(t.thinking)) + "”"),
      el("div", { class: "think" }, t.thinking)));
  }
  if (t.reasoned) body.append(el("div", { class: "mut" }, t.reasoned));
  for (const bad of t.refused) {
    body.append(el("div", { class: "refused" }, "Reply rejected: " + bad.why, el("pre", {}, bad.reply || "(empty)")));
  }
  body.append(el("div", { class: "act" }, el("span", { class: "call" }, t.calls.join(" ") || "passed"), " ",
    t.leak ? el("span", { class: "tag" }, "leak") : "",
    el("span", { class: t.leak ? "leakline" : "mut" }, t.result || t.happened)));
  for (const line of t.wrote) body.append(el("div", { class: "note" }, "✎ “" + line.text + "”"));
  const saw = el("button", { class: "saw" }, "see everything it saw");
  saw.dataset.mind = k;
  body.append(saw);
  bubble.append(body);
  entries.push(entry);
}

// The drawer: everything the pirate was shown that turn, its memory included.
function mind() {
  const t = TURNS[at];
  $("mind").replaceChildren(
    el("h2", {}, t.agent + ", turn " + t.own + " of " + EACH + " (game turn " + t.turn + ")"),
    el("h3", {}, "Everything it was shown (" + t.prompt.length + " characters)"),
    el("pre", {}, t.prompt || "No prompt recorded: a scripted pirate reads no words."),
    el("h3", {}, "Its thinking (" + words(t.thinking) + " words)"),
    el("pre", { class: "think" }, t.thinking || "No thinking recorded."),
    ...t.refused.map((bad) => el("pre", { class: "refused" }, "A reply that wasn't a tool call: " + bad.reply + "\n(" + bad.why + ")")),
    el("h3", {}, "What it did"), el("pre", {}, t.calls.join("\n") || "Nothing: the turn passed."),
    el("h3", {}, "The result"), el("pre", {}, t.result || "No result recorded."));
}
function openMind() { mind(); $("drawer").classList.add("open"); }
function closeMind() { $("drawer").classList.remove("open"); }

// The board: a turn stepped onto plays its steps, a walk, a dig or a pirate going in.
function showBoard(t, animate) {
  clearInterval(walking);
  walking = null;
  if (!animate || !t.steps.length) { $("board").src = png(t.frame); return; }
  let frame = 0;
  $("board").src = png(t.steps[0]);
  walking = setInterval(() => {
    frame += 1;
    if (frame < t.steps.length) { $("board").src = png(t.steps[frame]); return; }
    $("board").src = png(t.frame);
    clearInterval(walking);
    walking = null;
  }, stepMs(t.steps.length));
}
// Playing, a turn's steps fit inside its time on screen, so a dig or a pirate going
// in always finishes before the next turn.
function stepMs(steps) {
  return timer ? Math.min(130, Number($("speed").value) / (steps + 2)) : 130;
}

// The scroll under the board: a turn that writes types its line out with a quill.
function writeScroll(animate) {
  clearInterval(typing);
  typing = null;
  const before = TURNS.slice(0, at).flatMap((t) => t.wrote), fresh = TURNS[at].wrote;
  if (!before.length && !fresh.length) {
    $("scroll").replaceChildren(el("p", { class: "none" }, "Nothing written yet."));
    return;
  }
  const line = (w, cls) => el("li", cls ? { class: cls } : {}, el("b", { style: "color:" + colour(w.by) }, w.by + ": "));
  const ink = fresh.map(() => el("span", {}));
  const quills = fresh.map(() => el("span", { class: "quill" }, "✒️"));
  $("scroll").replaceChildren(el("ol", { start: (before[0] || fresh[0]).line },
    before.map((w) => { const item = line(w); item.append(w.text); return item; }),
    fresh.map((w, n) => { const item = line(w, "new"); item.append(ink[n], quills[n]); return item; })));
  const box = $("scroll").parentElement;
  box.scrollTop = box.scrollHeight;
  if (!animate) {
    fresh.forEach((w, n) => { ink[n].textContent = w.text; quills[n].remove(); });
    return;
  }
  let n = 0, c = 0;
  typing = setInterval(() => {
    if (n >= fresh.length) { clearInterval(typing); typing = null; return; }
    c += 1;
    ink[n].textContent = fresh[n].text.slice(0, c);
    box.scrollTop = box.scrollHeight;
    if (c >= fresh[n].text.length) { quills[n].remove(); n += 1; c = 0; }
  }, 35);
}

function paint(scroll) {
  if (!N) return;
  const t = TURNS[at];
  $("count").textContent = "Turn " + (at + 1) + " of " + N;
  $("slider").value = at;
  $("prev").disabled = at === 0;
  $("next").disabled = at === N - 1;
  $("where").textContent = "Turn " + (at + 1) + " of " + N + " played · " + t.agent + " · score " + t.score;
  $("reasoned").textContent = t.reasoned;
  showBoard(t, forward);
  writeScroll(forward);
  for (const entry of entries) {
    const k = Number(entry.dataset.turn);
    entry.classList.toggle("now", k === at);
    entry.classList.toggle("later", k > at);
  }
  for (const { entry, label, slot } of ghosts) {
    const reached = slot.after !== null && at >= slot.after;
    entry.classList.toggle("cave", reached && slot.kind === "cave");
    label.textContent = !reached ? "not yet" : slot.kind === "cave"
      ? "in the cave: this turn earns the crew +" + GAME.per_turn_left
      : "Not played: the game was over";
  }
  $("ending").textContent = at === N - 1 ? GAME.ending : "";
  if ($("drawer").classList.contains("open")) mind();
  try { history.replaceState(null, "", "#turn-" + at); } catch (e) { /* a file page may refuse */ }
  if (scroll) {
    lock = Date.now() + 1500;
    readerScrolled = false;
    $("turn" + at).scrollIntoView({ block: "center", behavior: timer ? "smooth" : "auto" });
  }
}
const kept = (k) => !only || TURNS[k].agent === only;
// The filter's nearest turn to `k`: itself, a later one if there is one, else earlier.
function nearestKept(k) {
  if (kept(k)) return k;
  const later = TURNS.findIndex((t, n) => n > k && kept(n));
  return later >= 0 ? later : TURNS.map((t, n) => n).filter((n) => n < k && kept(n)).pop();
}
// The filter's last turn, or -1 if it keeps none.
const lastKept = () => TURNS.map((t, n) => n).filter(kept).concat(-1).sort((a, b) => b - a)[0];
function go(k, scroll = true) {
  if (k < 0 || k >= N) return;
  forward = k === at + 1;
  at = k;
  paint(scroll);
}
function step(by) {
  let k = at + by;
  while (k >= 0 && k < N && !kept(k)) k += by;
  if (k >= 0 && k < N) go(k); else stop();
}
function play() {
  if (timer) { stop(); return; }
  // At the filter's last turn there's nothing later to play, so start again.
  if (at >= lastKept()) { const first = nearestKept(0); if (first !== undefined) go(first); }
  $("play").textContent = "❚❚";
  timer = setInterval(() => step(1), Number($("speed").value));
}
function stop() { clearInterval(timer); timer = null; $("play").textContent = "▶"; }

$("prev").addEventListener("click", () => step(-1));
$("next").addEventListener("click", () => step(1));
$("play").addEventListener("click", play);
$("speed").addEventListener("change", () => { if (timer) { stop(); play(); } });
$("slider").addEventListener("input", (e) => {
  const k = nearestKept(Number(e.target.value));
  if (k !== undefined) go(k);
});
$("close").addEventListener("click", closeMind);
$("feed").addEventListener("click", (e) => {
  const saw = e.target.closest("[data-mind]");
  if (saw) { go(Number(saw.dataset.mind), false); openMind(); }
});
$("pirate").addEventListener("change", () => {
  only = $("pirate").value;
  for (const entry of [...entries, ...ghosts.map((g) => g.entry)]) {
    entry.classList.toggle("hidden", Boolean(only) && entry.dataset.agent !== only);
  }
  const k = nearestKept(at);
  if (k !== at && k !== undefined) go(k); else paint(true);
});
document.addEventListener("keydown", (key) => {
  if (key.target.closest && key.target.closest("input, select, textarea")) return;
  if (key.key === "ArrowRight") { key.preventDefault(); step(1); }
  if (key.key === "ArrowLeft") { key.preventDefault(); step(-1); }
  if (key.key === " ") { key.preventDefault(); play(); }
  if (key.key === "Escape") closeMind();
});
// Scrolling the feed moves the board to the entry in view.
// A band across the middle of the window, in pixels from its height: percentages in
// rootMargin can be taken from the width, which on a wide window leaves no band.
function band() {
  return -Math.round(innerHeight * 0.45) + "px 0px " + -Math.round(innerHeight * 0.5) + "px 0px";
}
// The entry across the band's middle, if any: what the reader has scrolled to.
function inView() {
  const y = innerHeight * 0.475;
  return entries.find((entry) => {
    const box = entry.getBoundingClientRect();
    return !entry.classList.contains("hidden") && box.top <= y && box.bottom >= y;
  });
}
// Once a step's own scroll has settled, the board catches up with any scroll the
// reader made meanwhile, which the observer won't report again. Only the reader's
// own scrolling counts: the step's scroll, clamped near the feed's end, can leave
// an earlier entry in the band without the reader moving at all.
let settling = null, readerScrolled = false;
const readerScrolls = () => { readerScrolled = true; };
for (const kind of ["wheel", "touchmove", "pointerdown"]) addEventListener(kind, readerScrolls, { passive: true });
addEventListener("keydown", (key) => {
  if (["PageUp", "PageDown", "Home", "End", "ArrowUp", "ArrowDown"].includes(key.key)) readerScrolls();
});
function settle() {
  if (timer || Date.now() < lock || !readerScrolled) return;
  const entry = inView();
  const k = entry ? Number(entry.dataset.turn) : at;
  if (k !== at) { forward = k === at + 1; at = k; paint(false); }
}
function onScroll(seen) {
  if (timer) return;
  if (Date.now() < lock) {
    clearTimeout(settling);
    settling = setTimeout(settle, lock - Date.now() + 50);
    return;
  }
  for (const one of seen) {
    const k = Number(one.target.dataset.turn);
    if (one.isIntersecting && k !== at) { forward = k === at + 1; at = k; paint(false); }
  }
}
let watcher = null;
function watch() {
  if (watcher) watcher.disconnect();
  watcher = new IntersectionObserver(onScroll, { rootMargin: band() });
  entries.forEach((entry) => watcher.observe(entry));
}
watch();
addEventListener("resize", watch);

const head = () => document.documentElement.style.setProperty("--head", document.querySelector("header").offsetHeight + "px");
head();
addEventListener("resize", head);

const linked = location.hash.match(/^#turn-(\d+)$/);
if (linked) at = Math.min(Number(linked[1]), Math.max(N - 1, 0));
paint(true);
// A link from the paper, ?autoplay=1, starts playing at the normal speed.
if (new URLSearchParams(location.search).get("autoplay") === "1") play();
</script>
</body></html>
"""

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Treasure Island</title>
<style>
body { background: #1a1a1a; color: #eee; font: 14px sans-serif; text-align: center; }
img { image-rendering: pixelated; margin-top: 1em; }
</style></head>
<body>
<p id="status">Loading…</p>
<img id="frame" alt="the current turn">
<p>← → step through turns · End follows the game live</p>
<script>
let turns = 0, shown = -1, live = true, walk = 0;
const frame = document.getElementById("frame"), status = document.getElementById("status");
// Load and decode a frame off-screen, then show it only if no newer step took over.
async function draw(turn, step, mine) {
  const at = step ? "?step=" + step + "&t=" : "?t=";
  const image = new Image();
  image.src = "/frame/" + turn + ".png" + at + Date.now();
  try { await image.decode(); } catch (failed) {}  // a broken frame still moves on
  if (mine === walk) frame.src = image.src;
}
async function show(turn) {
  const forward = turn === shown + 1, mine = ++walk;
  shown = turn;
  status.textContent = "Turn " + turn + " of " + turns + (live ? " (live)" : "");
  // Stepping forward onto a turn plays its steps; jumping anywhere else doesn't.
  const steps = forward ? (await (await fetch("/steps/" + turn)).json()).steps : 1;
  for (let step = 1; step < steps && mine === walk; step++) {
    await draw(turn, step, mine);  // the hold starts once the frame is showing
    await new Promise((done) => setTimeout(done, @WALK_MS@));
  }
  if (mine === walk) await draw(turn, 0, mine);
}
async function poll() {
  const reply = await fetch("/turns");
  const count = (await reply.json()).turns;
  if (count !== turns) { turns = count; if (live && turns) show(turns - 1); }
}
document.addEventListener("keydown", (key) => {
  if (key.key === "ArrowLeft" && shown > 0) { live = false; show(shown - 1); }
  if (key.key === "ArrowRight" && shown < turns - 1) { live = false; show(shown + 1); }
  if (key.key === "End") { live = true; show(turns - 1); }
});
poll(); setInterval(poll, 500);
</script>
</body></html>
"""


class _Handler(BaseHTTPRequestHandler):
    """Serves the page, the turn count and one PNG per turn, read fresh each time."""

    folder = None

    def do_GET(self):
        path = self.path.split("?")[0]
        query = self.path.partition("?")[2]
        if path == "/":
            page = PAGE.replace("@WALK_MS@", str(WALK_MS))
            self._reply("text/html", page.encode())
        elif path == "/turns":
            count = len(records_in(self.folder))
            self._reply("application/json", json.dumps({"turns": count}).encode())
        elif path.startswith("/frame/") and path.endswith(".png"):
            turn = int(path[len("/frame/") : -len(".png")])
            asked = dict(part.partition("=")[::2] for part in query.split("&") if part)
            step = int(asked["step"]) if asked.get("step", "0") != "0" else None
            self._reply("image/png", frame_png(self.folder, turn, step))
        elif path.startswith("/steps/"):
            turn = int(path[len("/steps/") :])
            records, scoring = records_in(self.folder), scoring_in(self.folder)
            steps = len(turn_steps(records, turn, scoring))
            self._reply("application/json", json.dumps({"steps": steps}).encode())
        else:
            self.send_error(404)

    def _reply(self, kind, body):
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


def server(folder, port):
    """An HTTP server for the run folder, not yet serving; port 0 picks one."""
    handler = type("RunHandler", (_Handler,), {"folder": Path(folder)})
    return ThreadingHTTPServer(("127.0.0.1", port), handler)
