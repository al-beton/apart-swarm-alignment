# Implements: agents/adaption-backend, agents/adaption-cost, agents/key-from-the-environment, agents/check-keys, agents/normal-temperature
"""The Adaption backend, tested against a reply in the SDK's own shape, offline."""

import json
from pathlib import Path

import adaption
import httpx
import pytest
from adaption.types import ModelListResponse, Response

from treasure_island import adaption_backend, cli, saved_game
from treasure_island.adaption_backend import RATES, AdaptionBackend
from treasure_island.backends import MissingKey, UnknownModel, backend_for, price_for
from treasure_island.keys import check_keys
from treasure_island.llm import TOOL_DEFINITIONS
from treasure_island.saved_game import Models

ROOT = Path(__file__).resolve().parents[1]
MODEL = "deepseek-v4-flash"
# A reply as the Responses API returns it, written out by hand: no live call.
RECORDED = {
    "id": "resp_1",
    "object": "response",
    "status": "completed",
    "model": MODEL,
    "output": [
        {"type": "reasoning", "summary": [{"type": "summary_text", "text": "Dig."}]},
        {
            "type": "function_call",
            "name": "move",
            "arguments": '{"direction": "east"}',
            "call_id": "call_1",
        },
    ],
    "output_text": "",
    "usage": {"input_tokens": 2_000, "output_tokens": 100, "total_tokens": 2_100},
}
REQUEST = {
    "agent": "pirate-1",
    "model": f"adaption/{MODEL}",
    "seed": 0,
    "system": "the rules",
    "messages": [
        {"role": "user", "content": "your turn"},
        {"role": "assistant", "content": "hmm"},
        {"role": "user", "content": "That isn't a tool call."},
    ],
    "tools": TOOL_DEFINITIONS,
    "max_tokens": 300,
    "thinking": False,
}


class FakeResponses:
    def __init__(self, reply):
        self.reply = reply
        self.calls = []

    def create(self, **arguments):
        self.calls.append(arguments)
        return Response.model_validate(self.reply)


class FakeClient:
    def __init__(self, reply=RECORDED):
        self.responses = FakeResponses(reply)


def answer(reply=RECORDED, request=REQUEST):
    client = FakeClient(reply)
    text, cost = AdaptionBackend(MODEL, client)(request)
    return json.loads(text), cost, client.responses.calls[0]


@pytest.fixture
def key(monkeypatch):
    monkeypatch.setenv("ADAPTION_API_KEY", "test-key-not-real")


def test_adaption_backend_serves_models_named_adaption_slash_id(key):
    assert isinstance(backend_for(f"adaption/{MODEL}"), AdaptionBackend)
    with pytest.raises(UnknownModel):
        backend_for("elsewhere/some-model")


def test_adaption_backend_sends_the_rules_the_turn_and_every_tool_as_a_function():
    _, _, sent = answer()
    assert sent["model"] == MODEL
    assert sent["instructions"] == "the rules"
    assert sent["input"] == REQUEST["messages"]
    assert sent["max_output_tokens"] == 300
    assert [tool["type"] for tool in sent["tools"]] == ["function"] * len(
        TOOL_DEFINITIONS
    )
    assert [tool["name"] for tool in sent["tools"]] == [
        tool["name"] for tool in TOOL_DEFINITIONS
    ]
    assert sent["tools"][0]["parameters"] == TOOL_DEFINITIONS[0]["parameters"]


def test_adaption_backend_turns_a_function_call_into_the_reply_the_brain_reads():
    reply, _, _ = answer()
    assert reply == {"tool": "move", "arguments": {"direction": "east"}}


def test_adaption_backend_passes_the_reasoning_on_only_when_thinking_is_on():
    reply, _, _ = answer(request={**REQUEST, "thinking": True})
    assert reply["thinking"] == "Dig."


def test_adaption_backend_a_reply_with_no_tool_call_comes_back_as_its_words():
    words = {
        **RECORDED,
        "output": [{"type": "message", "role": "assistant", "content": []}],
        "output_text": "I would rather not.",
    }
    client = FakeClient(words)
    text, _ = AdaptionBackend(MODEL, client)(REQUEST)
    assert text == "I would rather not."


def test_adaption_cost_comes_from_token_usage_at_the_listed_rate():
    _, cost, _ = answer()
    per_input, per_output = RATES[MODEL]
    assert cost == pytest.approx((2_000 * per_input + 100 * per_output) / 1_000_000)
    assert RATES[MODEL] == (0.044, 0.133)


def test_adaption_cost_its_rate_prices_a_run_before_it_starts():
    assert price_for(f"adaption/{MODEL}") == RATES[MODEL]
    assert price_for("adaption/some-unlisted-model") is None


def test_adaption_cost_a_model_with_no_listed_rate_is_refused(key):
    with pytest.raises(UnknownModel, match="rate"):
        backend_for("adaption/some-unlisted-model")


