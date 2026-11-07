# Implements: treasure-island/named-runs, treasure-island/everything-cached, treasure-island/brain-in-config, runs/replay-byte-identical
"""`treasure-island run` and `replay` on the real game."""

import json
import os
import shutil
import socket
from pathlib import Path

import pytest

from treasure_island import cli, saved_game
from treasure_island.config import ConfigError, load_config, parse_config
from treasure_island.strategies import brains_for

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "runs/s-sweep-seed-7"
LOGS = ("events.jsonl", "story.txt", "pirates-log.txt")


@pytest.fixture
def config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return shutil.copy(ROOT / "configs/s-sweep.toml", tmp_path / "s-sweep.toml")


def played(config_path, capsys, seed=7):
    assert cli.main(["run", str(config_path), "--seed", str(seed), "--no-watch"]) == 0
    return Path(config_path).parent / capsys.readouterr().out.strip()


def contents(folder):
    return {path.name: path.read_bytes() for path in folder.iterdir()}


def test_named_runs_save_config_seed_both_logs_and_replies(config, capsys):
    folder = played(config, capsys)
    assert {path.name for path in folder.iterdir()} == {
        *LOGS,
        "config.json",
        "replies.jsonl",
        "manifest.json",
    }
    saved = json.loads((folder / "config.json").read_text())
    assert saved["seed"] == 7
    assert saved["brain"] == "s-sweep"
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["cost_usd"] == 0
    assert set(manifest) >= {"started_at", "finished_at"}


def test_named_runs_are_named_after_config_and_seed_and_never_overwrite(config, capsys):
    first = played(config, capsys)
    before = contents(first)
    second = played(config, capsys)
    assert first.name == "s-sweep-seed-7"
    assert second.name == "s-sweep-seed-7-2"
    assert contents(first) == before


def test_named_runs_the_seed_on_the_command_line_decides_the_game(config, capsys):
    seven = played(config, capsys, seed=7)
    six = played(config, capsys, seed=6)
    assert (seven / "events.jsonl").read_bytes() != (six / "events.jsonl").read_bytes()
    assert '"seed": 6' in (six / "config.json").read_text()


def test_named_runs_the_committed_game_replays_byte_identical(capsys):
    assert cli.main(["replay", str(COMMITTED)]) == 0
    assert "Score 40" in (COMMITTED / "story.txt").read_text()


def test_named_runs_save_every_lever_even_the_defaults(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "plain.toml"
    path.write_text('brain = "say-a-number"\nturns_per_pirate = 2\n')
    folder = played(path, capsys, seed=1)
    saved = json.loads((folder / "config.json").read_text())
    assert saved["grid_size"] == 10
    assert saved["crew_size"] == 6
    assert saved["turns_per_pirate"] == 2
    assert len(saved["pirates"]) == 6
    assert saved["pirates"][0]["personality"] == 1
    assert cli.main(["replay", str(folder)]) == 0


def test_named_runs_the_viewer_can_render_one(config, capsys):
    folder = played(config, capsys)
    out = folder.parent / "game.gif"
    assert cli.main(["render", str(folder), "--out", str(out)]) == 0
    assert out.read_bytes().startswith(b"GIF")


def test_everything_cached_replay_is_byte_identical_with_no_keys_or_network(
    config, capsys, monkeypatch
):
    folder = played(config, capsys)
    for name in os.environ:
        if name.endswith("_API_KEY"):
            monkeypatch.delenv(name)

    def no_network(*args, **kwargs):
        raise AssertionError("replay opened a socket")

    monkeypatch.setattr(socket, "socket", no_network)
    assert cli.main(["replay", str(folder)]) == 0


@pytest.mark.parametrize("log", LOGS)
def test_everything_cached_replay_fails_if_a_log_changed(log, config, capsys):
    folder = played(config, capsys)
    path = folder / log
    path.write_bytes(path.read_bytes() + b"\n")
    assert cli.main(["replay", str(folder)]) == 1
    assert log in capsys.readouterr().err


def test_everything_cached_replay_fails_if_the_config_changed(config, capsys):
    folder = played(config, capsys)
    path = folder / "config.json"
    saved = json.loads(path.read_text())
    saved["seed"] = 6
    path.write_text(json.dumps(saved))
    assert cli.main(["replay", str(folder)]) == 1


def test_everything_cached_replay_leaves_the_folder_untouched(config, capsys):
    folder = played(config, capsys)
    before = contents(folder)
    assert cli.main(["replay", str(folder)]) == 0
    assert contents(folder) == before


def test_brain_in_config_picks_what_plays():
    config = load_config(ROOT / "configs/say-a-number.toml")
    assert config.brain == "say-a-number"
    assert len(brains_for(config.brain, config)) == config.crew_size


def test_brain_in_config_refuses_one_it_does_not_know():
    config = parse_config({"brain": "ouija"})
    with pytest.raises(ConfigError, match="ouija"):
        brains_for(config.brain, config)
    with pytest.raises(ConfigError, match="brain"):
        parse_config({"brain": 3})


def test_named_runs_a_real_game_opens_for_watching_before_the_first_turn(config):
    seen = []

    def on_start(folder):
        seen.append(
            ((folder / "config.json").is_file(), (folder / "story.txt").exists())
        )

    folder = saved_game.play_saved(config, 7, on_start)
    assert seen == [(True, False)]
    assert (folder / "story.txt").is_file()


def test_named_runs_a_real_game_is_paced_only_when_watched(config, monkeypatch):
    naps = []
    monkeypatch.setattr("time.sleep", naps.append)
    plain = saved_game.play_saved(config, 7)
    assert naps == []
    paced = saved_game.play_saved(config, 7, pace=0.25)
    assert naps and set(naps) == {0.25}
    assert (plain / "events.jsonl").read_bytes() == (
        paced / "events.jsonl"
    ).read_bytes()


def test_named_runs_run_opens_the_view_on_a_real_game(config, capsys, monkeypatch):
    opened = []
    monkeypatch.setattr("webbrowser.open", opened.append)
    monkeypatch.setattr("time.sleep", lambda seconds: None)
    assert cli.main(["run", str(config), "--seed", "7"]) == 0
    assert len(opened) == 1
    assert opened[0].startswith("http://127.0.0.1:")
