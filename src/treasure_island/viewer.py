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

Implements: viewer/cave-drawn, treasure-island/cave, viewer/turn-marked, viewer/story-caption, treasure-island/side-panel, treasure-island/readable-at-once, event-log/crew-positions, viewer/one-renderer, viewer/frame-shows-the-swarm, viewer/watch-live, viewer/render-gif, viewer/art-folder, viewer/sprite-from-definition, viewer/sprite-follows-action, viewer/walks-between-squares, treasure-island/pokemon-style, viewer/slideshow-file, viewer/game-page, viewer/score-counter, viewer/transcript, viewer/board-framed, viewer/dig-steps, viewer/enter-steps, treasure-island/slideshow, viewer/long-log-lines, treasure-island/treasure-mark, treasure-island/log-at-bottom, runs/same-in-every-process, treasure-island/square-names
"""

import base64
import io
import json
import re
from functools import cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageChops

import assets
from assets.board import EDGE_BOTTOM, EDGE_LEFT, board_edges
from assets.cave import ENTER_STEPS, entering, hat_stack
from assets.dig import DIG_STEPS, dig_ground, digging
from assets.font import draw_text, text_width, wrap
from assets.pirates import pirate, portrait
from assets.pixels import DARK
from assets.ui import open_scroll, panel, scroll_note
from treasure_island.config import DEFAULTS, parse_config
from treasure_island.game_state import GameState
from treasure_island.looks import sprite_values
from treasure_island.pirates_log import one_line

ASSETS = Path(assets.__file__).parent
SAND_TILES = ("sand", "sand-2", "sand-3")
TILE = 48
# Where a label sits on a sprite: (left, top, right, bottom).
_LABEL_BOX = (14, 2, 34, 16)
# The turn arrow floats this far above the acting pirate's hat, centred, as on the
# art sheet, so it never covers the label; a note goes above the arrow.
ARROW_ROOM = 14
_ARROW_LEFT = 16
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


def _crew_names(records):
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
    names = _crew_names(records)
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
    for name in _crew_names(records):
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


def _log_so_far(records, turn):
    """The scroll as it stands after `turn`: only a note adds a line to it."""
    lines = []
    for record in records[: turn + 1]:
        for action in record["did"]:
            if action["action"] == "write":
                note = f"{record['agent']}: {one_line(action['text'])}"
                lines.append((len(lines) + 1, note))
    return lines


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


def _motion(record):
    """What a turn plays out and in how many steps: a walk, a dig, going in, or none."""
    if _walk(record):
        return "walk", WALK_FRAMES
    if record["outcome"].get("in_cave"):
        return "enter", ENTER_STEPS
    if any(action["action"] == "dig" for action in record["did"]):
        return "dig", DIG_STEPS
    return None, 1


def turn_steps(records, turn, scoring=None):
    """The steps a turn is drawn in: 1 to N for a walk, dig or going in, else [None].

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
    """The run's score numbers, as the counter needs them."""

    turns_per_pirate: int
    in_cave: int
    per_turn_left: int


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
    if recorded:
        return Scoring(*(recorded[field] for field in fields))
    path = Path(folder) / "config.json"
    saved = json.loads(path.read_text()) if path.exists() else {}
    return Scoring(*(saved.get(field, DEFAULTS[field]) for field in fields))


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
    seats = {name: index for index, name in enumerate(_crew_names(records))}
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
        "log_so_far": _log_so_far(records, turn),
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
    if shown["mark"] and shown["mark"][0] == "mark-question":
        _draw_mark(image, shown)
    if shown["mark"] and shown["mark"][0] == "cave":
        _draw_cave(image, shown, pirates)
    if shown["digging"]:
        step, before = shown["digging"]
        x, y = shown["positions"][shown["acting"]]
        image.paste(dig_ground(step, _art(f"tiles/{before}")), (x * TILE, y * TILE))


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
    """Labels go over the pirates and the arrow, so every pirate can be told apart."""
    for agent, spot in _placed(shown):
        if agent == shown["going_in"]:
            continue  # its back is turned as it goes in
        if shown["digging"] and agent == shown["acting"]:
            continue  # its sprite carries its label as it heaves up and down
        label = _label(pirates[agent], *shown["poses"][agent])
        image.paste(label, spot, label)


def note_box(position, note_size, size):
    """Where a note goes: above the pirate's arrow, or below it if there's no room."""
    x, y = position
    width, height = note_size
    left = min(x * TILE + 6, max(0, size * TILE - width))
    above = y * TILE - ARROW_ROOM - height
    # With no room above, the arrow goes under the feet and the note under that.
    return left, above if above >= 0 else y * TILE + TILE + ARROW_ROOM + 2


