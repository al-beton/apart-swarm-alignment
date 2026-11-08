# Implements: event-log/crew-positions, viewer/one-renderer, viewer/frame-shows-the-swarm, viewer/watch-live, viewer/render-gif, viewer/art-folder, viewer/sprite-from-definition, viewer/sprite-follows-action, treasure-island/pokemon-style
"""Watching a run in the browser and rendering it to a GIF from one renderer."""

import io
import json
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageStat

from assets.pirates import pirate
from treasure_island import cli, viewer
from treasure_island.config import parse_config
from treasure_island.game_state import starting_squares
from treasure_island.looks import sprite_values


def record(turn, agent, start, end, **rest):
    """One event-log record; `did`, `log` and `found` can be given in `rest`."""
    return {
        "turn": turn,
        "agent": agent,
        "saw": {"position": start, "prompt": f"Turn {turn}."},
        "did": rest.get("did", []),
        "log_shown": rest.get("log", []),
        **({"crew": rest["crew"]} if "crew" in rest else {}),
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
    (run / "config.json").write_text(json.dumps({"grid_size": 3, "seed": 1}) + "\n")
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

    def counted(records, turn, *rest, **named):
        drawn.append(turn)
        return draw(records, turn, *rest, **named)

    monkeypatch.setattr(viewer, "frame", counted)
    frames = list(png_frames(viewer.gif(folder)))
    steps = [(t, s) for t in range(len(RECORDS)) for s in viewer.turn_steps(RECORDS, t)]
    assert drawn == [turn for turn, _ in steps]
    served = [
        Image.open(io.BytesIO(viewer.frame_png(folder, turn, step))).convert("RGB")
        for turn, step in steps
    ]
    assert drawn == 2 * [turn for turn, _ in steps]
    for frame, page in zip(frames, served, strict=True):
        assert frame.size == page.size
        # A GIF frame holds at most 256 colours, so compare within that loss.
        diff = ImageChops.difference(frame, page)
        assert ImageStat.Stat(diff.convert("L")).mean[0] < 2


def test_frame_shows_the_swarm_every_pirate_whose_turn_and_what_it_wrote():
    scene = viewer.scene(RECORDS, 1, size=3)
    assert scene["size"] == 3
    assert scene["positions"] == {"pirate-a": [1, 0], "pirate-b": [2, 2]}
    assert scene["acting"] == "pirate-b"
    assert scene["note"] == "nothing here"
    assert scene["treasure"] is None
    assert viewer.scene(RECORDS, 2, size=3)["treasure"] == [1, 0]


def test_crew_positions_a_frame_shows_a_pirate_before_its_first_turn():
    first = {**RECORDS[0], "crew": {"pirate-a": [0, 0], "pirate-b": [2, 2]}}
    scene = viewer.scene([first], 0, size=3)
    assert scene["positions"] == {"pirate-a": [1, 0], "pirate-b": [2, 2]}
    assert scene["note"] is None


def crew_of(count, size):
    """A crew standing where a real game starts it, each on its own square."""
    agents = [f"pirate-{number + 1}" for number in range(count)]
    squares = dict(zip(agents, starting_squares(size), strict=False))
    return (
        agents,
        squares,
        [
            record(turn, agent, [*squares[agent]], [*squares[agent]], crew=squares)
            for turn, agent in enumerate(agents)
        ],
    )


def assert_every_label_shows(image, looks_and_spots):
    for values, spot in looks_and_spots:
        with_label = pirate(*values, "down", 0)
        bare = pirate(values[0], values[1], "", "down", 0)
        label = [
            (x, y)
            for x in range(viewer.TILE)
            for y in range(viewer.TILE)
            if with_label.getpixel((x, y)) != bare.getpixel((x, y))
        ]
        assert label
        for x, y in label:
            shown = image.getpixel((viewer.EDGE_LEFT + spot[0] + x, spot[1] + y))
            assert shown == with_label.getpixel((x, y))[:3], (values[2], x, y)


@pytest.mark.parametrize("count", [2, 6, 20])
@pytest.mark.parametrize("acting", [0, -1])
def test_frame_shows_the_swarm_every_pirate_on_its_own_square(count, acting):
    """Each pirate is drawn on its square, and nothing covers anyone's label."""
    _, squares, crew = crew_of(count, size=8)
    turn = list(range(count))[acting]
    image = viewer.frame(crew, turn, 8).convert("RGB")
    looks = [sprite_values(p) for p in parse_config({"crew_size": count}).pirates]
    spots = [(x * viewer.TILE, y * viewer.TILE) for x, y in squares.values()]
    assert_every_label_shows(image, zip(looks, spots, strict=True))


def tile_at(image, x, y):
    box = (viewer.EDGE_LEFT + x * viewer.TILE, y * viewer.TILE)  # in its frame
    return image.crop((*box, box[0] + viewer.TILE, box[1] + viewer.TILE)).convert("RGB")


def art(name):
    return Image.open(viewer.ASSETS / f"{name}.png").convert("RGBA")


def sand_tiles():
    return [art(f"tiles/{n}").convert("RGB").tobytes() for n in viewer.SAND_TILES]


def on_ground(image, x, y, sprite):
    """Whether the acting pirate's square is exactly this sprite on some sand tile.

    Its square is outlined in yellow under it (viewer/turn-marked).
    """
    shown = tile_at(image, x, y).tobytes()
    for name in viewer.SAND_TILES:
        ground = art(f"tiles/{name}").copy()
        viewer.outline(ground, (0, 0))
        ground.alpha_composite(sprite)
        if ground.convert("RGB").tobytes() == shown:
            return True
    return False


def alone(turn=0, did=(), found=False):
    return record(
        turn,
        "pirate-1",
        [1, 1],
        [1, 1],
        crew={"pirate-1": [1, 1]},
        did=list(did),
        found=found,
    )


def look(**settings):
    return parse_config({"pirates": [settings]}).pirates[0]


def test_art_folder_every_empty_square_is_a_sand_tile_from_the_assets():
    image = viewer.frame([alone()], 0, 5)
    # Squares away from the west and south edges, which carry the squares' names.
    for x, y in [(4, 0), (2, 1), (3, 2), (3, 3)]:
        assert tile_at(image, x, y).tobytes() in sand_tiles()


def test_art_folder_a_pirate_is_exactly_its_sprite_and_never_a_shape():
    image = viewer.frame([alone()], 0, 3)
    only = parse_config({"crew_size": 1}).pirates[0]
    assert on_ground(image, 1, 1, pirate(*sprite_values(only), "down", 0))


def test_art_folder_a_dug_square_and_a_found_treasure_use_their_art():
    dig = alone(0, [{"action": "dig"}])
    moved = record(
        1,
        "pirate-1",
        [1, 1],
        [2, 1],
        crew={"pirate-1": [1, 1]},
        did=[{"action": "move", "direction": "east"}],
    )
    image = viewer.frame([dig, moved], 1, 3)
    assert tile_at(image, 1, 1).tobytes() == art("tiles/dug").convert("RGB").tobytes()
    found = alone(0, [{"action": "dig"}], found=True)
    gone = {**moved, "turn": 1}
    image = viewer.frame([found, gone], 1, 3)
    ground = art("tiles/dug").copy()
    ground.alpha_composite(art("treasure/cave-2"))  # turn 1 glints
    assert tile_at(image, 1, 1).tobytes() == ground.convert("RGB").tobytes()


def test_art_folder_missing_art_is_an_error_not_a_different_picture(
    folder, monkeypatch
):
    monkeypatch.setattr(viewer, "ASSETS", Path("/nowhere"))
    with pytest.raises(FileNotFoundError):
        viewer.frame_png(folder, 0)


def test_art_folder_the_art_loads_from_outside_the_repository(tmp_path):
    subprocess.run(
        [sys.executable, "-c", "import assets.pirates, treasure_island.viewer"],
        cwd=tmp_path,
        check=True,
    )


def test_sprite_from_definition_uses_the_configured_look(folder):
    wanted = {"personality": 7, "head_text": "Anne", "colour": [10, 200, 30]}
    saved = json.loads((folder / "config.json").read_text())
    saved["pirates"] = [wanted, {"personality": 2}]
    (folder / "config.json").write_text(json.dumps(saved))
    first, second = parse_config({"pirates": saved["pirates"]}).pirates
    pirates = viewer.pirates_in(folder, viewer.records_in(folder))
    assert pirates == {
        "pirate-a": sprite_values(first),
        "pirate-b": sprite_values(second),
    }
    assert pirates["pirate-a"] == (7, "#0ac81e", "AN")


def test_sprite_from_definition_a_run_that_does_not_say_gets_the_default_crew(folder):
    default = parse_config({"crew_size": 2}).pirates
    assert viewer.pirates_in(folder, viewer.records_in(folder)) == {
        "pirate-a": sprite_values(default[0]),
        "pirate-b": sprite_values(default[1]),
    }


def test_sprite_from_definition_the_frame_draws_the_given_look():
    chosen = (7, "#0ac81e", "AN")
    image = viewer.frame([alone()], 0, 3, {"pirate-1": chosen})
    assert on_ground(image, 1, 1, pirate(*chosen, "down", 0))


@pytest.mark.parametrize(
    "direction,pose",
    [("north", "up"), ("south", "down"), ("east", "right"), ("west", "left")],
)
def test_sprite_follows_action_a_pirate_faces_the_way_it_moves(direction, pose):
    moving = alone(0, [{"action": "move", "direction": direction}])
    assert viewer.scene([moving], 0, 3)["poses"]["pirate-1"] == (pose, 1)


def test_sprite_follows_action_it_keeps_facing_that_way_and_stands_still():
    moved = alone(0, [{"action": "move", "direction": "west"}])
    passed = alone(1, [])  # a turn that passed, with no action
    assert viewer.scene([moved, passed], 1, 3)["poses"]["pirate-1"] == ("left", 0)


def test_sprite_follows_action_walking_alternates_its_feet():
    moves = [alone(t, [{"action": "move", "direction": "east"}]) for t in range(2)]
    feet = [viewer.scene(moves, t, 3)["poses"]["pirate-1"][1] for t in range(2)]
    assert feet == [1, 2]


def test_sprite_follows_action_each_pirate_alternates_its_own_feet():
    east = [{"action": "move", "direction": "east"}]
    crew = {"pirate-1": [0, 0], "pirate-2": [0, 0]}
    turns = [
        record(t, f"pirate-{t % 2 + 1}", [0, 0], [0, 0], crew=crew, did=east)
        for t in range(6)
    ]
    feet = [viewer.scene(turns, t, 3)["poses"]["pirate-1"][1] for t in (0, 2, 4)]
    assert feet == [1, 2, 1]


def test_sprite_follows_action_digging_and_finding_the_treasure():
    dig = alone(0, [{"action": "dig"}])
    assert viewer.scene([dig], 0, 3)["poses"]["pirate-1"][0] == "dig"
    found = alone(0, [{"action": "dig"}], found=True)
    assert viewer.scene([found], 0, 3)["poses"]["pirate-1"][0] == "cheer"
    only = parse_config({"crew_size": 1}).pirates[0]
    image = viewer.frame([dig], 0, 3)
    assert on_ground_dug(image, 1, 1, pirate(*sprite_values(only), "dig", 0))


def on_ground_dug(image, x, y, sprite):
    ground = art("tiles/dug").copy()
    viewer.outline(ground, (0, 0))  # the acting pirate's square
    ground.alpha_composite(sprite)
    return tile_at(image, x, y).tobytes() == ground.convert("RGB").tobytes()


def test_sprite_follows_action_others_stay_as_they_were():
    agents, _, together = crew_of(2, size=3)
    moved = {**together[0], "did": [{"action": "move", "direction": "east"}]}
    poses = viewer.scene([moved, together[1]], 1, 3)["poses"]
    assert poses[agents[0]] == ("right", 0)
    assert poses[agents[1]] == ("down", 0)


def test_one_renderer_rendering_twice_gives_an_identical_gif(folder):
    assert viewer.gif(folder) == viewer.gif(folder)


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
    # A move's walking frames are served too, and the page knows how many there are.
    assert json.loads(get(server, "/steps/0")[1]) == {"steps": 4}
    assert get(server, "/frame/0.png?step=2")[1] == viewer.frame_png(folder, 0, 2)
    assert b"/steps/" in page


def test_watch_live_a_run_with_no_turn_yet_has_none_to_show(tmp_path):
    # The page asks before the first model call has answered and the log exists.
    httpd = viewer.server(tmp_path, port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        assert json.loads(get(httpd, "/turns")[1]) == {"turns": 0}
    finally:
        httpd.shutdown()


def _script(page):
    return page.split("<script>")[1].split("</script>")[0]


def test_watch_live_each_walking_frame_shows_before_the_next_is_asked_for():
    script = _script(viewer.PAGE)
    draw = script[script.index("function draw") : script.index("async function show")]
    # A frame is loaded and decoded off-screen, and shown only if still wanted.
    assert draw.index("decode()") < draw.index("frame.src =")
    assert "mine === walk" in draw
    show = script[
        script.index("async function show") : script.index("async function poll")
    ]
    # Each step's hold starts only once its frame is on the page.
    assert show.index("await draw(turn, step, mine)") < show.index("setTimeout")


def test_watch_live_stepping_away_mid_walk_stops_it():
    script = _script(viewer.PAGE)
    show = script[
        script.index("async function show") : script.index("async function poll")
    ]
    assert "step < steps && mine === walk" in show
    assert "mine = ++walk" in show


def test_watch_live_the_command_names_its_address(folder, capsys, monkeypatch):
    started = {}

    def fake_serve_forever(self):
        started["port"] = self.server_address[1]

    monkeypatch.setattr(viewer.ThreadingHTTPServer, "serve_forever", fake_serve_forever)
    assert cli.main(["watch", str(folder), "--port", "0"]) == 0
    assert f"http://127.0.0.1:{started['port']}/" in capsys.readouterr().out


def test_render_gif_writes_one_frame_per_turn_and_each_walk_next_to_the_run(
    folder, capsys
):
    assert cli.main(["render", str(folder)]) == 0
    out = folder.with_suffix(".gif")
    assert out.exists()
    assert str(out) in capsys.readouterr().out
    # One frame per turn, and the in-between steps of each move and dig.
    steps = [len(viewer.turn_steps(RECORDS, turn)) for turn in range(len(RECORDS))]
    assert sum(steps) > len(RECORDS)
    assert len(list(png_frames(out.read_bytes()))) == sum(steps)


def test_render_gif_writes_where_asked(folder, tmp_path):
    out = tmp_path / "elsewhere" / "game.gif"
    assert cli.main(["render", str(folder), "--out", str(out)]) == 0
    assert out.read_bytes()[:6] in (b"GIF87a", b"GIF89a")
