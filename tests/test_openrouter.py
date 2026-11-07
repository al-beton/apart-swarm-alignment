# Implements: agents/openrouter-backend, agents/key-from-the-environment
"""The OpenRouter backend answers from a recorded reply, with no network and no key.

`openrouter-reply.json` follows the reply OpenRouter's API reference documents for
a tool call. It was written from that reference, not captured from a live call,
since tests and CI never spend; the first live game can replace it with a real one.
"""

import io
import json
import socket
import urllib.request
from pathlib import Path

import pytest

from treasure_island import cli
from treasure_island.backends import backend_for
from treasure_island.brain import BadToolCall
from treasure_island.llm import TOOL_DEFINITIONS, _read_reply

HERE = Path(__file__).parent
RECORDED = json.loads((HERE / "openrouter-reply.json").read_text())
KEY = "not-a-real-key"
MODEL = "openrouter/deepseek/deepseek-chat-v3.1"
REQUEST = {
    "agent": "pirate-1",
    "model": MODEL,
    "seed": 7,
    "system": "You are a pirate.",
    "messages": [{"role": "user", "content": "Turn 1. What do you do?"}],
    "tools": TOOL_DEFINITIONS,
    "max_tokens": 300,
    "thinking": False,
}
CONFIG = f"""
grid_size = 3
turns_per_pirate = 2
brain = "s-sweep"

[[pirates]]
model = "{MODEL}"
"""


class FakeOpenRouter:
    """Stands in for `urllib.request.urlopen`: keeps each request, gives one reply."""

    def __init__(self, reply):
        self.reply = reply
        self.sent = []

    def __call__(self, request, timeout=None):
        self.sent.append(request)
        return io.BytesIO(json.dumps(self.reply).encode())

    def body(self, index=0):
        return json.loads(self.sent[index].data)


@pytest.fixture
def offline(monkeypatch, tmp_path):
    """No keys, no sockets, and a fresh folder for runs/."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    def no_network(*args, **kwargs):
        raise AssertionError("a socket was opened")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def answering(monkeypatch, reply=RECORDED):
    monkeypatch.setenv("OPENROUTER_API_KEY", KEY)
    fake = FakeOpenRouter(reply)
    monkeypatch.setattr(urllib.request, "urlopen", fake)
    return fake


def ask(request=REQUEST):
    return backend_for(request["model"])(request)


def test_openrouter_backend_a_tool_call_comes_back_in_the_one_reply_form(
    offline, monkeypatch
):
    answering(monkeypatch)
    text, cost = ask()
    assert json.loads(text) == {"tool": "move", "arguments": {"direction": "east"}}
    assert cost == RECORDED["usage"]["cost"]
    text, _ = ask({**REQUEST, "thinking": True})
    assert json.loads(text)["thinking"] == "The square to the east is unchecked."


def test_openrouter_backend_asks_with_every_tool_and_the_key(offline, monkeypatch):
    fake = answering(monkeypatch)
    ask()
    ask({**REQUEST, "thinking": True})
    sent = fake.sent[0]
    assert sent.full_url == "https://openrouter.ai/api/v1/chat/completions"
    assert sent.get_header("Authorization") == f"Bearer {KEY}"
    body = fake.body()
    assert body["model"] == "deepseek/deepseek-chat-v3.1"
    assert body["messages"] == [
        {"role": "system", "content": "You are a pirate."},
        {"role": "user", "content": "Turn 1. What do you do?"},
    ]
    assert body["tools"] == [
        {"type": "function", "function": tool} for tool in TOOL_DEFINITIONS
    ]
    assert (body["max_tokens"], body["seed"]) == (300, 7)
    assert "reasoning" not in body
    assert fake.body(1)["reasoning"] == {"enabled": True}


def test_openrouter_backend_a_reply_with_no_tool_call_is_passed_on_to_be_refused(
    offline, monkeypatch
):
    choice = {"message": {"role": "assistant", "content": "I'd go east."}}
    answering(monkeypatch, {**RECORDED, "choices": [choice]})
    text, _ = ask()
    assert text == "I'd go east."
    with pytest.raises(BadToolCall):
        _read_reply(text)


def test_openrouter_backend_the_manifest_totals_the_reply_s_cost(
    offline, monkeypatch, capsys
):
    fake = answering(monkeypatch)
    (offline / "llm.toml").write_text(CONFIG)
    assert cli.main(["run", "llm.toml", "--seed", "1", "--no-watch", "--yes"]) == 0
    folder = offline / capsys.readouterr().out.splitlines()[-1]
    manifest = json.loads((folder / "manifest.json").read_text())
    assert fake.sent
    total = len(fake.sent) * RECORDED["usage"]["cost"]
    assert manifest["cost_usd"] == pytest.approx(total)
    assert KEY not in "".join(p.read_text() for p in folder.iterdir())


def test_openrouter_backend_a_reply_with_no_cost_stops_the_run(
    offline, monkeypatch, capsys
):
    usage = {k: v for k, v in RECORDED["usage"].items() if k != "cost"}
    fake = answering(monkeypatch, {**RECORDED, "usage": usage})
    (offline / "llm.toml").write_text(CONFIG)
    assert cli.main(["run", "llm.toml", "--seed", "1", "--no-watch", "--yes"]) == 0
    folder = offline / capsys.readouterr().out.splitlines()[-1]
    assert len(fake.sent) == 1
    last = (folder / "story.txt").read_text().splitlines()[-1]
    assert last.startswith("Game stopped:")
    assert "no cost" in last


def test_key_from_the_environment_a_missing_key_stops_the_run_before_the_game(
    offline, monkeypatch, capsys
):
    fake = FakeOpenRouter(RECORDED)
    monkeypatch.setattr(urllib.request, "urlopen", fake)

    def never_asked(question):
        raise AssertionError("asked to spend before the key was checked")

    monkeypatch.setattr("builtins.input", never_asked)
    (offline / "llm.toml").write_text(CONFIG)
    assert cli.main(["run", "llm.toml", "--seed", "1", "--no-watch"]) == 1
    assert "OPENROUTER_API_KEY" in capsys.readouterr().err
    assert fake.sent == []
    assert not (offline / "runs").exists() or not any((offline / "runs").iterdir())


def test_key_from_the_environment_env_example_names_the_key_with_no_value():
    lines = (HERE.parent / ".env.example").read_text().splitlines()
    assert "OPENROUTER_API_KEY=" in lines
