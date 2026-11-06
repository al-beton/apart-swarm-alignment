# Implements: runs/run-command, runs/run-folder, runs/replies-keyed, runs/manifest-varies, runs/replay-byte-identical, runs/no-silent-model-calls
"""Running a game into a folder, and replaying that folder offline."""

import json
import os
import socket

import pytest

from treasure_island import cli
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


def played(config, capsys, seed=1):
    """Run the config through the command; return the folder it printed."""
    assert cli.main(["run", str(config), "--seed", str(seed)]) == 0
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
