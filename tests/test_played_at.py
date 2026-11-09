# Implements: runs/played-at
"""Every game's manifest names the commit that played it."""

import json
import shutil
import subprocess
from pathlib import Path

from treasure_island import cli, saved_game

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def played(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    config = shutil.copy(ROOT / "configs/silent.toml", tmp_path / "silent.toml")
    assert cli.main(["run", str(config), "--seed", "7", "--no-watch"]) == 0
    folder = tmp_path / capsys.readouterr().out.strip()
    return json.loads((folder / "manifest.json").read_text())


def test_played_at_the_manifest_names_the_commit_and_whether_it_was_dirty(
    tmp_path, monkeypatch, capsys
):
    manifest = played(tmp_path, monkeypatch, capsys)
    assert manifest["commit"] == git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain", "--untracked-files=no"))
    assert manifest["dirty"] is dirty


def test_played_at_outside_a_checkout_names_no_commit(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(saved_game, "CODE", tmp_path)  # not a git checkout
    manifest = played(tmp_path, monkeypatch, capsys)
    assert "commit" not in manifest and "dirty" not in manifest
