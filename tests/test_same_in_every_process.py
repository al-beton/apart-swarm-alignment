# Implements: runs/same-in-every-process
"""Repeating a run for real: the installed command, in separate processes.

Python hashes strings differently in each process unless told otherwise, so
anything that leans on set or hash order passes a test inside one process and
still plays a different game next time. Each run here gets its own hash seed.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from treasure_island.event_log import log_errors

ROOT = Path(__file__).resolve().parents[1]
COMMAND = Path(sys.executable).parent / "treasure-island"
CONFIGS = ["s-sweep", "say-a-number"]
# Two seeds that place the treasure on different squares.
SEED, OTHER_SEED = 7, 8


def command(*arguments, cwd, hash_seed):
    """Run the real command in a process of its own, with no keys; return its output."""
    env = {k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
    done = subprocess.run(
        [str(COMMAND), *map(str, arguments)],
        cwd=cwd,
        env={**env, "PYTHONHASHSEED": str(hash_seed)},
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout.strip()


def played(name, seed, cwd, hash_seed):
    """Play one game in its own process; return the folder it made."""
    cwd.mkdir(exist_ok=True)
    config = ROOT / "configs" / f"{name}.toml"
    out = command(
        "run", config, "--seed", seed, "--no-watch", cwd=cwd, hash_seed=hash_seed
    )
    return cwd / out


def contents(folder):
    return {path.name: path.read_bytes() for path in folder.iterdir()}


@pytest.mark.parametrize("name", CONFIGS)
def test_same_in_every_process_every_file_but_the_manifest_s_times(name, tmp_path):
    first = played(name, SEED, tmp_path / "a", hash_seed=1)
    second = played(name, SEED, tmp_path / "b", hash_seed=2)
    files, others = contents(first), contents(second)
    assert set(files) == set(others)
    manifest = files.pop("manifest.json")
    other_manifest = others.pop("manifest.json")
    assert files == others
    # Only the times may differ in the manifest.
    times = {"started_at", "finished_at"}
    kept = [
        {k: v for k, v in json.loads(m).items() if k not in times}
        for m in (manifest, other_manifest)
    ]
    assert kept[0] == kept[1]


@pytest.mark.parametrize("name", CONFIGS)
def test_same_in_every_process_the_gif_too(name, tmp_path):
    gifs = []
    for hash_seed, where in ((1, "a"), (2, "b")):
        folder = played(name, SEED, tmp_path / where, hash_seed)
        out = tmp_path / f"{where}.gif"
        command(
            "render", folder, "--out", out, cwd=tmp_path / where, hash_seed=hash_seed
        )
        gifs.append(out.read_bytes())
    assert gifs[0] == gifs[1]
    assert gifs[0]


@pytest.mark.parametrize("name", CONFIGS)
def test_same_in_every_process_another_seed_is_another_valid_game(name, tmp_path):
    first = contents(played(name, SEED, tmp_path / "a", hash_seed=1))
    other_folder = played(name, OTHER_SEED, tmp_path / "b", hash_seed=1)
    other = contents(other_folder)
    for file in ("events.jsonl", "story.txt", "config.json"):
        assert first[file] != other[file], file
    assert log_errors(other_folder / "events.jsonl") == []
    assert command("replay", other_folder, cwd=tmp_path / "b", hash_seed=2)
