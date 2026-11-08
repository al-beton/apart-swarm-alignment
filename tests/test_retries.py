# Implements: treasure-island/retries-dropped-calls
"""A model call that drops is tried again with backoff; only the last failure stops."""

import http.client
import io
import json
import socket
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from treasure_island import retries, saved_game
from treasure_island.llm import TOOL_DEFINITIONS
from treasure_island.openrouter import OpenRouter
from treasure_island.saved_game import Models

HERE = Path(__file__).parent

DIG = json.dumps({"tool": "dig", "arguments": {}})
CONFIG = """
grid_size = 2
turns_per_pirate = 2
brain = "silent"
thinking = false

[[pirates]]
model = "fake/flaky"
"""


class Flaky:
    """A backend that fails with `errors`, one per call, then digs."""

    def __init__(self, *errors):
        self.errors = list(errors)
        self.calls = 0

    def __call__(self, request):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return DIG, 0.0


@pytest.fixture
def waits(monkeypatch):
    slept = []
    monkeypatch.setattr(retries, "_sleep", slept.append)
    return slept


@pytest.fixture
def toml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "flaky.toml"
    path.write_text(CONFIG)
    return path


def play(toml, backend):
    # No cache: each game here must ask its backend, not an earlier game's replies.
    models = Models(backend, cache=False, agree=lambda: True)
    folder = saved_game.play_saved(toml, 0, models=models)
    return folder, (folder / "story.txt").read_text().splitlines()


def dns():
    return urllib.error.URLError(socket.gaierror(8, "nodename nor servname provided"))


def test_retries_dropped_calls_a_dropped_call_is_tried_again(toml, waits):
    backend = Flaky(dns(), TimeoutError("timed out"))
    _, story = play(toml, backend)
    assert backend.errors == []  # both failures were tried past
    assert story[-1].startswith("Game over:")
    assert waits == list(retries.WAITS[:2])


def test_retries_dropped_calls_back_off_to_about_a_minute(waits, toml):
    assert len(retries.WAITS) == 4  # 5 tries
    assert list(retries.WAITS) == sorted(retries.WAITS)
    assert 45 <= sum(retries.WAITS) <= 75


def test_retries_dropped_calls_the_story_says_so_on_that_turn(toml, waits):
    _, story = play(toml, Flaky(dns(), dns()))
    assert "its model call dropped 2 times and was tried again" in story[0]
    assert all("dropped" not in line for line in story[1:])


def test_retries_dropped_calls_the_story_is_the_same_on_replay(toml, waits):
    folder, _ = play(toml, Flaky(dns()))
    assert saved_game.differences(folder) == []


def test_retries_dropped_calls_a_5xx_is_retried_but_a_4xx_is_not(toml, waits):
    gone = urllib.error.HTTPError("https://x.invalid", 503, "busy", None, None)
    backend = Flaky(gone)
    _, story = play(toml, backend)
    assert backend.errors == []
    assert story[-1].startswith("Game over:")
    refused = urllib.error.HTTPError("https://x.invalid", 401, "no", None, None)
    with pytest.raises(urllib.error.HTTPError):
        play(toml, Flaky(refused))


def test_retries_dropped_calls_a_stream_the_server_closes_part_way_is_retried():
    # httpx's own error when Adaption closes a streamed reply before its end.
    import httpx

    closed = httpx.RemoteProtocolError(
        "peer closed connection without sending complete message body"
    )
    assert retries.dropped(closed)
    assert retries.dropped(httpx.ReadTimeout("slow"))


def test_retries_dropped_calls_only_the_last_failure_stops_the_run(toml, waits):
    backend = Flaky(*[dns() for _ in range(5)])
    folder, story = play(toml, backend)
    assert backend.calls == 5
    assert story[-1].startswith("Game stopped:")
    assert "run the same command again" in story[-1]
    manifest = json.loads((folder / "manifest.json").read_text())
    assert "stopped" in manifest


class CutOff(io.BytesIO):
    """A reply whose connection drops after the headers, part way through the body."""

    def read(self, *size):
        raise http.client.IncompleteRead(b'{"choi', 900)


def test_retries_dropped_calls_a_reply_cut_off_part_way_is_tried_again(
    waits, monkeypatch
):
    whole = json.dumps(json.loads((HERE / "openrouter-reply.json").read_text()))
    answers = [CutOff(), io.BytesIO(whole.encode())]
    monkeypatch.setattr(
        urllib.request, "urlopen", lambda request, timeout=None: answers.pop(0)
    )
    backend = retries.Retrying(OpenRouter("some/model", "not-a-real-key"))
    request = {
        "agent": "pirate-1",
        "model": "openrouter/some/model",
        "seed": 0,
        "system": "rules",
        "messages": [{"role": "user", "content": "your turn"}],
        "tools": TOOL_DEFINITIONS,
        "max_tokens": 300,
        "thinking": False,
        "thinking_tokens": 0,
    }
    text, _ = backend(request)
    assert json.loads(text)["tool"] == "move"
    assert backend.last_retries == 1
    assert waits == [retries.WAITS[0]]
    assert retries.dropped(http.client.RemoteDisconnected("gone"))
