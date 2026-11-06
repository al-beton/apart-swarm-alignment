"""Drawing a run: one renderer behind the browser page and the GIF.

Everything visual reads `events.jsonl` and nothing else, so a frame can be
drawn while the game is still writing. `scene` turns the records up to a turn
into what a frame shows: the grid size, where every pirate stands (from the
turn's `crew`, so pirates that haven't acted yet are there too), whose turn
it is, what it said and the log lines it saw. `frame` draws that scene with
Pillow. The browser page asks for `/frame/<turn>.png` and the GIF strings the
same PNGs together, which is what keeps the two from ever disagreeing.

Tiles are looked up in `assets/` by their path there (`tiles/sand.png`,
`treasure/mark-x.png`), and plain shapes stand in for whatever isn't there
yet, pirates included.

Implements: event-log/crew-positions, viewer/one-renderer, viewer/frame-shows-the-swarm, viewer/watch-live, viewer/render-gif, viewer/art-folder
"""

import io
import json
from functools import cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parents[2] / "assets"
TILE = 48
PANEL = 220
LOG_LINES = 4
LINE = 18
COLOURS = ["#d62828", "#1d4ed8", "#15803d", "#b45309", "#7e22ce", "#0e7490"]
SAND = "#f1d9a0"
GRID = "#c9b67c"
FRAME_MS = 600


def records_in(folder):
    """Every record in the run's event log so far."""
    lines = (Path(folder) / "events.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def grid_size(folder, records):
    """The grid size from config.json, or the widest position seen plus one."""
    config = Path(folder) / "config.json"
    if config.exists():
        return json.loads(config.read_text())["size"]
    spots = [r["saw"]["position"] for r in records]
    spots += [r["outcome"]["position"] for r in records]
    return max((max(x, y) for x, y in spots), default=0) + 1


def _said(record):
    """What a pirate's turn says in its bubble: its words, else its actions."""
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
        "log": [line["text"] for line in current["log_shown"]],
        "treasure": treasure,
    }


@cache
def _font(px):
    return ImageFont.load_default(px)


@cache
def _loaded(path):
    if not path.is_file():
        return None
    return Image.open(path).convert("RGBA").resize((TILE, TILE), Image.NEAREST)


def _art(name):
    """The asset image scaled to a tile, or None when there's no art for it."""
    return _loaded(ASSETS / f"{name}.png")  # ASSETS is read here so tests can move it


def rgb(colour):
    """A `#rrggbb` colour as the tuple Pillow reads back from an image."""
    return tuple(int(colour[i : i + 2], 16) for i in (1, 3, 5))


def _colour(agent):
    letter = agent.rsplit("-", 1)[-1][:1]
    return COLOURS[(ord(letter) - ord("a")) % len(COLOURS)] if letter else COLOURS[0]


def _draw_grid(image, draw, size, treasure):
    sand = _art("tiles/sand")
    for x in range(size):
        for y in range(size):
            box = (x * TILE, y * TILE, (x + 1) * TILE - 1, (y + 1) * TILE - 1)
            if sand:
                image.paste(sand, box[:2], sand)
            else:
                draw.rectangle(box, fill=SAND, outline=GRID)
    if treasure:
        x, y = treasure
        chest = _art("treasure/mark-x")
        if chest:
            image.paste(chest, (x * TILE, y * TILE), chest)
        else:
            draw.line(
                (x * TILE + 6, y * TILE + 6, (x + 1) * TILE - 6, (y + 1) * TILE - 6),
                fill="black",
                width=3,
            )
            draw.line(
                (x * TILE + 6, (y + 1) * TILE - 6, (x + 1) * TILE - 6, y * TILE + 6),
                fill="black",
                width=3,
            )


def _draw_pirate(draw, agent, position, place, crowd):
    """A coloured disc with the pirate's letter; `place` of `crowd` on its square."""
    x, y = position
    size = TILE if crowd == 1 else TILE // 2
    left = x * TILE + (place % 2) * size
    top = y * TILE + (place // 2) * size
    draw.ellipse(
        (left + 3, top + 3, left + size - 4, top + size - 4),
        fill=_colour(agent),
        outline="black",
    )
    letter = agent.rsplit("-", 1)[-1][:1].upper()
    font = _font(14 if crowd == 1 else 10)
    draw.text(
        (left + size / 2, top + size / 2), letter, fill="white", font=font, anchor="mm"
    )


def _draw_pirates(draw, positions):
    """Pirates sharing a square are fanned into quarters, so all stay visible."""
    crowds = {}
    for agent, position in positions.items():
        crowds.setdefault(tuple(position), []).append(agent)
    for position, agents in crowds.items():
        for place, agent in enumerate(agents[:4]):
            _draw_pirate(draw, agent, position, place, len(agents))


def _draw_bubble(draw, position, text, size):
    text = text if len(text) <= 28 else text[:27] + "…"
    font = _font(12)
    width = draw.textlength(text, font=font) + 10
    x, y = position
    left = min(max(0, x * TILE + TILE / 2 - width / 2), max(0, size * TILE - width))
    top = max(0, y * TILE - 22)
    draw.rounded_rectangle(
        (left, top, left + width, top + 18), radius=5, fill="white", outline="black"
    )
    draw.text((left + 5, top + 3), text, fill="black", font=font)


def _draw_panel(draw, shown, left, height):
    draw.rectangle((left, 0, left + PANEL, height), fill="#2b2b2b")
    font = _font(13)
    draw.text((left + 10, 10), f"Turn {shown['turn']}", fill="white", font=font)
    draw.text(
        (left + 10, 32),
        f"{shown['acting']}'s turn",
        fill=_colour(shown["acting"]),
        font=font,
    )
    draw.text((left + 10, 54), shown["bubble"][:30], fill="white", font=_font(12))
    draw.text((left + 10, 84), "Log it saw:", fill="#bbbbbb", font=_font(12))
    lines = shown["log"][-LOG_LINES:] or ["(nothing)"]
    for row, line in enumerate(lines):
        draw.text(
            (left + 10, 102 + row * LINE), line[:30], fill="white", font=_font(12)
        )


def frame(records, turn, size):
    """The image for one turn: grid, pirates, bubble and the side panel."""
    shown = scene(records, turn, size)
    grid = max(size, 1) * TILE
    height = max(grid, 102 + LOG_LINES * LINE + 10)
    image = Image.new("RGB", (grid + PANEL, height), "#2b2b2b")
    draw = ImageDraw.Draw(image)
    _draw_grid(image, draw, size, shown["treasure"])
    _draw_pirates(draw, shown["positions"])
    _draw_bubble(draw, shown["positions"][shown["acting"]], shown["bubble"], size)
    _draw_panel(draw, shown, grid, height)
    return image


def _png(image):
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def frame_png(folder, turn):
    """The PNG the page serves for one turn, read fresh from the run folder."""
    records = records_in(folder)
    return _png(frame(records, turn, grid_size(folder, records)))


def gif(folder):
    """The whole run as GIF bytes, one frame per turn, from the same frames."""
    records = records_in(folder)
    size = grid_size(folder, records)
    frames = [
        Image.open(io.BytesIO(_png(frame(records, turn, size))))
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
