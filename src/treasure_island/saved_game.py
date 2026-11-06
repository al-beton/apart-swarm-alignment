"""A real game as a named run: played into a folder, and replayed from it.

`play_saved` writes `runs/<config>-seed-<N>/`: `config.json` (every lever, defaults
included, so a later change of default can't change what this run was),
`events.jsonl`, `story.txt` and `pirates-log.txt` (see game_loop), `replies.jsonl`
(every model reply, which scripted brains don't make) and `manifest.json` (what
varies between identical runs).

`differences` plays the game again from that folder, in a temporary folder and
with nothing but what's saved, and names any log that doesn't match byte for byte.

Implements: treasure-island/named-runs, treasure-island/everything-cached, runs/plays-live
"""

import datetime
import json
import tempfile
import tomllib
from pathlib import Path

from treasure_island.config import parse_config, save_config
from treasure_island.game_loop import write_game
from treasure_island.runs import new_folder
from treasure_island.strategies import brains_for

LOGS = ("events.jsonl", "story.txt", "pirates-log.txt")


def is_real_config(path):
    """Whether a config plays the real game: only those name a brain."""
    return "brain" in tomllib.loads(Path(path).read_text(encoding="utf-8"))


def is_real_run(folder):
    return (Path(folder) / "story.txt").is_file()


def _now():
    return datetime.datetime.now(datetime.UTC).isoformat()


def _write_json(path, value):
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def play_saved(config_path, seed, on_start=None, pace=0):
    """Play the config with this seed into a new named folder; return the folder.

    `on_start(folder)` is called once the folder can be watched, before any turn,
    and `pace` waits that many seconds after each turn. Neither changes the game.
    """
    data = tomllib.loads(Path(config_path).read_text(encoding="utf-8"))
    data["seed"] = seed
    config = parse_config(data)
    brains = brains_for(config.brain, config)
    folder = new_folder(f"{Path(config_path).stem}-seed-{seed}")
    save_config(config, folder / "config.json")
    (folder / "replies.jsonl").touch()
    if on_start:
        on_start(folder)
    started_at = _now()
    write_game(config, brains, folder, pace)
    manifest = {
        "started_at": started_at,
        "finished_at": _now(),
        "cost_usd": 0,
        "cache_hits": 0,
        "cache_misses": 0,
    }
    text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    (folder / "manifest.json").write_text(text, encoding="utf-8")
    return folder


def differences(folder):
    """The logs a replay of this folder doesn't rebuild byte for byte."""
    folder = Path(folder)
    config = parse_config(
        json.loads((folder / "config.json").read_text(encoding="utf-8"))
    )
    with tempfile.TemporaryDirectory() as scratch:
        write_game(config, brains_for(config.brain, config), scratch)
        return [
            log
            for log in LOGS
            if (Path(scratch) / log).read_bytes() != (folder / log).read_bytes()
        ]
