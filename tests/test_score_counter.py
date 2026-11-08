# Implements: viewer/score-counter
"""The crew's score on every frame, counting up as it's earned."""

import io
import json
import shutil
from pathlib import Path

import pytest
from PIL import Image, ImageChops

from assets.cave import ENTER_STEPS
from assets.dig import DIG_STEPS
from treasure_island import examples, viewer
from treasure_island.viewer import FRAME_MS, WALK_MS, Scoring

ROOT = Path(__file__).resolve().parents[1]
NAMES = sorted(examples.EXAMPLES)


def turn(number, agent, did, *, in_cave=False, at=(1, 1)):
    outcome = {"position": list(at), "found_treasure": False}  # as the game records it
    if in_cave:
        outcome["in_cave"] = True
    return {
        "turn": number,
        "agent": agent,
        "saw": {"position": list(at), "prompt": ""},
        "did": [{"action": did}],
        "log_shown": [],
        "outcome": outcome,
    }


def counts(records, scoring):
    return [
        viewer.scene(records, n, 3, scoring=scoring)["score"]
        for n in range(len(records))
    ]


# Two pirates with 3 turns each. pirate-1 goes in on its first turn with 2 left,
# and pirate-2 digs on. The turn order passes pirate-1 on each of pirate-2's later turns.
EARLY = [
    turn(0, "pirate-1", "enter", in_cave=True, at=(1, 1)),
    turn(1, "pirate-2", "dig", at=(0, 1)),
    turn(2, "pirate-2", "dig", at=(0, 1)),
    turn(3, "pirate-2", "dig", at=(0, 1)),
]
THREE_TURNS = Scoring(turns_per_pirate=3, in_cave=100, per_turn_left=10)


# One pirate with 4 turns digs once, then goes in with 2 turns left: game over.
ALONE = [
    turn(0, "pirate-1", "dig"),
    {
        **turn(1, "pirate-1", "enter", in_cave=True),
        "game_over": {"score": 120, "treasure": [2, 2]},
    },
]