def _overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def turn_arrow(shown):
    """The turn arrow and where it goes: over the acting pirate's hat.

    Where that's off the board or on another pirate's label, it goes under the
    feet instead, pointing up (default, Al to confirm). Each place must be on
    the board.
    """
    placed = _placed(shown)
    x, y = dict(placed)[shown["acting"]]
    labels = [
        (lx + _LABEL_BOX[0], ly + _LABEL_BOX[1], lx + _LABEL_BOX[2], ly + _LABEL_BOX[3])
        for agent, (lx, ly) in placed
        if agent != shown["acting"]
    ]
    down = _art("ui/turn-arrow")
    up = down.transpose(Image.FLIP_TOP_BOTTOM)
    left = x + _ARROW_LEFT
    candidates = [
        (down, (left, y - ARROW_ROOM)),
        (up, (left, y + TILE + 2)),
    ]
    bottom = shown["size"] * TILE
    for arrow, (ax, ay) in candidates:
        box = (ax, ay, ax + arrow.width, ay + arrow.height)
        on_board = ay >= 0 and box[3] <= bottom
        if on_board and not any(_overlap(box, label) for label in labels):
            return arrow, (ax, ay)
    return candidates[1]


def note_spot(shown, note_size, arrow_box):
    """Where the writer's note goes: beside the writer, clear of every other pirate.

    It tries above, then right, then left, then below, and takes the first spot
    on the board that covers no other pirate and not the turn arrow, so the note
    reads as the writer's own. With none, it falls back on `note_box`.
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
        clear = not any(_overlap(box, other) for other in [*others, arrow_box])
        if on_board and clear:
            return left, top
    left, top = note_box((x, y), note_size, size)
    if _overlap((left, top, left + width, top + height), arrow_box):
        top = arrow_box[3] + 2  # an arrow under the feet: the note goes below it
    return left, top


def _draw_note(image, shown, arrow_box):
    text = shown["note"]
    if text is None:
        if shown["reading"]:
            # A reader holds the scroll open, with none of its words on it.
            held = open_scroll()
            image.paste(held, note_spot(shown, held.size, arrow_box), held)
        return
    if len(text) > _NOTE_CHARACTERS:
        text = text[: _NOTE_CHARACTERS - 3] + "..."
    note = scroll_note(text)
    image.paste(note, note_spot(shown, note.size, arrow_box), note)


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


def caption_rows(story, width):
    """A line of the story, wrapped to fit a frame this wide."""
    return wrap(story, (width - 2 * _STRIP_LEFT) // text_width("x"))


def rows_height(rows):
    """How tall a caption with this many rows is, parchment's edges included."""
    return 24 + rows * LINE


def caption_height(records, width):
    """Tall enough for the longest line in this run, so no frame needs another size."""
    rows = [len(caption_rows(r.get("story", ""), width)) for r in records]
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
    above = y * TILE - ARROW_ROOM - LINE  # clear of the turn arrow over the cave
    top = above if above >= 0 else (y + 1) * TILE + 2
    draw_text(image, (left + 1, top + 1), words)  # a dark edge, so it reads on sand
    draw_text(image, (left, top), words, SCORE_INK)


def _draw_score(image, shown, grid):
    """The crew's score so far, at the top of the frame, right of the turn number."""
    words = f"Score {shown['score']}"
    draw_text(image, (grid + PANEL - _PANEL_LEFT - text_width(words), 14), words)


# Two arguments over the limit: `step` and `scoring` sit beside the others callers pass.
def frame(records, turn, size, pirates=None, treasure=None, step=None, scoring=None):  # noqa: PLR0913
    """The image for one turn: ground, pirates, turn arrow, note, panel, caption, log."""
    pirates = pirates or _default_pirates(_crew_names(records))
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
    _draw_ground(sand, size, shown, pirates)
    _draw_pirates(sand, shown, pirates)
    arrow, at = turn_arrow(shown)
    sand.paste(arrow, at, arrow)  # before the note and labels, so it covers neither
    arrow_box = (*at, at[0] + arrow.width, at[1] + arrow.height)
    _draw_labels(sand, shown, pirates)
    # The note goes over the labels, so what was written always shows in full.
    _draw_note(sand, shown, arrow_box)
    _draw_gains(sand, shown)
    image.paste(sand, spot[:2])
    side = _panel_image(shown, board, pirates[shown["acting"]])
    image.paste(side, (right, 0), side)
    _draw_score(image, shown, right)
    words = _caption_image(records[turn].get("story", ""), width, caption)
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


