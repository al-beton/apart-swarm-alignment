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
turn's own frame. `walk_steps` says which steps a turn has, and the GIF and the page
both draw exactly those.

Implements: viewer/cave-drawn, treasure-island/cave, viewer/turn-marked, viewer/story-caption, treasure-island/side-panel, treasure-island/readable-at-once, event-log/crew-positions, viewer/one-renderer, viewer/frame-shows-the-swarm, viewer/watch-live, viewer/render-gif, viewer/art-folder, viewer/sprite-from-definition, viewer/sprite-follows-action, viewer/walks-between-squares, treasure-island/pokemon-style, viewer/slideshow-file, treasure-island/slideshow, viewer/long-log-lines, treasure-island/treasure-mark, treasure-island/log-at-bottom, runs/same-in-every-process
"""

import base64
import io
import json
from functools import cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image, ImageChops

import assets
from assets.cave import going_in, hat_stack
from assets.font import draw_text, text_width, wrap
from assets.pirates import pirate, portrait
from assets.ui import panel, scroll_note
from treasure_island.config import parse_config
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
LOG_LINES = 4
THOUGHTS = 3
LINE = 12
_DID_LINES = 3
_THOUGHT_LINES = 6
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


def _read(record):
    """The lines a read returned, or None on a turn that didn't read."""
    if not any(action["action"] == "read" for action in record["did"]):
        return None
    return [_shown(line) for line in record["log_shown"]]


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


def _shown(line):
    """A line a pirate was shown, with who wrote it when the record says."""
    return f"{line['by']}: {line['text']}" if "by" in line else line["text"]


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


def walk_steps(records, turn):
    """The steps a turn is drawn in: 1 to WALK_FRAMES for a move, else [None]."""
    if _walk(records[turn]):
        return list(range(1, WALK_FRAMES + 1))
    return [None]


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


def scene(records, turn, size, treasure=None, step=None):
    """What the frame for `turn` shows, from the records up to and including it.

    `step`, one of `walk_steps`, is how far along its walk a moving pirate is drawn.
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
        "read": _read(current),
        "treasure": found,
        "mark": _mark(records, treasure, found),
        "log_so_far": _log_so_far(records, turn),
        "poses": _poses(records, turn),
        "dug": _dug(records, turn),
        "inside": inside,
        "going_in": going,
    }
    if step is not None and step < WALK_FRAMES and _walk(current):
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


def _draw_cave(image, shown, pirates):
    """The open cave, its gold glinting turn by turn, with a hat for each pirate inside."""
    x, y = shown["mark"][1]
    cave = _art("treasure/cave" if shown["turn"] % 2 == 0 else "treasure/cave-2")
    square = cave.copy()
    hats = [pirates[agent][1:] for agent in shown["inside"]]  # (colour, label)
    square.alpha_composite(hat_stack(hats))
    image.paste(square, (x * TILE, y * TILE), square)


def _draw_going_in(image, shown, pirates):
    """The pirate entering this turn, sinking into the cave's mouth."""
    if shown["going_in"]:
        x, y = shown["mark"][1]
        sprite = going_in(*pirates[shown["going_in"]], 1)
        image.paste(sprite, (x * TILE, y * TILE), sprite)


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
        sprite = _sprite(pirates[agent], *shown["poses"][agent])
        image.paste(sprite, spot, sprite)


def _draw_labels(image, shown, pirates):
    """Labels go over the pirates and the arrow, so every pirate can be told apart."""
    for agent, spot in _placed(shown):
        if agent == shown["going_in"]:
            continue  # its back is turned as it goes in
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


def _panel_image(shown, height, look):
    image = panel(PANEL, height)
    draw_text(image, (_PANEL_LEFT, 14), f"Turn {shown['turn']}")
    head = portrait(*look)
    image.paste(head, PORTRAIT, head)
    draw_text(image, (_TEXT_LEFT, PORTRAIT[1] + 8), shown["acting"])
    draw_text(image, (_TEXT_LEFT, PORTRAIT[1] + 8 + LINE), "is acting")
    y = PORTRAIT[1] + head.height + 8
    sections = [("It did:", wrapped(shown["did"]), _DID_LINES)]
    if shown["thoughts"]:
        lines = [line for thought in shown["thoughts"] for line in wrapped(thought)]
        # The latest thought matters most, so older lines are the ones to go.
        sections.append(("Thinking:", lines[-_THOUGHT_LINES:], _THOUGHT_LINES))
    if shown["read"] is not None:
        read = [line or "(blank)" for line in shown["read"][-LOG_LINES:]]
        read = [line[:PANEL_COLUMNS] for line in read or ["(nothing new)"]]
        sections.append(("It read:", read, LOG_LINES))
    for title, lines, most in sections:
        draw_text(image, (_PANEL_LEFT, y), title)
        y += LINE
        for line in _fitted(lines, most):
            draw_text(image, (_PANEL_LEFT, y), line)
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


