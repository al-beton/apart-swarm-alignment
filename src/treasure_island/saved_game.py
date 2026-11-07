"""A game as a named run: played into a folder, and replayed from it.

`play_saved` writes `runs/<config>-seed-<N>/`: `config.json` (every lever, defaults
included, so a later change of default can't change what this run was),
`events.jsonl`, `story.txt` and `pirates-log.txt` (see game_loop), `replies.jsonl`
(every model reply, which scripted brains don't make) and `manifest.json` (what
varies between identical runs).

A model's replies go through `Replies`: a live run asks the model's backend for
any reply neither this run nor an earlier one has (unless `cache` is off), and
replay asks nothing, so a reply its folder doesn't hold fails instead of costing.

`differences` plays the game again from that folder, in a temporary folder and
with nothing but what's saved, and names any log that doesn't match byte for byte.

Implements: agents/plays-then-replays, runs/cache-across-runs, runs/no-cache, treasure-island/named-runs, treasure-island/everything-cached, runs/one-game, runs/run-folder, runs/manifest-varies, runs/replay-byte-identical, runs/plays-live, results/examples-stay-true, agents/key-from-the-environment
"""

import dataclasses
import datetime
import json
import tempfile
import tomllib
from pathlib import Path

from treasure_island.backends import backend_for
from treasure_island.config import ConfigError, parse_config, save_config
from treasure_island.game_loop import write_game
from treasure_island.runs import Replies, earlier_replies, new_folder
from treasure_island.strategies import brains_for

LOGS = ("events.jsonl", "story.txt", "pirates-log.txt")


def _now():
    return datetime.datetime.now(datetime.UTC).isoformat()


def _write_json(path, value):
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _every_model(config):
    """A backend that hands each request to its own model's backend.

    Every pirate's backend is made now, so an unknown model or a missing key is
    refused before the game starts.
    """
    models = {pirate.model for pirate in config.pirates if pirate.model}
    backends = {model: backend_for(model) for model in sorted(models)}

    def ask(request):
        return backends[request["model"]](request)

    return ask


@dataclasses.dataclass(frozen=True)
class Models:
    """How a live run reaches its models: `cache=False` asks every model again,
    and `backend` stands in for every model's own (a test's fake, say)."""

    backend: object = None
    cache: bool = True


ASK_EVERY_MODEL = Models()


def play_saved(config_path, seed, on_start=None, pace=0, models=ASK_EVERY_MODEL):
    """Play the config with this seed into a new named folder; return the folder.

    `on_start(folder)` is called once the folder can be watched, before any turn,
    and `pace` waits that many seconds after each turn. Neither changes the game.
    """
    config = config_with_seed(config_path, seed)
    brains_for(config.brain, config)  # a bad brain makes no folder
    if models.backend is None:  # nor does a model with no backend or no key
        models = dataclasses.replace(models, backend=_every_model(config))
    folder = new_folder(f"{Path(config_path).stem}-seed-{seed}")
    return write_saved(config, folder, on_start, pace, models)


def config_with_seed(config_path, seed):
    """The config a game of this file and seed plays; it must name a brain."""
    data = tomllib.loads(Path(config_path).read_text(encoding="utf-8"))
    if "brain" not in data:
        raise ConfigError(f"{Path(config_path).name} names no brain to play with.")
    return parse_config({**data, "seed": seed})


def write_saved(config, folder, on_start=None, pace=0, models=ASK_EVERY_MODEL):
    """Play `config` (see `config_with_seed`) into `folder`, which must exist."""
    folder = Path(folder)
    (folder / "replies.jsonl").touch()
    replies = Replies(
        folder / "replies.jsonl",
        models.backend or _every_model(config),
        earlier_replies() if models.cache else None,
    )
    brains = brains_for(config.brain, config, replies)
    save_config(config, folder / "config.json")
    if on_start:
        on_start(folder)
    started_at = _now()
    write_game(config, brains, folder, pace)
    manifest = {
        "started_at": started_at,
        "finished_at": _now(),
        "cost_usd": round(replies.cost_usd, 6) if replies.cost_usd else 0,
        "cache_hits": replies.hits,
        "cache_misses": replies.misses,
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
    replies = Replies(folder / "replies.jsonl")  # no backend: replay asks nothing
    with tempfile.TemporaryDirectory() as scratch:
        write_game(config, brains_for(config.brain, config, replies), scratch)
        return [
            log
            for log in LOGS
            if (Path(scratch) / log).read_bytes() != (folder / log).read_bytes()
        ]