def _scroll_writes(records):
    """The lines each turn added to the scroll, numbered as the scroll numbers them."""
    line, writes = 0, []
    for record in records:
        wrote = []
        for action in record.get("did", []):
            if action.get("action") == "write":
                line += 1
                # As the scroll keeps it, on one line; `did` keeps it as written.
                text = one_line(action["text"])
                wrote.append({"line": line, "by": record["agent"], "text": text})
        writes.append(wrote)
    return writes


def turn_records(records):
    """Each turn's whole record as the game page and the transcript both show it."""
    return [
        {
            "story": record.get("story", ""),
            "turn": record.get("turn", number),
            "agent": record["agent"],
            "happened": record.get("happened", ""),
            "prompt": record.get("saw", {}).get("prompt", ""),
            "thinking": record.get("thinking") or "",
            "refused": record.get("refused", []),
            "did": record.get("did", []),
            "result": record.get("result", ""),
            "wrote": wrote,
        }
        for number, (record, wrote) in enumerate(
            zip(records, _scroll_writes(records), strict=True)
        )
    ]


def slideshow_page(folder):
    """The game page: every turn's frame and whole record, as one HTML file's text."""
    records = records_in(folder)
    turns = [
        {"frame": base64.b64encode(frame_png(folder, number)).decode(), **turn}
        for number, turn in enumerate(turn_records(records))
    ]
    # No raw "<" in the data, which is still the same JSON, so a note can't close the
    # script it's held in or stop it closing. Escaping "</" alone misses "<!-- <script>".
    data = json.dumps(turns, ensure_ascii=False).replace("<", "\\u003c")
    return SLIDESHOW.replace("@TURNS@", data)


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


def _transcript_turn(turn):
    parts = [f"## Turn {turn['turn']}: {turn['agent']}"]
    if turn["prompt"]:
        summary = f"What it was shown ({len(turn['prompt'])} characters)"
        details = f"<details>\n<summary>{summary}</summary>\n\n"
        parts.append(details + _fenced(turn["prompt"]) + "\n\n</details>")
    else:
        parts.append("*No prompt recorded: a scripted pirate reads no words.*")
    thinking = _quoted(turn["thinking"]) if turn["thinking"] else None
    parts.append("**Its thinking**\n\n" + (thinking or "*No thinking recorded.*"))
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
    parts += [_transcript_turn(turn) for turn in turn_records(records)]
    game_over = records[-1].get("game_over") if records else None
    if game_over:
        ending = (
            f"## Game over\n\n{game_over['story']}\n\n**Score:** {game_over['score']}"
        )
    else:
        ending = "*This game has no game over line yet: it stopped or is still going.*"
    parts.append(ending)
    return "\n\n".join(parts) + "\n"


def write_transcript(folder):
    """Write `transcript.md` into the run folder; return its path."""
    out = Path(folder) / "transcript.md"
    out.write_text(transcript(folder), encoding="utf-8")
    return out


