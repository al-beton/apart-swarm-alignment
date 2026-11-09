# Implements: runs/one-game, runs/run-command, runs/run-folder, runs/replies-keyed, runs/manifest-varies, runs/no-silent-model-calls, runs/plays-live, runs/paced-from-cache, runs/cache-across-runs, runs/same-answer-wins, runs/no-cache
"""Running a game into a folder, and the replies a model brain will reuse."""

import json
import os
import sys
import urllib.request
import webbrowser

import pytest

from treasure_island import cli, runs
from treasure_island.event_log import log_errors
from treasure_island.runs import MissingReply, Replies, earlier_replies, request_key

CONFIG = """
grid_size = 3
crew_size = 2
turns_per_pirate = 6
brain = "stripes"
"""
TURNS = 12
REQUEST = {
    "agent": "pirate-1",
    "model": "some/model",
    "prompt": "You are at (0, 0).",
    "temperature": 0.0,
    "seed": 1,
}


@pytest.fixture
def config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "small.toml"
    path.write_text(CONFIG)
    return path


def played(config, capsys, *flags, seed=1):
    """Run the config through the command; return the folder it printed."""
    command = ["run", str(config), "--seed", str(seed), "--no-watch", *flags]
    assert cli.main(command) == 0
    return config.parent / capsys.readouterr().out.strip()


def contents(folder):
    return {path.name: path.read_bytes() for path in folder.iterdir()}


def test_one_game_a_config_with_no_brain_is_refused(config, capsys):
    config.write_text("grid_size = 3\ncrew_size = 2\n")
    assert cli.main(["run", str(config), "--seed", "1", "--no-watch"]) == 1
    assert "brain" in capsys.readouterr().err
    assert not (config.parent / "runs").exists()


def test_one_game_a_brain_nobody_knows_is_refused_too(config, capsys):
    config.write_text('brain = "no-such-brain"\n')
    assert cli.main(["run", str(config), "--seed", "1", "--no-watch"]) == 1
    assert "no-such-brain" in capsys.readouterr().err
    assert not (config.parent / "runs").exists()


def test_run_command_makes_a_new_folder_each_time(config, capsys):
    first = played(config, capsys)
    before = contents(first)
    second = played(config, capsys)
    assert first != second
    assert first.parent.name == second.parent.name == "runs"
    assert contents(first) == before


def test_run_folder_holds_both_logs_the_story_replies_config_and_manifest(
    config, capsys
):
    folder = played(config, capsys, seed=4)
    assert {path.name for path in folder.iterdir()} == {
        "events.jsonl",
        "story.txt",
        "pirates-log.txt",
        "replies.jsonl",
        "config.json",
        "manifest.json",
    }
    saved = json.loads((folder / "config.json").read_text())
    assert saved["seed"] == 4 and saved["grid_size"] == 3


def test_run_folder_events_pass_the_validator(config, capsys):
    assert log_errors(played(config, capsys) / "events.jsonl") == []


@pytest.mark.parametrize(
    "part,other",
    [
        ("agent", "pirate-2"),
        ("model", "some/other-model"),
        ("prompt", "You are at (1, 0)."),
        ("temperature", 0.5),
        ("seed", 2),
    ],
)
def test_replies_keyed_each_part_of_the_request_changes_the_key(part, other):
    assert request_key(REQUEST) != request_key({**REQUEST, part: other})


def test_replies_keyed_a_repeated_request_reuses_its_reply(tmp_path):
    calls = []

    def backend(request):
        calls.append(request)
        return f"reply {len(calls)}", 0.5

    replies = Replies(tmp_path / "replies.jsonl", backend)
    assert replies.ask(REQUEST) == replies.ask(REQUEST) == "reply 1"
    assert replies.ask({**REQUEST, "seed": 2}) == "reply 2"
    assert (replies.hits, replies.misses, replies.cost_usd) == (1, 2, 1.0)


@pytest.mark.parametrize("separator", [" ", "\u0085", "\x0c"])
def test_replies_keyed_a_stored_reply_survives_any_line_separator(tmp_path, separator):
    text = f"dig{separator}now"
    path = tmp_path / "replies.jsonl"
    assert Replies(path, lambda request: (text, 0.0)).ask(REQUEST) == text
    assert Replies(path).ask(REQUEST) == text


def test_manifest_varies_holds_times_cost_and_cache_hits(config, capsys):
    manifest = json.loads((played(config, capsys) / "manifest.json").read_text())
    assert set(manifest) == {
        "started_at",
        "finished_at",
        "cost_usd",
        "cache_hits",
        "cache_misses",
        "prompt",
        "commit",
        "dirty",
    }
    assert manifest["cost_usd"] == 0


def test_manifest_varies_two_identical_runs_differ_nowhere_else(config, capsys):
    first = contents(played(config, capsys))
    second = contents(played(config, capsys))
    first.pop("manifest.json")
    second.pop("manifest.json")
    assert first == second


def test_no_silent_model_calls_a_missing_reply_fails_with_no_backend(tmp_path):
    with pytest.raises(MissingReply):
        Replies(tmp_path / "replies.jsonl").ask(REQUEST)


class FakeModel:
    """Stands in for a paid model: every call is new, costs money and is counted."""

    def __init__(self):
        self.calls = 0

    def __call__(self, request):
        self.calls += 1
        return f"call {self.calls}", 0.01


def answered(name, model, started_at="2026-01-01T00:00:00+00:00"):
    """A finished run folder under runs/ whose model answered REQUEST."""
    folder = runs.RUNS / name
    folder.mkdir(parents=True)
    Replies(folder / "replies.jsonl", model).ask(REQUEST)
    (folder / "manifest.json").write_text(json.dumps({"started_at": started_at}))
    return folder


