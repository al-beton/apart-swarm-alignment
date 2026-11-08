"""What a run needs that isn't the game: a folder of its own, and model replies.

The game itself is in `game_loop` and a saved run in `saved_game`. Scripted brains
make no replies, so `Replies` and `earlier_replies` wait for the first brain that
asks a model, and nothing in a game calls them yet.

Model providers can't promise the same reply twice, so exact replay comes from
stored replies. With no backend, a reply that isn't stored fails instead of calling
anything. Everything that shapes a request is in the request, so hashing all of it
makes the key, and anything added to a request later joins the key.

A run also reuses any earlier run's reply to the same request, since the key says
the request is identical, and copies it into its own `replies.jsonl`, so its folder
alone can regenerate it. If two runs answered one request differently, the run that
started last wins, by the time committed in its manifest: file times don't survive a
clone, so they'd play a different game on another machine. Replay never borrows: it
only reads the folder it's checking.

Implements: treasure-island/retries-dropped-calls, runs/run-command, runs/replies-keyed, runs/no-silent-model-calls, runs/paced-from-cache, runs/cache-across-runs, runs/same-answer-wins, runs/no-cache, agents/backend-interface, treasure-island/everything-cached
"""

import hashlib
import json
from pathlib import Path

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
        self.last_retries = 0  # how often the last reply's call was tried again
        self._stored, self._retries = {}, {}
        if self.path.exists():
            for row in map(json.loads, self.path.read_text().splitlines()):
                self._stored[row["key"]] = row["reply"]
                self._retries[row["key"]] = row.get("retries", 0)

    def ask(self, request):
        key = request_key(request)
        self.last_retries = self._retries.get(key, 0)
        if key in self._stored:
            self.hits += 1
            return self._stored[key]
        if key in self.earlier:
            self.hits += 1
            return self._keep(key, request, self.earlier[key])
        if self.backend is None:
            raise MissingReply(f"No stored reply for {request['agent']}: {key}")
        self.misses += 1
        text, cost = self.backend(request)
        self.cost_usd += cost
        self.last_retries = getattr(self.backend, "last_retries", 0)
        return self._keep(key, request, text, self.last_retries)

    def _keep(self, key, request, text, retries=0):
        self._stored[key] = text
        self._retries[key] = retries
        row = {"key": key, "request": request, "reply": text}
        if retries:  # the call dropped and was tried again, which the story says
            row["retries"] = retries
        with self.path.open("ab") as file:
            file.write(_line(row))
        return text


def _started_at(replies_path):
    """When a run started, as sortable UTC text; "" if it never wrote a manifest."""
    manifest = replies_path.with_name("manifest.json")
    return json.loads(manifest.read_text())["started_at"] if manifest.exists() else ""


def earlier_rows():
    """Every stored reply earlier runs got, with its request, oldest run first."""
    paths = sorted(
        RUNS.glob("**/replies.jsonl"), key=lambda p: (_started_at(p), str(p.parent))
    )
    return [json.loads(line) for p in paths for line in p.read_text().splitlines()]


def earlier_replies():
    """Every reply earlier runs got, by key, the last run to start winning."""
    return {row["key"]: row["reply"] for row in earlier_rows()}


def new_folder(name):
    """runs/<name>, or runs/<name>-2 and so on if that's already taken.

    A name may hold a slash, as `<config>/<seed>` does: its parents are made too.
    """
    RUNS.mkdir(exist_ok=True)
    folder, tries = RUNS / name, 1
    while True:
        try:
            folder.parent.mkdir(parents=True, exist_ok=True)
            folder.mkdir()
            return folder
        except FileExistsError:
            tries += 1
            folder = RUNS / f"{name}-{tries}"