def frame(records, turn, size, pirates=None, treasure=None, step=None):
    """The image for one turn: ground, pirates, turn arrow, note, panel, caption, log."""
    pirates = pirates or _default_pirates(_crew_names(records))
    shown = scene(records, turn, size, treasure, step)
    grid = max(size, 1) * TILE
    board = max(grid, PANEL_HEIGHT)
    width = grid + PANEL
    caption = caption_height(records, width)
    image = Image.new("RGB", (width, board + caption + STRIP), "#2b2b2b")
    _draw_ground(image, size, shown, pirates)
    _draw_pirates(image, shown, pirates)
    _draw_going_in(image, shown, pirates)
    arrow, spot = turn_arrow(shown)
    image.paste(arrow, spot, arrow)  # before the note and labels, so it covers neither
    arrow_box = (*spot, spot[0] + arrow.width, spot[1] + arrow.height)
    _draw_labels(image, shown, pirates)
    # The note goes over the labels, so what was written always shows in full.
    _draw_note(image, shown, arrow_box)
    side = _panel_image(shown, board, pirates[shown["acting"]])
    image.paste(side, (grid, 0), side)
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
    return _png(frame(records, turn, size, pirates, treasure, step=step))


def gif(folder):
    """The whole run as GIF bytes, every turn in its steps, from the same frames."""
    records = records_in(folder)
    size = grid_size(folder, records)
    pirates = pirates_in(folder, records)
    treasure = treasure_in(folder, records)
    frames, durations = [], []
    for turn in range(len(records)):
        for step in walk_steps(records, turn):
            drawn = frame(records, turn, size, pirates, treasure, step=step)
            frames.append(Image.open(io.BytesIO(_png(drawn))))
            last = step is None or step == WALK_FRAMES
            durations.append(FRAME_MS if last else WALK_MS)
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


def slideshow_page(folder):
    """One HTML file holding every turn's frame and story, as text."""
    turns = [
        {
            "frame": base64.b64encode(frame_png(folder, number)).decode(),
            "story": record.get("story", ""),
        }
        for number, record in enumerate(records_in(folder))
    ]
    # No raw "<" in the data, which is still the same JSON, so a note can't close the
    # script it's held in or stop it closing. Escaping "</" alone misses "<!-- <script>".
    data = json.dumps(turns, ensure_ascii=False).replace("<", "\\u003c")
    return SLIDESHOW.replace("@TURNS@", data)


def slideshow(folder, out=None):
    """Write the slideshow next to the run's folder (or to `out`); return the path."""
    out = Path(out) if out else Path(folder).with_suffix(".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(slideshow_page(folder), encoding="utf-8")
    return out


SLIDESHOW = """<!doctype html>
<html><head><meta charset="utf-8"><title>Treasure Island</title>
<style>
body { background: #1a1a1a; color: #eee; font: 14px sans-serif; text-align: center; }
img { image-rendering: pixelated; margin-top: 1em; max-width: 100%; }
#story { max-width: 60em; margin: 1em auto; min-height: 3em; }
</style></head>
<body>
<p id="status"></p>
<img id="frame" alt="the current turn">
<p id="story"></p>
<p>← → step through turns · Home and End jump to the first and the last</p>
<script>
const TURNS = @TURNS@;
const frame = document.getElementById("frame");
const story = document.getElementById("story");
const status = document.getElementById("status");
let shown = 0;
function show(turn) {
  shown = Math.max(0, Math.min(turn, TURNS.length - 1));
  frame.src = "data:image/png;base64," + TURNS[shown].frame;
  story.textContent = TURNS[shown].story;
  status.textContent = "Turn " + shown + " (" + (shown + 1) + " of " + TURNS.length + ")";
}
document.addEventListener("keydown", (key) => {
  if (key.key === "ArrowLeft") show(shown - 1);
  if (key.key === "ArrowRight") show(shown + 1);
  if (key.key === "Home") show(0);
  if (key.key === "End") show(TURNS.length - 1);
});
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
function draw(turn, step) {
  const at = step ? "?step=" + step + "&t=" : "?t=";
  frame.src = "/frame/" + turn + ".png" + at + Date.now();
}
async function show(turn) {
  const forward = turn === shown + 1, mine = ++walk;
  shown = turn;
  status.textContent = "Turn " + turn + " of " + turns + (live ? " (live)" : "");
  // Stepping forward onto a move plays its walk; jumping anywhere else doesn't.
  const steps = forward ? (await (await fetch("/steps/" + turn)).json()).steps : 1;
  for (let step = 1; step < steps && mine === walk; step++) {
    draw(turn, step);
    await new Promise((done) => setTimeout(done, @WALK_MS@));
  }
  if (mine === walk) draw(turn, 0);
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
            steps = len(
                walk_steps(records_in(self.folder), int(path[len("/steps/") :]))
            )
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
