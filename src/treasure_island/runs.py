"""Playing a game into a run folder, and replaying that folder offline.

A run folder holds `config.json` (the game and its seed), `events.jsonl` (what
happened), `replies.jsonl` (every reply a model gave) and `manifest.json` (what
varies between identical runs, so the other three don't have to).

Model providers can't promise the same reply twice, so exact replay comes from
stored replies. `run` and `replay` share one path through the game and differ
only in `Replies`: with no backend, a reply that isn't stored fails instead of
calling anything. Everything that shapes a request is in the request, so hashing
all of it makes the key, and anything added to a request later joins the key.

A run also reuses any earlier run's reply to the same request, since the key says
the request is identical, and copies it into its own `replies.jsonl`, so its folder
alone can regenerate it. If two runs answered one request differently, the newest
answer wins. Replay never borrows: it only reads the folder it's checking. A
scripted agent that remembers its turns always answers for itself: it's free, and
a look-alike request from another run may follow a different history.

Events and replies are written as they happen, so a run can be followed live. A
watched run waits out the rest of `PACE_SECONDS` after each turn, which is what
stops a game from the cache jumping to the end; a slow model is not slowed further.

Implements: runs/run-command, runs/run-folder, runs/replies-keyed, runs/manifest-varies, runs/replay-byte-identical, runs/no-silent-model-calls, runs/paced-from-cache, runs/cache-across-runs, runs/no-cache, agents/one-interface, treasure-island/everything-cached
"""

import dataclasses
import datetime
import hashlib
import json
import time
import tomllib
from pathlib import Path

from treasure_island.backends import backend_for
from treasure_island.event_log import log_errors
from treasure_island.game import Config, play

RUNS = Path("runs")
PACE_SECONDS = 0.6  # the page polls twice a second, so it shows every turn


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

    def __init__(self, path, backend=None, earlier=None):
        self.path = Path(path)
        self.backend = backend
        self.earlier = earlier or {}
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
        # The key can't vouch for a reply shaped by memory the request doesn't show.
        trusted = not getattr(self.backend, "remembers_outside_the_request", False)
        if key in self.earlier and trusted:
            self.hits += 1
            return self._keep(key, request, self.earlier[key])
        if self.backend is None:
            raise MissingReply(f"No stored reply for {request['agent']}: {key}")
        self.misses += 1
        text, cost = self.backend(request)
        self.cost_usd += cost
        return self._keep(key, request, text)

    def _keep(self, key, request, text):
        self._stored[key] = text
        with self.path.open("ab") as file:
            file.write(_line({"key": key, "request": request, "reply": text}))
        return text


def _earlier_replies():
    """Every reply earlier runs got, by key, the newest run's answer winning."""
    paths = sorted(RUNS.glob("*/replies.jsonl"), key=lambda p: (p.stat().st_mtime, p))
    rows = (json.loads(line) for p in paths for line in p.read_text().splitlines())
    return {row["key"]: row["reply"] for row in rows}


def new_folder(name):
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


def _wait_out_the_turn(started, pace):
    """Sleep for what's left of this turn's `pace` seconds, if anything."""
    left = pace - (time.monotonic() - started)
    if left > 0:
        time.sleep(left)


def run(config_path, seed, use_cache=True, on_start=None, pace=0):
    """Play the config once into a new run folder, and return the folder.

    `on_start(folder)` is called once the folder can be watched, before any turn.
    """
    config = Config(**tomllib.loads(Path(config_path).read_text()))
    backend = backend_for(config.model)
    earlier = _earlier_replies() if use_cache else {}
    folder = new_folder(f"{Path(config_path).stem}-seed-{seed}")
    saved = {**dataclasses.asdict(config), "seed": seed}
    (folder / "config.json").write_bytes(_line(saved))
    replies = Replies(folder / "replies.jsonl", backend, earlier)
    started_at = _now()
    with (folder / "events.jsonl").open("wb") as events:
        if on_start:
            on_start(folder)
        turn_started = time.monotonic()
        for record in play(config, seed, replies.ask):
            events.write(_line(record))
            events.flush()
            _wait_out_the_turn(turn_started, pace)
            turn_started = time.monotonic()
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
