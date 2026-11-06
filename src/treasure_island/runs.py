"""Playing a game into a run folder, and replaying that folder offline.

A run folder holds `config.json` (the game and its seed), `events.jsonl` (what
happened), `replies.jsonl` (every reply a model gave) and `manifest.json` (what
varies between identical runs, so the other three don't have to).

Model providers can't promise the same reply twice, so exact replay comes from
stored replies. `run` and `replay` share one path through the game and differ
only in `Replies`: with no backend, a reply that isn't stored fails instead of
calling anything. Everything that shapes a request is in the request, so hashing
all of it makes the key, and anything added to a request later joins the key.

Events and replies are written as they happen, so a run can be followed live.

Implements: runs/run-command, runs/run-folder, runs/replies-keyed, runs/manifest-varies, runs/replay-byte-identical, runs/no-silent-model-calls, agents/one-interface
"""

import dataclasses
import datetime
import hashlib
import json
import tomllib
from pathlib import Path

from treasure_island.backends import backend_for
from treasure_island.event_log import log_errors
from treasure_island.game import Config, play

RUNS = Path("runs")


class MissingReply(LookupError):
    """A replay needed a reply the run folder doesn't hold."""


def _line(value):
    """One JSON Lines row, always the same bytes for the same value.

    Escaping everything outside ASCII keeps one row on one line, because
    `str.splitlines` also splits on characters JSON would otherwise leave raw.
    """
    return (json.dumps(value, sort_keys=True) + "\n").encode()


def request_key(request):
    return hashlib.sha256(_line(request)).hexdigest()


class Replies:
    """The replies a run got, stored in a file. No backend means replay."""

    def __init__(self, path, backend=None):
        self.path = Path(path)
        self.backend = backend
        self.hits = self.misses = 0
        self.cost_usd = 0.0
        self._stored = {}
        if self.path.exists():
            rows = map(json.loads, self.path.read_text().splitlines())
            self._stored = {row["key"]: row["reply"] for row in rows}

    def ask(self, request):
        key = request_key(request)
        if key in self._stored:
            self.hits += 1
            return self._stored[key]
        if self.backend is None:
            raise MissingReply(f"No stored reply for {request['agent']}: {key}")
        self.misses += 1
        text, cost = self.backend(request)
        self.cost_usd += cost
        self._stored[key] = text
        with self.path.open("ab") as file:
            file.write(_line({"key": key, "request": request, "reply": text}))
        return text


def _new_folder(name):
    """runs/<name>, or runs/<name>-2 and so on if that's already taken."""
    RUNS.mkdir(exist_ok=True)
    folder, tries = RUNS / name, 1
    while True:
        try:
            folder.mkdir()
            return folder
        except FileExistsError:
            tries += 1
            folder = RUNS / f"{name}-{tries}"


def _now():
    return datetime.datetime.now(datetime.UTC).isoformat()


def run(config_path, seed):
    """Play the config once into a new run folder, and return the folder."""
    config = Config(**tomllib.loads(Path(config_path).read_text()))
    backend = backend_for(config.model)
    folder = _new_folder(f"{Path(config_path).stem}-seed-{seed}")
    saved = {**dataclasses.asdict(config), "seed": seed}
    (folder / "config.json").write_bytes(_line(saved))
    replies = Replies(folder / "replies.jsonl", backend)
    started_at = _now()
    with (folder / "events.jsonl").open("wb") as events:
        for record in play(config, seed, replies.ask):
            events.write(_line(record))
            events.flush()
    manifest = {
        "started_at": started_at,
        "finished_at": _now(),
        "cost_usd": replies.cost_usd,
        "cache_hits": replies.hits,
        "cache_misses": replies.misses,
    }
    (folder / "manifest.json").write_bytes(_line(manifest))
    if errors := log_errors(folder / "events.jsonl"):
        raise ValueError("\n".join(errors))
    return folder


def replay(folder):
    """The events a run's stored replies rebuild, as bytes. Writes nothing."""
    folder = Path(folder)
    saved = json.loads((folder / "config.json").read_text())
    seed = saved.pop("seed")
    replies = Replies(folder / "replies.jsonl")
    records = play(Config(**saved), seed, replies.ask)
    return b"".join(_line(record) for record in records)
