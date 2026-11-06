# Implements: event-log/crew-positions, viewer/one-renderer, viewer/frame-shows-the-swarm, viewer/watch-live, viewer/render-gif, viewer/art-folder
"""Watching a run in the browser and rendering it to a GIF from one renderer."""

import io
import json
import threading
import urllib.request
from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageStat

from treasure_island import cli, viewer


def record(turn, agent, start, end, **rest):
    """One event-log record; `did`, `log` and `found` can be given in `rest`."""
    return {
        "turn": turn,
        "agent": agent,
        "saw": {"position": start, "prompt": f"Turn {turn}."},
        "did": rest.get("did", []),
        "log_shown": rest.get("log", []),
        "outcome": {"position": end, "found_treasure": rest.get("found", False)},
    }


RECORDS = [
    record(
        0, "pirate-a", [0, 0], [1, 0], did=[{"action": "move", "direction": "east"}]
    ),
    record(
        1,
        "pirate-b",
        [2, 2],
        [2, 2],
        did=[{"action": "write", "text": "nothing here"}],
        log=[{"line": 0, "text": "pirate-a: east"}],
    ),
    record(2, "pirate-a", [1, 0], [1, 0], did=[{"action": "dig"}], found=True),
]


@pytest.fixture
def folder(tmp_path):
    run = tmp_path / "runs" / "small-seed-1"
    run.mkdir(parents=True)
    (run / "config.json").write_text(json.dumps({"size": 3, "seed": 1}) + "\n")
    (run / "events.jsonl").write_text("".join(json.dumps(r) + "\n" for r in RECORDS))
    return run


def png_frames(gif_bytes):
    image = Image.open(io.BytesIO(gif_bytes))
    for index in range(image.n_frames):
        image.seek(index)
        yield image.convert("RGB")


def test_one_renderer_the_gif_holds_exactly_the_frames_the_page_serves(
    folder, monkeypatch
):
    drawn = []
    draw = viewer.frame

    def counted(records, turn, size):
        drawn.append(turn)
        return draw(records, turn, size)

    monkeypatch.setattr(viewer, "frame", counted)
    frames = list(png_frames(viewer.gif(folder)))
    assert drawn == list(range(len(RECORDS)))
    served = [
        Image.open(io.BytesIO(viewer.frame_png(folder, turn))).convert("RGB")
        for turn in range(len(RECORDS))
    ]
    assert drawn == 2 * list(range(len(RECORDS)))
    for frame, page in zip(frames, served, strict=True):
        assert frame.size == page.size
        # A GIF frame holds at most 256 colours, so compare within that loss.
        diff = ImageChops.difference(frame, page)
        assert ImageStat.Stat(diff.convert("L")).mean[0] < 2


def test_frame_shows_the_swarm_every_pirate_whose_turn_the_bubble_and_the_log():
    scene = viewer.scene(RECORDS, 1, size=3)
    assert scene["size"] == 3
    assert scene["positions"] == {"pirate-a": [1, 0], "pirate-b": [2, 2]}
    assert scene["acting"] == "pirate-b"
    assert scene["bubble"] == "nothing here"
    assert scene["log"] == ["pirate-a: east"]
    assert scene["treasure"] is None
    assert viewer.scene(RECORDS, 2, size=3)["treasure"] == [1, 0]


def test_crew_positions_a_frame_shows_a_pirate_before_its_first_turn():
    first = {**RECORDS[0], "crew": {"pirate-a": [0, 0], "pirate-b": [2, 2]}}
    scene = viewer.scene([first], 0, size=3)
    assert scene["positions"] == {"pirate-a": [1, 0], "pirate-b": [2, 2]}
    assert scene["bubble"] == "move east"


def test_frame_shows_the_swarm_pirates_on_one_square_are_all_visible():
    together = [
        record(0, "pirate-a", [1, 1], [1, 1]),
        record(1, "pirate-b", [1, 1], [1, 1]),
    ]
    image = viewer.frame(together, 1, 3).convert("RGB")
    colours = {image.getpixel((x, y)) for x in range(144) for y in range(144)}
    assert viewer.rgb(viewer.COLOURS[0]) in colours
    assert viewer.rgb(viewer.COLOURS[1]) in colours


def test_frame_shows_the_swarm_as_an_image_with_grid_panel_and_log(folder):
    image = Image.open(io.BytesIO(viewer.frame_png(folder, 0)))
    assert image.width > 3 * viewer.TILE
    assert image.height > 3 * viewer.TILE


@pytest.fixture
def server(folder):
    httpd = viewer.server(folder, port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd
    httpd.shutdown()


def get(httpd, path):
    url = f"http://127.0.0.1:{httpd.server_address[1]}{path}"
    with urllib.request.urlopen(url) as reply:
        return reply.headers.get_content_type(), reply.read()


def test_watch_live_the_page_follows_the_log_as_it_is_written(folder, server):
    kind, page = get(server, "/")
    assert kind == "text/html"
    assert b"<html" in page.lower()
    assert json.loads(get(server, "/turns")[1]) == {"turns": 3}
    with (folder / "events.jsonl").open("a") as events:
        events.write(json.dumps(record(3, "pirate-b", [2, 2], [2, 1])) + "\n")
    assert json.loads(get(server, "/turns")[1]) == {"turns": 4}
    kind, png = get(server, "/frame/3.png")
    assert kind == "image/png"
    assert png == viewer.frame_png(folder, 3)


def test_watch_live_the_command_names_its_address(folder, capsys, monkeypatch):
    started = {}

    def fake_serve_forever(self):
        started["port"] = self.server_address[1]

    monkeypatch.setattr(viewer.ThreadingHTTPServer, "serve_forever", fake_serve_forever)
    assert cli.main(["watch", str(folder), "--port", "0"]) == 0
    assert f"http://127.0.0.1:{started['port']}/" in capsys.readouterr().out


def test_render_gif_writes_one_frame_per_turn_next_to_the_run(folder, capsys):
    assert cli.main(["render", str(folder)]) == 0
    out = folder.with_suffix(".gif")
    assert out.exists()
    assert str(out) in capsys.readouterr().out
    assert len(list(png_frames(out.read_bytes()))) == len(RECORDS)


def test_render_gif_writes_where_asked(folder, tmp_path):
    out = tmp_path / "elsewhere" / "game.gif"
    assert cli.main(["render", str(folder), "--out", str(out)]) == 0
    assert out.read_bytes()[:6] in (b"GIF87a", b"GIF89a")


def test_art_folder_the_viewer_draws_without_art(folder, monkeypatch):
    monkeypatch.setattr(viewer, "ASSETS", Path("/nowhere"))
    assert viewer.frame_png(folder, 0)[:8] == b"\x89PNG\r\n\x1a\n"


def test_art_folder_art_is_drawn_when_it_exists(folder, tmp_path, monkeypatch):
    plain = viewer.frame_png(folder, 0)
    art = tmp_path / "assets"
    (art / "tiles").mkdir(parents=True)
    Image.new("RGB", (8, 8), "magenta").save(art / "tiles" / "sand.png")
    monkeypatch.setattr(viewer, "ASSETS", art)
    assert viewer.frame_png(folder, 0) != plain
