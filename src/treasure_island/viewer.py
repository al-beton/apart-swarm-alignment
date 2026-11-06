"""Drawing a run: one renderer behind the browser page and the GIF.

Everything visual reads `events.jsonl` and nothing else, so a frame can be
drawn while the game is still writing. `scene` turns the records up to a turn
into what a frame shows: the grid size, where every pirate stands (from the
turn's `crew`, so pirates that haven't acted yet are there too), whose turn
it is, what it said and the log lines it saw. `frame` draws that scene with
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

Implements: treasure-island/side-panel, treasure-island/readable-at-once, event-log/crew-positions, viewer/one-renderer, viewer/frame-shows-the-swarm, viewer/watch-live, viewer/render-gif, viewer/art-folder, viewer/sprite-from-definition, viewer/sprite-follows-action, viewer/crowds-fan-out, treasure-island/pokemon-style
"""

import io
import json
import math
import re
from functools import cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image, ImageChops

import assets
from assets.font import draw_text, wrap
from assets.pirates import pirate, portrait
from assets.ui import panel, speech_bubble
from treasure_island.config import parse_config
from treasure_island.looks import sprite_values

ASSETS = Path(assets.__file__).parent
SAND_TILES = ("sand", "sand-2", "sand-3")
TILE = 48
# How far apart pirates sharing a square stand, which is the size of a two-letter
# label, and where a label sits on a sprite: (left, top, right, bottom).
_FAN = (20, 14)
_LABEL_BOX = (14, 2, 34, 16)
_ROWS = 3
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
_BUBBLE_CHARACTERS = 90
FRAME_MS = 600