def reused(folder, earlier, model=None):
    """What a run in `folder` gets for REQUEST, given those earlier replies."""
    return Replies(folder / "replies.jsonl", model, earlier).ask(REQUEST)


@pytest.fixture
def in_runs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "next").mkdir()
    return tmp_path / "next"


def test_cache_across_runs_a_repeat_asks_the_model_nothing(in_runs):
    model = FakeModel()
    answered("first", model)
    replies = Replies(in_runs / "replies.jsonl", model, earlier_replies())
    assert replies.ask(REQUEST) == "call 1"
    assert model.calls == 1
    assert (replies.hits, replies.misses, replies.cost_usd) == (1, 0, 0.0)


def test_cache_across_runs_its_folder_alone_regenerates_the_game(in_runs):
    answered("first", FakeModel())
    assert reused(in_runs, earlier_replies(), FakeModel()) == "call 1"
    assert reused(in_runs, {}) == "call 1"


def test_cache_across_runs_only_the_same_request_reuses_a_reply(in_runs):
    model = FakeModel()
    answered("first", model)
    other = Replies(in_runs / "replies.jsonl", model, earlier_replies())
    assert other.ask({**REQUEST, "seed": 2}) == "call 2"


def test_cache_across_runs_replay_never_borrows_from_another_run(in_runs):
    answered("first", FakeModel())
    with pytest.raises(MissingReply):
        reused(in_runs, {})


def test_no_cache_asks_again_into_a_new_folder(config, capsys):
    first = played(config, capsys)
    before = contents(first)
    fresh = played(config, capsys, "--no-cache")
    assert fresh != first
    assert contents(first) == before
    # Scripted brains ask nothing, so the same game comes out.
    assert (fresh / "events.jsonl").read_bytes() == before["events.jsonl"]


def test_no_cache_means_no_earlier_replies_so_the_model_is_asked_again(in_runs):
    model = FakeModel()
    answered("first", model)
    assert reused(in_runs, {}, model) == "call 2"


def test_no_cache_a_later_repeat_reuses_the_newest_replies(in_runs):
    model = FakeModel()
    answered("first", model, "2026-01-01T00:00:00+00:00")
    answered("fresh", model, "2026-01-02T00:00:00+00:00")
    assert reused(in_runs, earlier_replies()) == "call 2"


def two_answers():
    """Two runs that answered the same request differently, oldest first."""
    model = FakeModel()
    return (
        answered("b-older", model, "2026-01-01T00:00:00+00:00"),
        answered("a-newer", model, "2026-01-02T00:00:00+00:00"),
    )


def test_same_answer_wins_whatever_the_file_times_say(in_runs):
    older, newer = two_answers()
    # A fresh clone can give the files any times at all, so make them lie.
    os.utime(older / "replies.jsonl", (2_000_000_000, 2_000_000_000))
    os.utime(newer / "replies.jsonl", (1_000_000_000, 1_000_000_000))
    assert reused(in_runs, earlier_replies()) == "call 2"


def test_same_answer_wins_a_run_with_no_manifest_counts_as_the_oldest(in_runs):
    _, stopped = two_answers()
    (stopped / "manifest.json").unlink()
    assert reused(in_runs, earlier_replies()) == "call 1"


def test_same_answer_wins_runs_that_started_together_go_by_folder_name(in_runs):
    model = FakeModel()
    answered("a-first", model)
    second = answered("b-second", model)
    os.utime(second / "replies.jsonl", (1_000_000_000, 1_000_000_000))
    assert reused(in_runs, earlier_replies()) == "call 2"


def test_plays_live_no_watch_opens_nothing_and_never_waits(config, capsys, monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("--no-watch must not open a view or wait")

    monkeypatch.setattr(webbrowser, "open", refuse)
    monkeypatch.setattr("time.sleep", refuse)
    events = played(config, capsys) / "events.jsonl"
    assert len(events.read_text().splitlines()) == TURNS


@pytest.fixture
def watching(monkeypatch):
    """Run with a stand-in browser that reads the live page on every paced turn."""
    seen = {"opened": [], "turns": [], "served": []}

    def fake_sleep(seconds):
        assert 0 < seconds <= runs.PACE_SECONDS
        with urllib.request.urlopen(seen["opened"][0] + "turns") as reply:
            seen["turns"].append(json.load(reply)["turns"])

    monkeypatch.setattr(webbrowser, "open", lambda url: seen["opened"].append(url))
    monkeypatch.setattr("time.sleep", fake_sleep)
    monkeypatch.setattr(
        cli, "_serve_until_interrupted", lambda: seen["served"].append(1)
    )
    return seen


def test_plays_live_run_opens_the_view_by_default(config, capsys, watching):
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    out = capsys.readouterr().out
    assert len(watching["opened"]) == 1
    assert watching["opened"][0] in out
    assert "runs/small-seed-1" in out


def test_plays_live_stays_open_at_a_terminal_but_not_in_a_script(
    config, capsys, watching, monkeypatch
):
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    assert watching["served"] == []
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True, raising=False)
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    assert watching["served"] == [1]


def test_paced_from_cache_a_game_plays_turn_by_turn(config, capsys, watching):
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    assert watching["turns"] == list(range(1, TURNS + 1))


def test_paced_from_cache_a_repeat_plays_turn_by_turn_too(config, capsys, watching):
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    watching["turns"].clear()
    watching["opened"].clear()
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    assert watching["turns"] == list(range(1, TURNS + 1))
