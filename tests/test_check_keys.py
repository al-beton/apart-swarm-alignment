# Implements: agents/check-keys
"""`check-keys` against a recorded OpenRouter key reply, with no network.

`openrouter-key.json` follows the reply OpenRouter's API reference documents for
`GET /api/v1/key`, not a live call. Its `label` is the key masked, as OpenRouter
shows it, which is why the command never prints the label.
"""

import io
import json
import socket
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from treasure_island import cli

HERE = Path(__file__).parent
RECORDED = json.loads((HERE / "openrouter-key.json").read_text())
KEY = "sk-or-v1-abc123notarealkey0009xyz"


class FakeOpenRouter:
    """Stands in for `urllib.request.urlopen`: keeps each request, then answers."""

    def __init__(self, status=200, reply=RECORDED):
        self.status = status
        self.reply = reply
        self.sent = []

    def __call__(self, request, timeout=None):
        self.sent.append(request)
        body = io.BytesIO(json.dumps(self.reply).encode())
        if self.status != 200:
            raise urllib.error.HTTPError(
                request.full_url, self.status, "Unauthorized", {}, body
            )
        return body


@pytest.fixture
def offline(monkeypatch):
    """No sockets, and only the key a test sets."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    def no_network(*args, **kwargs):
        raise AssertionError("a socket was opened")

    monkeypatch.setattr(socket, "socket", no_network)


def checked(monkeypatch, capsys, fake, key=KEY):
    if key:
        monkeypatch.setenv("OPENROUTER_API_KEY", key)
    monkeypatch.setattr(urllib.request, "urlopen", fake)
    code = cli.main(["check-keys"])
    return code, capsys.readouterr().out


def test_check_keys_a_working_key_says_what_it_has_spent_and_its_limit(
    offline, monkeypatch, capsys
):
    code, out = checked(monkeypatch, capsys, FakeOpenRouter())
    assert code == 0
    (line,) = [line for line in out.splitlines() if "OPENROUTER_API_KEY" in line]
    assert "works" in line
    assert "$25.50" in line
    assert "$100.00" in line
    no_limit = {"data": {**RECORDED["data"], "limit": None, "limit_remaining": None}}
    code, out = checked(monkeypatch, capsys, FakeOpenRouter(reply=no_limit))
    assert code == 0
    assert "no limit" in out


def test_check_keys_a_rejected_key_fails(offline, monkeypatch, capsys):
    error = {"error": {"code": 401, "message": "User not found."}}
    code, out = checked(monkeypatch, capsys, FakeOpenRouter(401, error))
    assert code == 1
    assert "rejected" in out
    assert "401" in out


def test_check_keys_a_missing_key_is_said_and_doesn_t_fail(
    offline, monkeypatch, capsys
):
    fake = FakeOpenRouter()
    code, out = checked(monkeypatch, capsys, fake, key=None)
    assert code == 0
    assert "OPENROUTER_API_KEY isn't set" in out
    assert fake.sent == []


def test_check_keys_never_prints_any_part_of_a_key(offline, monkeypatch, capsys):
    for fake in (FakeOpenRouter(), FakeOpenRouter(401, {"error": {"code": 401}})):
        _, out = checked(monkeypatch, capsys, fake)
        assert RECORDED["data"]["label"] not in out
        for start in range(len(KEY) - 5):
            assert KEY[start : start + 6] not in out


def test_check_keys_asks_no_model_anything(offline, monkeypatch, capsys):
    fake = FakeOpenRouter()
    checked(monkeypatch, capsys, fake)
    (sent,) = fake.sent
    assert sent.full_url == "https://openrouter.ai/api/v1/key"
    assert sent.get_method() == "GET"
    assert sent.data is None
    assert sent.get_header("Authorization") == f"Bearer {KEY}"