def records_in(folder):
    """Every record in the run's event log so far."""
    lines = (Path(folder) / "events.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def grid_size(folder, records):
    """The grid size from config.json, or the widest position seen plus one."""
    config = Path(folder) / "config.json"
    if config.exists():
        saved = json.loads(config.read_text())
        return saved["grid_size"] if "grid_size" in saved else saved["size"]
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
    if not isinstance(saved, list):  # the walking skeleton saves only a count
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


def _said(record):
    """What a pirate's turn says in its bubble: its words, else its actions."""
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
            actions.append(f"read line {action['line']}")
        else:
            actions.append(action["action"])
    return ", ".join(actions) or "..."


def _did(record):
    """What the turn did in plain words: its story without who, where or why."""
    story = record.get("story")
    if not story:
        return _said(record)
    what = re.sub(r"^Turn \d+: \S+ at \(\d+, \d+\) ", "", story)
    return what.rsplit(" Why: ", 1)[0] if record.get("thinking") else what


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


def scene(records, turn, size):
    """What the frame for `turn` shows, from the records up to and including it."""
    positions = dict(records[turn].get("crew", {}))
    for record in records:
        positions.setdefault(record["agent"], record["saw"]["position"])
    treasure = None
    for record in records[: turn + 1]:
        positions[record["agent"]] = record["outcome"]["position"]
        if record["outcome"]["found_treasure"]:
            treasure = record["outcome"]["position"]
    current = records[turn]
    return {
        "size": size,
        "turn": turn,
        "positions": positions,
        "acting": current["agent"],
        "bubble": _said(current),
        "did": _did(current),
        "thoughts": _thoughts(records, turn),
        "log": [line["text"] for line in current["log_shown"]],
        "treasure": treasure,
        "poses": _poses(records, turn),
        "dug": _dug(records, turn),
    }


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


def _draw_ground(image, size, shown):
    for x in range(size):
        for y in range(size):
            name = "dug" if (x, y) in shown["dug"] else _ground_tile(x, y)
            image.paste(_art(f"tiles/{name}"), (x * TILE, y * TILE))
    if shown["treasure"]:
        mark = _art("treasure/mark-x")
        x, y = shown["treasure"]
        image.paste(mark, (x * TILE, y * TILE), mark)


def fanned(count, square, size):
    """Where `count` pirates on one square stand, in pixels.

    Two columns of three rows fit six labels inside a square, which is what stops a
    neighbour's label landing on one. A bigger crowd adds columns, moved along if
    needed to keep every label on the board.
    """
    across = math.ceil(count / _ROWS)
    spots = []
    for place in range(count):
        column, row = place // _ROWS, place % _ROWS
        x = square[0] * TILE + (2 * column - across + 1) * _FAN[0] // 2
        spots.append((x, square[1] * TILE + row * _FAN[1]))
    lefts = [x for x, _ in spots]
    board = size * TILE
    shift = max(-(min(lefts) + _LABEL_BOX[0]), 0)
    shift += min(board - (max(lefts) + _LABEL_BOX[2]), 0)
    return [(x + shift, y) for x, y in spots]


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
    crowds = {}
    for agent, position in shown["positions"].items():
        crowds.setdefault(tuple(position), []).append(agent)
    placed = []
    for square, agents in crowds.items():
        placed += zip(agents, fanned(len(agents), square, shown["size"]), strict=True)
    return sorted(placed, key=lambda spot: spot[0] == shown["acting"])


def _draw_pirates(image, shown, pirates):
    for agent, spot in _placed(shown):
        sprite = _sprite(pirates[agent], *shown["poses"][agent])
        image.paste(sprite, spot, sprite)


def _draw_labels(image, shown, pirates):
    """Labels go over everything, so a crowd can always be told apart."""
    for agent, spot in _placed(shown):
        label = _label(pirates[agent], *shown["poses"][agent])
        image.paste(label, spot, label)


def bubble_box(position, bubble_size, size):
    """Where a bubble goes: above the pirate, or below the crowd if there's no room."""
    x, y = position
    width, height = bubble_size
    left = min(x * TILE + 6, max(0, size * TILE - width))
    above = y * TILE - height
    return left, above if above >= 0 else y * TILE + TILE + (_ROWS - 1) * _FAN[1]


def _draw_bubble(image, position, text, size):
    if len(text) > _BUBBLE_CHARACTERS:
        text = text[: _BUBBLE_CHARACTERS - 3] + "..."
    bubble = speech_bubble(text)
    image.paste(bubble, bubble_box(position, bubble.size, size), bubble)


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
    log = [line or "(blank)" for line in shown["log"][-LOG_LINES:]] or ["(nothing)"]
    log = [line[:PANEL_COLUMNS] for line in log]
    sections.append(("Log it saw:", log, LOG_LINES))
    for title, lines, most in sections:
        draw_text(image, (_PANEL_LEFT, y), title)
        y += LINE
        for line in _fitted(lines, most):
            draw_text(image, (_PANEL_LEFT, y), line)
            y += LINE
        y += LINE // 2
    return image


def frame(records, turn, size, pirates=None):
    """The image for one turn: ground, pirates, bubble and the side panel."""
    pirates = pirates or _default_pirates(_crew_names(records))
    shown = scene(records, turn, size)
    grid = max(size, 1) * TILE
    height = max(grid, PANEL_HEIGHT)
    image = Image.new("RGB", (grid + PANEL, height), "#2b2b2b")
    _draw_ground(image, size, shown)
    _draw_pirates(image, shown, pirates)
    _draw_bubble(image, shown["positions"][shown["acting"]], shown["bubble"], size)
    _draw_labels(image, shown, pirates)
    side = _panel_image(shown, height, pirates[shown["acting"]])
    image.paste(side, (grid, 0), side)
    return image


def _png(image):
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def frame_png(folder, turn):
    """The PNG the page serves for one turn, read fresh from the run folder."""
    records = records_in(folder)
    size = grid_size(folder, records)
    return _png(frame(records, turn, size, pirates_in(folder, records)))


def gif(folder):
    """The whole run as GIF bytes, one frame per turn, from the same frames."""
    records = records_in(folder)
    size = grid_size(folder, records)
    pirates = pirates_in(folder, records)
    frames = [
        Image.open(io.BytesIO(_png(frame(records, turn, size, pirates))))
        for turn in range(len(records))
    ]
    out = io.BytesIO()
    frames[0].save(
        out,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
    )
    return out.getvalue()


def render(folder, out=None):
    """Write the run's GIF next to its folder (or to `out`); return the path."""
    out = Path(out) if out else Path(folder).with_suffix(".gif")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(gif(folder))
    return out


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
let turns = 0, shown = -1, live = true;
const frame = document.getElementById("frame"), status = document.getElementById("status");
function show(turn) {
  shown = turn;
  frame.src = "/frame/" + turn + ".png?t=" + Date.now();
  status.textContent = "Turn " + turn + " of " + turns + (live ? " (live)" : "");
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
        if path == "/":
            self._reply("text/html", PAGE.encode())
        elif path == "/turns":
            count = len(records_in(self.folder))
            self._reply("application/json", json.dumps({"turns": count}).encode())
        elif path.startswith("/frame/") and path.endswith(".png"):
            turn = int(path[len("/frame/") : -len(".png")])
            self._reply("image/png", frame_png(self.folder, turn))
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