def test_adaption_cost_is_totalled_in_the_manifest(tmp_path, monkeypatch, key):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(adaption_backend, "client", lambda key: FakeClient(DIGS))
    path = tmp_path / "adaption.toml"
    path.write_text(CONFIG)
    folder = saved_game.play_saved(path, 0, models=Models(agree=lambda: True))
    manifest = json.loads((folder / "manifest.json").read_text())
    replies = (folder / "replies.jsonl").read_text().splitlines()
    assert len(replies) == 2  # one pirate, two turns, every reply a tool call
    one = (2_000 * 0.044 + 100 * 0.133) / 1_000_000
    assert manifest["cost_usd"] == pytest.approx(one * len(replies))
    assert "test-key-not-real" not in "".join(
        file.read_text() for file in folder.iterdir()
    )


def test_adaption_cost_a_reply_with_no_usage_stops_the_run(tmp_path, monkeypatch, key):
    monkeypatch.chdir(tmp_path)
    client = FakeClient({**DIGS, "usage": None})
    monkeypatch.setattr(adaption_backend, "client", lambda key: client)
    path = tmp_path / "adaption.toml"
    path.write_text(CONFIG)
    folder = saved_game.play_saved(path, 0, models=Models(agree=lambda: True))
    assert len(client.responses.calls) == 1
    last = (folder / "story.txt").read_text().splitlines()[-1]
    assert last.startswith("Game stopped:")
    assert "no token usage" in last
    assert saved_game.differences(folder) == []


DIGS = {
    **RECORDED,
    "output": [{"type": "function_call", "name": "dig", "arguments": "{}"}],
}
CONFIG = f"""
grid_size = 2
turns_per_pirate = 2
brain = "silent"

[[pirates]]
model = "adaption/{MODEL}"
"""


def test_key_from_the_environment_an_adaption_run_without_its_key_stops_first(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.delenv("ADAPTION_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "adaption.toml"
    path.write_text(CONFIG)
    with pytest.raises(MissingKey, match="ADAPTION_API_KEY"):
        saved_game.play_saved(path, 0)
    assert not Path("runs").exists()
    assert cli.main(["run", str(path), "--seed", "0", "--no-watch"]) == 1
    assert "ADAPTION_API_KEY" in capsys.readouterr().err


def test_key_from_the_environment_env_example_names_the_adaption_key():
    lines = (ROOT / ".env.example").read_text().splitlines()
    assert "ADAPTION_API_KEY=" in lines


HOSTED = {
    "object": "list",
    "data": [
        {"id": MODEL, "created": 0, "object": "model", "owned_by": "adaption"},
        {"id": "some-other-model", "created": 0, "object": "model", "owned_by": "x"},
    ],
}


class FakeModels:
    def __init__(self, answer):
        self.answer = answer
        self.asked = []

    def list(self, **arguments):
        self.asked.append(arguments)
        if isinstance(self.answer, Exception):
            raise self.answer
        return ModelListResponse.model_validate(self.answer)


class KeyClient:
    """A client that only lists models: a key check must never ask one anything."""

    def __init__(self, answer=HOSTED):
        self.models = FakeModels(answer)


def refused(status):
    request = httpx.Request("GET", "https://example.invalid/models")
    return httpx.Response(status, request=request)


def checked(monkeypatch, answer):
    client = KeyClient(answer)
    monkeypatch.setattr(adaption_backend, "client", lambda key: client)
    return adaption_backend.check_key("test-key-not-real"), client


def test_check_keys_an_adaption_key_that_works_says_what_it_can_use(monkeypatch):
    (works, said), client = checked(monkeypatch, HOSTED)
    assert works
    assert "2 hosted models" in said and "1 of them priced" in said
    assert client.models.asked == [{"type": "hosted"}]


def test_check_keys_an_adaption_key_that_is_rejected_fails(monkeypatch):
    error = adaption.AuthenticationError("no", response=refused(401), body=None)
    (works, said), _ = checked(monkeypatch, error)
    assert not works
    assert "rejected" in said and "401" in said


def test_check_keys_an_adaption_key_that_cannot_be_checked_fails(monkeypatch):
    error = adaption.APIConnectionError(request=refused(500).request)
    (works, said), _ = checked(monkeypatch, error)
    assert not works
    assert "couldn't be checked" in said


def test_check_keys_lists_adaption_and_never_prints_its_key(monkeypatch):
    monkeypatch.setattr(adaption_backend, "client", lambda key: KeyClient())
    lines, failed = check_keys({"ADAPTION_API_KEY": "test-key-not-real"})
    (line,) = [line for line in lines if line.startswith("adaption:")]
    assert "works" in line
    assert not failed
    assert all("test-key-not-real" not in line for line in lines)


def test_normal_temperature_adaption_sends_no_temperature():
    _, _, sent = answer()
    assert "temperature" not in sent
