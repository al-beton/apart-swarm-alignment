# Implements: runs/run-command, runs/run-folder, runs/replies-keyed, runs/manifest-varies, runs/replay-byte-identical, runs/no-silent-model-calls, runs/plays-live, runs/paced-from-cache, runs/cache-across-runs, runs/no-cache, treasure-island/everything-cached
"""Running a game into a folder, and replaying that folder offline."""

import json
import os
import shutil
import socket
import sys
import urllib.request
import webbrowser

import pytest

from treasure_island import cli, runs
from treasure_island.event_log import log_errors
from treasure_island.runs import MissingReply, Replies, replay, request_key

CONFIG = """
size = 3
pirates = 2
turns = 12
model = "scripted/random"
temperature = 0.0
"""
REQUEST = {
    "agent": "pirate-a",
    "model": "scripted/random",
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


def test_run_command_makes_a_new_folder_each_time(config, capsys):
    first = played(config, capsys)
    before = contents(first)
    second = played(config, capsys)
    assert first != second
    assert first.parent.name == second.parent.name == "runs"
    assert contents(first) == before


def test_run_folder_holds_events_replies_config_and_manifest(config, capsys):
    folder = played(config, capsys, seed=4)
    assert {path.name for path in folder.iterdir()} == {
        "events.jsonl",
        "replies.jsonl",
        "config.json",
        "manifest.json",
    }
    saved = json.loads((folder / "config.json").read_text())
    assert saved["seed"] == 4 and saved["size"] == 3


def test_run_folder_events_pass_the_validator(config, capsys):
    folder = played(config, capsys)
    assert log_errors(folder / "events.jsonl") == []


@pytest.mark.parametrize(
    "part,other",
    [
        ("agent", "pirate-b"),
        ("model", "scripted/other"),
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


@pytest.mark.parametrize("separator", ["\u2028", "\u0085", "\x0c"])
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
    }
    assert manifest["cost_usd"] == 0
    assert manifest["cache_misses"] > 0


def test_manifest_varies_two_identical_runs_differ_nowhere_else(config, capsys):
    first = contents(played(config, capsys))
    second = contents(played(config, capsys))
    first.pop("manifest.json")
    second.pop("manifest.json")
    assert first == second


def test_replay_byte_identical_with_no_keys_or_network(config, capsys, monkeypatch):
    folder = played(config, capsys)
    for name in os.environ:
        if name.endswith("_API_KEY"):
            monkeypatch.delenv(name)

    def no_network(*args, **kwargs):
        raise AssertionError("replay opened a socket")

    monkeypatch.setattr(socket, "socket", no_network)
    assert cli.main(["replay", str(folder)]) == 0
    rebuilt = replay(folder)
    assert rebuilt == (folder / "events.jsonl").read_bytes()
    assert rebuilt


def test_replay_byte_identical_fails_when_a_reply_changed(config, capsys):
    folder = played(config, capsys)
    path = folder / "replies.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows[0]["reply"] = "dig" if rows[0]["reply"] != "dig" else "move north"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    assert cli.main(["replay", str(folder)]) == 1


def test_replay_byte_identical_leaves_the_folder_untouched(config, capsys):
    folder = played(config, capsys)
    before = contents(folder)
    assert cli.main(["replay", str(folder)]) == 0
    assert contents(folder) == before


def test_no_silent_model_calls_a_missing_reply_fails_the_replay(config, capsys):
    folder = played(config, capsys)
    path = folder / "replies.jsonl"
    path.write_text("".join(path.read_text().splitlines(keepends=True)[1:]))
    with pytest.raises(MissingReply):
        replay(folder)
    before = contents(folder)
    assert cli.main(["replay", str(folder)]) == 1
    assert contents(folder) == before


class FakeModel:
    """Stands in for a paid model: every call is new, costs money and is counted."""

    def __init__(self):
        self.calls = 0

    def __call__(self, request):
        self.calls += 1
        return f"write call {self.calls}", 0.01


@pytest.fixture
def model(monkeypatch):
    fake = FakeModel()
    monkeypatch.setattr(runs, "backend_for", lambda name: fake)
    return fake


def manifest_of(folder):
    return json.loads((folder / "manifest.json").read_text())


def turns_in(folder):
    return len((folder / "events.jsonl").read_text().splitlines())


def test_cache_across_runs_a_repeat_asks_the_model_nothing(config, capsys, model):
    first = played(config, capsys)
    asked = model.calls
    second = played(config, capsys)
    assert asked == 12 and model.calls == asked
    assert first != second
    assert (first / "events.jsonl").read_bytes() == (
        second / "events.jsonl"
    ).read_bytes()
    manifest = manifest_of(second)
    assert (manifest["cache_hits"], manifest["cache_misses"]) == (12, 0)
    assert manifest["cost_usd"] == 0


def test_cache_across_runs_its_folder_alone_regenerates_the_game(config, capsys, model):
    first = played(config, capsys)
    second = played(config, capsys)
    shutil.rmtree(first)
    assert cli.main(["replay", str(second)]) == 0
    assert replay(second) == (second / "events.jsonl").read_bytes()


def test_cache_across_runs_only_the_same_request_reuses_a_reply(config, capsys, model):
    played(config, capsys, seed=1)
    asked = model.calls
    played(config, capsys, seed=2)
    assert model.calls == asked * 2


def test_cache_across_runs_replay_never_borrows_from_another_run(config, capsys, model):
    played(config, capsys)
    second = played(config, capsys)
    path = second / "replies.jsonl"
    path.write_text("".join(path.read_text().splitlines(keepends=True)[1:]))
    with pytest.raises(MissingReply):
        replay(second)


def test_no_cache_asks_again_into_a_new_folder(config, capsys, model):
    first = played(config, capsys)
    before = contents(first)
    fresh = played(config, capsys, "--no-cache")
    assert model.calls == 24
    assert fresh != first
    assert contents(first) == before
    assert (fresh / "events.jsonl").read_bytes() != before["events.jsonl"]
    assert manifest_of(fresh)["cache_misses"] == 12
    assert cli.main(["replay", str(fresh)]) == 0


def test_no_cache_a_later_repeat_reuses_the_newest_replies(config, capsys, model):
    played(config, capsys)
    fresh = played(config, capsys, "--no-cache")
    repeat = played(config, capsys)
    assert (repeat / "events.jsonl").read_bytes() == (
        fresh / "events.jsonl"
    ).read_bytes()


def test_plays_live_no_watch_opens_nothing_and_never_waits(
    config, capsys, model, monkeypatch
):
    def refuse(*args, **kwargs):
        raise AssertionError("--no-watch must not open a view or wait")

    monkeypatch.setattr(webbrowser, "open", refuse)
    monkeypatch.setattr(runs.time, "sleep", refuse)
    assert turns_in(played(config, capsys)) == 12


@pytest.fixture
def watching(monkeypatch):
    """Run with a stand-in browser that reads the live page on every paced turn."""
    seen = {"opened": [], "turns": [], "served": []}

    def fake_sleep(seconds):
        assert 0 < seconds <= runs.PACE_SECONDS
        with urllib.request.urlopen(seen["opened"][0] + "turns") as reply:
            seen["turns"].append(json.load(reply)["turns"])

    monkeypatch.setattr(webbrowser, "open", lambda url: seen["opened"].append(url))
    monkeypatch.setattr(runs.time, "sleep", fake_sleep)
    monkeypatch.setattr(
        cli, "_serve_until_interrupted", lambda: seen["served"].append(1)
    )
    return seen


def test_plays_live_run_opens_the_view_by_default(config, capsys, model, watching):
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    out = capsys.readouterr().out
    assert len(watching["opened"]) == 1
    assert watching["opened"][0] in out
    assert "runs/small-seed-1" in out


def test_plays_live_stays_open_at_a_terminal_but_not_in_a_script(
    config, capsys, model, watching, monkeypatch
):
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    assert watching["served"] == []
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True, raising=False)
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    assert watching["served"] == [1]


def test_paced_from_cache_a_new_game_plays_turn_by_turn(
    config, capsys, model, watching
):
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    assert watching["turns"] == list(range(1, 13))


def test_paced_from_cache_a_cached_game_plays_turn_by_turn_too(
    config, capsys, model, watching
):
    played(config, capsys)
    asked = model.calls
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    assert model.calls == asked
    assert watching["turns"] == list(range(1, 13))


def test_cache_across_runs_a_longer_game_keeps_a_scripted_agent_s_memory(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.chdir(tmp_path)
    short = tmp_path / "short.toml"
    short.write_text('size = 3\npirates = 1\nturns = 2\nmodel = "scripted/counter"\n')
    long = tmp_path / "long.toml"
    long.write_text('size = 3\npirates = 1\nturns = 4\nmodel = "scripted/counter"\n')
    played(short, capsys)
    folder = played(long, capsys)
    events = [json.loads(line) for line in (folder / "events.jsonl").open()]
    assert [e["did"][0]["text"] for e in events] == ["1", "2", "3", "4"]
    manifest = manifest_of(folder)
    assert (manifest["cache_hits"], manifest["cache_misses"]) == (2, 2)