def records_of(name):
    lines = (ROOT / "examples" / name / "events.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines]


def test_score_counter_starts_at_0():
    for name in NAMES:
        folder = ROOT / "examples" / name
        shown = viewer.scene(records_of(name), 0, 5, scoring=viewer.scoring_in(folder))
        assert shown["score"] == 0


def test_score_counter_going_in_adds_100_and_a_rising_plus_100():
    shown = viewer.scene(EARLY, 0, 3, scoring=THREE_TURNS)
    assert shown["score"] == 100
    assert shown["gains"] == ["+100"]


def test_score_counter_each_pass_of_a_pirate_inside_adds_10_while_it_had_turns_left():
    assert counts(EARLY, THREE_TURNS) == [100, 100, 110, 120]
    gains = [viewer.scene(EARLY, n, 3, scoring=THREE_TURNS)["gains"] for n in range(4)]
    assert gains == [["+100"], [], ["+10"], ["+10"]]
    # It had 2 turns left, so a game that went on would add nothing more for it.
    longer = [*EARLY, turn(4, "pirate-2", "dig", at=(0, 1))]
    assert counts(longer, Scoring(4, 100, 10))[-1] == 130  # 3 turns left with 4 each


def test_score_counter_going_in_early_counts_up_to_more():
    late = [
        turn(0, "pirate-1", "dig"),
        turn(1, "pirate-2", "dig", at=(0, 1)),
        turn(2, "pirate-1", "enter", in_cave=True),
        turn(3, "pirate-2", "dig", at=(0, 1)),
        turn(4, "pirate-2", "dig", at=(0, 1)),
    ]
    assert counts(late, THREE_TURNS)[-1] < counts(EARLY, THREE_TURNS)[-1]


def test_score_counter_owed_turns_play_out_quickly_before_the_last_frame():
    alone = ALONE
    scoring = Scoring(4, 100, 10)
    steps = viewer.turn_steps(alone, 1, scoring)
    # Going in takes its own steps, its last playing out the first owed round.
    assert steps == [*range(1, ENTER_STEPS + 2), None]
    shown = [viewer.scene(alone, 1, 3, step=s, scoring=scoring) for s in steps]
    assert [s["score"] for s in shown] == [100] * (ENTER_STEPS - 1) + [110, 120, 120]
    gains = [s["gains"] for s in shown]
    assert gains == [["+100"]] * (ENTER_STEPS - 1) + [["+10"], ["+10"], ["+100"]]
    # Only the last turn plays them out.
    assert viewer.turn_steps(alone, 0, scoring) == list(range(1, DIG_STEPS + 1))


@pytest.mark.parametrize("name", NAMES)
def test_score_counter_the_last_frame_s_count_is_the_game_s_score(name):
    folder = ROOT / "examples" / name
    records = records_of(name)
    scoring = viewer.scoring_in(folder)
    last = len(records) - 1
    final = viewer.turn_steps(records, last, scoring)[-1]
    shown = viewer.scene(records, last, 5, step=final, scoring=scoring)
    assert shown["score"] == records[-1]["game_over"]["score"]
    # The committed GIF ends on that frame, after any owed turns played out quickly.
    gif = Image.open(folder / "game.gif")
    durations = []
    for index in range(gif.n_frames):
        gif.seek(index)
        durations.append(gif.info["duration"])
    owed = len(viewer.turn_steps(records, last, scoring)) - 1
    # A GIF merges a frame identical to the one before it, adding up their
    # times, so the last turn is read back by its total: quick steps, then a hold.
    want, tail = owed * WALK_MS + FRAME_MS, []
    while sum(tail) < want:
        tail.append(durations[len(durations) - 1 - len(tail)])
    assert sum(tail) == want
    assert tail[0] >= FRAME_MS
    assert set(tail[1:]) <= {WALK_MS}


def test_score_counter_is_drawn_at_the_top_of_the_frame():
    scoring = Scoring(4, 100, 10)
    last = ENTER_STEPS + 1  # the hat is on the stack by then, so only the score moves
    before = viewer.frame(ALONE, 1, 3, step=last - 1, scoring=scoring)  # 110
    after = viewer.frame(ALONE, 1, 3, step=last, scoring=scoring)  # 120, the same turn
    # Only the score differs; compare the panel's top line.
    grid = viewer.EDGE_LEFT + 3 * viewer.TILE
    top = (grid, 0, before.width, 30)
    changed = ImageChops.difference(before.crop(top), after.crop(top)).getbbox()
    assert changed and changed[0] > viewer.PANEL // 2  # right of "Turn N", not over it


def test_score_counter_the_live_page_asks_for_every_step_the_gif_draws(tmp_path):
    folder = tmp_path / "silent"
    shutil.copytree(ROOT / "examples/silent", folder)
    records = viewer.records_in(folder)
    last = len(records) - 1
    steps = viewer.turn_steps(records, last, viewer.scoring_in(folder))
    assert len(steps) > 1, "silent ends with everyone inside and turns owed"
    httpd = viewer.server(folder, 0)
    handler = httpd.RequestHandlerClass
    served = []

    class Reply(handler):  # the page's request, answered without a socket
        def __init__(self, path):  # noqa: PLW0231 (nothing to set up but the path)
            self.path = path
            self.body = None

        def _reply(self, kind, body):
            self.body = body

    for index in range(1, len(steps)):
        reply = Reply(f"/frame/{last}.png?step={index}&t=0")
        reply.do_GET()
        served.append(reply.body)
    reply = Reply(f"/frame/{last}.png?t=0")
    reply.do_GET()
    served.append(reply.body)
    httpd.server_close()
    expected = [viewer.frame_png(folder, last, step) for step in steps]
    assert served == expected
    assert (
        Image.open(io.BytesIO(served[-1])).size
        == Image.open(io.BytesIO(served[0])).size
    )


def test_score_counter_counts_by_the_event_log_s_numbers_then_config_json(tmp_path):
    records = [dict(record) for record in records_of("silent")]
    over = records[-1]["game_over"]
    assert viewer.scoring_in(ROOT / "examples/silent") == Scoring(
        *over["score_numbers"].values()
    )
    # A log from before the numbers were recorded counts by config.json instead.
    records[-1] = {**records[-1], "game_over": {**over}}
    del records[-1]["game_over"]["score_numbers"]
    (tmp_path / "events.jsonl").write_text(
        "".join(json.dumps(record) + "\n" for record in records)
    )
    (tmp_path / "config.json").write_text(json.dumps({"score_in_cave": 70}))
    assert viewer.scoring_in(tmp_path) == Scoring(30, 70, 10)
