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

Implements: treasure-island/side-panel, treasure-island/readable-at-once, event-log/crew-positions, viewer/one-renderer, viewer/frame-shows-the-swarm, viewer/watch-live, viewer/render-gif, viewer/art-folder, viewer/sprite-from-definition, viewer/sprite-follows-action, viewer/crowds-fan-out, treasure-island/pokemon-style, viewer/slideshow-file, treasure-island/slideshow, viewer/long-log-lines, treasure-island/treasure-mark, treasure-island/log-at-bottom
"""

import base64
import io
import json
import math
import re
from functools import cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image, ImageChops

import assets
from assets.font import draw_text, text_width, wrap
from assets.pirates import pirate, portrait
from assets.ui import panel, speech_bubble
from treasure_island.config import parse_config
from treasure_island.game_state import GameState
from treasure_island.looks import sprite_values
from treasure_island.pirates_log import one_line

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
STRIP_ROWS = 5
STRIP = 24 + (STRIP_ROWS + 1) * LINE + 4  # the parchment's edges, a heading and rows
_STRIP_LEFT = 14
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
    if "grid_size" not in saved:  # the walking skeleton saves no such thing
        return None
    state = GameState(
        saved["grid_size"], saved["crew_size"], saved["landing_square"], saved["seed"]
    )
    return state.treasure


def _log_so_far(records, turn):
    """The pirates' log as it stands after `turn`: each turn added one line to it."""
    lines = []
    for number, record in enumerate(records[: turn + 1], start=1):
        words = [a["text"] for a in record["did"] if a["action"] == "write"]
        lines.append((number, " ".join(one_line(word) for word in words)))
    return lines


def _mark(records, treasure, found):
    """Which mark the reader sees and where: an X once dug up, else a question mark."""
    if found:
        return ("mark-x", tuple(found))
    known = treasure
    if known is None and records and records[-1].get("game_over"):
        known = tuple(records[-1]["game_over"]["treasure"])
    return ("mark-question", tuple(known)) if known else None


def scene(records, turn, size, treasure=None):
    """What the frame for `turn` shows, from the records up to and including it."""
    positions = dict(records[turn].get("crew", {}))
    for record in records:
        positions.setdefault(record["agent"], record["saw"]["position"])
    found = None
    for record in records[: turn + 1]:
        positions[record["agent"]] = record["outcome"]["position"]
        if record["outcome"]["found_treasure"]:
            found = record["outcome"]["position"]
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
        "treasure": found,
        "mark": _mark(records, treasure, found),
        "log_so_far": _log_so_far(records, turn),
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
    if shown["mark"] and shown["mark"][0] == "mark-question":
        _draw_mark(image, shown)


def _draw_mark(image, shown):
    name, (x, y) = shown["mark"]
    mark = _art(f"treasure/{name}")
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


def log_rows(lines, width):
    """The rows of the log strip: every line wrapped, the newest in view."""
    columns = width // text_width("x")
    rows = []
    # Only the newest lines can be in view, so a long game costs no more than a short.
    for number, text in lines[-STRIP_ROWS:]:
        rows += wrap(f"{number}: {text}".rstrip(), columns)
    return rows[-STRIP_ROWS:]


def _strip_image(shown, width):
    image = panel(width, STRIP)
    draw_text(image, (_STRIP_LEFT, 12), "The pirates' log")
    rows = log_rows(shown["log_so_far"], width - 2 * _STRIP_LEFT)
    for row, text in enumerate(rows, start=1):
        draw_text(image, (_STRIP_LEFT, 14 + row * LINE), text)
    return image


def frame(records, turn, size, pirates=None, treasure=None):
    """The image for one turn: ground, pirates, bubble, side panel and log strip."""
    pirates = pirates or _default_pirates(_crew_names(records))
    shown = scene(records, turn, size, treasure)
    grid = max(size, 1) * TILE
    board = max(grid, PANEL_HEIGHT)
    image = Image.new("RGB", (grid + PANEL, board + STRIP), "#2b2b2b")
    _draw_ground(image, size, shown)
    _draw_pirates(image, shown, pirates)
    _draw_bubble(image, shown["positions"][shown["acting"]], shown["bubble"], size)
    _draw_labels(image, shown, pirates)
    # The X goes over everything, because whoever dug it up is standing on it, and it's
    # the moment a reader most wants to see. It's open enough for labels to show through.
    if shown["mark"] and shown["mark"][0] == "mark-x":
        _draw_mark(image, shown)
    side = _panel_image(shown, board, pirates[shown["acting"]])
    image.paste(side, (grid, 0), side)
    strip = _strip_image(shown, grid + PANEL)
    image.paste(strip, (0, board), strip)
    return image


def _png(image):
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def frame_png(folder, turn):
    """The PNG the page serves for one turn, read fresh from the run folder."""
    records = records_in(folder)
    size = grid_size(folder, records)
    pirates = pirates_in(folder, records)
    return _png(frame(records, turn, size, pirates, treasure_in(folder, records)))


def gif(folder):
    """The whole run as GIF bytes, one frame per turn, from the same frames."""
    records = records_in(folder)
    size = grid_size(folder, records)
    pirates = pirates_in(folder, records)
    treasure = treasure_in(folder, records)
    frames = [
        Image.open(io.BytesIO(_png(frame(records, turn, size, pirates, treasure))))
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