# Every word from the game goes in with textContent, never as markup.
SLIDESHOW = """<!doctype html>
<html><head><meta charset="utf-8"><title>Treasure Island</title>
<style>
body { background: #1a1a1a; color: #eee; font: 14px sans-serif; margin: 0 16px; }
header { display: flex; gap: 1em; align-items: baseline; flex-wrap: wrap; }
h1 { font-size: 18px; } h2 { font-size: 16px; margin: 0 0 .5em; }
h3 { font-size: 12px; text-transform: uppercase; color: #aaa; margin: 1em 0 .3em; }
.page { display: grid; grid-template-columns: auto minmax(0, 2fr) minmax(0, 1fr);
  gap: 16px; align-items: start; }
.page > section { min-width: 0; }
@media (max-width: 1100px) { .page { grid-template-columns: minmax(0, 1fr); } }
img { image-rendering: pixelated; max-width: 100%; display: block; }
pre, #story, #scroll li { white-space: pre-wrap; overflow-wrap: anywhere; margin: 0; }
pre { font: 13px/1.45 ui-monospace, Menlo, monospace; background: #222;
  padding: .6em; border-radius: 4px; }
.thinking { color: #9a9a9a; font-style: italic; }
.refused { color: #e0a060; }
.empty { color: #777; }
details summary { cursor: pointer; color: #aaa; }
#prompt { max-height: 40em; overflow: auto; }
#turns { position: relative; list-style: none; padding: 0; max-height: 18em; overflow: auto; margin: .5em 0; }
#turns button { all: unset; display: block; width: 100%; cursor: pointer;
  padding: 2px 4px; overflow-wrap: anywhere; }
#turns button.now { background: #3a3a5a; }
#turns button:hover { background: #2c2c2c; }
#scroll { padding-left: 0; list-style: none; max-height: 40em; overflow: auto; }
#scroll li { padding: 2px 0; border-bottom: 1px solid #2a2a2a; }
</style></head>
<body>
<header>
<h1>Treasure Island</h1>
<span id="status"></span>
<label>Show <select id="pirate"><option value="">every pirate</option></select></label>
<span class="empty">← → step through turns · Home and End jump to the first and last</span>
</header>
<main class="page">
<section>
<img id="frame" alt="the board on the current turn">
<p id="story"></p>
<ol id="turns"></ol>
</section>
<section id="record">
<h2 id="who"></h2>
<details><summary id="shown">What it was shown</summary><pre id="prompt"></pre></details>
<h3>Its thinking</h3><pre id="thinking" class="thinking"></pre>
<div id="refused"></div>
<h3>What it did</h3><pre id="did"></pre>
<h3>The result</h3><pre id="result"></pre>
</section>
<section>
<h3>The scroll so far</h3>
<ol id="scroll"></ol>
</section>
</main>
<script>
const TURNS = @TURNS@;
const $ = (id) => document.getElementById(id);
const filter = $("pirate"), list = $("turns");
let shown = 0, visible = [];
function text(id, words, none) {
  $(id).textContent = words || none;
  $(id).classList.toggle("empty", !words);
}
function call(action) {
  const { action: name, ...rest } = action;
  return Object.keys(rest).length ? name + " " + JSON.stringify(rest) : name;
}
for (const name of [...new Set(TURNS.map((t) => t.agent))]) {
  const option = document.createElement("option");
  option.value = option.textContent = name;
  filter.appendChild(option);
}
function listTurns() {
  visible = TURNS.map((t, i) => i).filter((i) => !filter.value || TURNS[i].agent === filter.value);
  list.replaceChildren(...visible.map((i) => {
    const item = document.createElement("li"), button = document.createElement("button");
    button.dataset.turn = i;
    button.textContent = "Turn " + TURNS[i].turn + " · " + TURNS[i].agent + " · " + TURNS[i].happened;
    item.appendChild(button);
    return item;
  }));
}
function show(turn) {
  shown = turn;
  const t = TURNS[turn];
  $("frame").src = "data:image/png;base64," + t.frame;
  $("story").textContent = t.story;
  $("status").textContent = "Turn " + t.turn + " (" + (turn + 1) + " of " + TURNS.length + ")";
  $("who").textContent = "Turn " + t.turn + ": " + t.agent;
  $("shown").textContent = "What it was shown (" + t.prompt.length + " characters)";
  text("prompt", t.prompt, "No prompt recorded: a scripted pirate reads no words.");
  text("thinking", t.thinking, "No thinking recorded.");
  $("refused").replaceChildren(...t.refused.map((bad) => {
    const line = document.createElement("pre");
    line.className = "refused";
    line.textContent = "A reply that wasn't a tool call: " + bad.reply + "\\n(" + bad.why + ")";
    return line;
  }));
  text("did", t.did.map(call).join("\\n"), "Nothing: the turn passed.");
  text("result", t.result, "No result recorded.");
  $("scroll").replaceChildren(...TURNS.slice(0, turn + 1).flatMap((each) => each.wrote).map((w) => {
    const line = document.createElement("li");
    line.textContent = w.line + " " + w.by + ": " + w.text;
    return line;
  }));
  $("scroll").scrollTop = $("scroll").scrollHeight;  // the newest line in view
  for (const button of list.querySelectorAll("button")) {
    const now = Number(button.dataset.turn) === turn;
    button.classList.toggle("now", now);
    // Scroll the list alone, never the page, so the board stays where it is.
    const top = button.offsetTop, bottom = top + button.offsetHeight;
    if (now && (top < list.scrollTop || bottom > list.scrollTop + list.clientHeight)) {
      list.scrollTop = top - list.clientHeight / 2;
    }
  }
}
function step(by) {
  const at = visible.indexOf(shown);
  const next = at < 0 ? visible.find((i) => i > shown) ?? visible.at(-1) : visible[at + by];
  if (next !== undefined) show(next);
}
list.addEventListener("click", (click) => {
  const button = click.target.closest("button");
  if (button) show(Number(button.dataset.turn));
});
filter.addEventListener("change", () => {
  listTurns();
  if (!visible.includes(shown) && visible.length) step(1); else show(shown);
});
document.addEventListener("keydown", (key) => {
  if (key.target === filter) return;
  if (key.key === "ArrowLeft") step(-1);
  if (key.key === "ArrowRight") step(1);
  if (key.key === "Home" && visible.length) show(visible[0]);
  if (key.key === "End" && visible.length) show(visible.at(-1));
});
listTurns();
show(0);
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
