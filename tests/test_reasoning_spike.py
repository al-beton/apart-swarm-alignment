# Implements: agents/reasoning-spike
"""The reasoning-budget spike, against fake providers: no live call."""

import io
import json
import urllib.request

import pytest
from adaption.types import Response

from treasure_island import reasoning_spike
from treasure_island.reasoning_spike import HEADER, Spike, main, play

ADAPTION_REPLY = {
    "id": "resp_1",
    "object": "response",
    "status": "completed",
    "model": "deepseek-v4-flash",
    "output": [
        {"type": "reasoning", "summary": [{"type": "summary_text", "text": "Dig."}]},
        {"type": "function_call", "name": "dig", "arguments": "{}", "call_id": "c1"},
    ],
    "output_text": "",
    "usage": {
        "input_tokens": 1_000,
        "output_tokens": 200,
        "total_tokens": 1_200,
        "input_tokens_details": {"cached_tokens": 0},
        "output_tokens_details": {"reasoning_tokens": 150},
    },
}
OPENROUTER_REPLY = {
    "choices": [
        {
            "finish_reason": "tool_calls",
            "message": {
                "content": "",
                "tool_calls": [
                    {"function": {"name": "dig", "arguments": "{}"}, "id": "c1"}
                ],
            },
        }
    ],
    "usage": {"cost": 0.0001, "completion_tokens_details": {"reasoning_tokens": 90}},
}


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **arguments):
        self.calls.append(arguments)
        return Response.model_validate(ADAPTION_REPLY)


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


class FakeOpenRouter:
    def __init__(self):
        self.bodies = []

    def __call__(self, request, timeout=None):
        self.bodies.append(json.loads(request.data))
        return io.BytesIO(json.dumps(OPENROUTER_REPLY).encode())


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refused(*args, **kwargs):
        raise AssertionError("the spike tried to reach the network")

    monkeypatch.setattr(urllib.request, "urlopen", refused)


def first_adaption_call(option):
    client = FakeClient()
    play(option, 2, 512, Spike(option, client=client), cap=1.0)
    return client.responses.calls[0]


def test_reasoning_spike_each_adaption_option_sends_its_one_change():
    plain = first_adaption_call("adaption-plain")
    assert "extra_body" not in plain and "tool_choice" not in plain
    assert plain["max_output_tokens"] == 300 + 512
    assert first_adaption_call("adaption-max-tokens")["extra_body"] == {
        "reasoning": {"max_tokens": 512}
    }
    assert first_adaption_call("adaption-effort-low")["extra_body"] == {
        "reasoning": {"effort": "low"}
    }
    assert first_adaption_call("adaption-required")["tool_choice"] == "required"


def test_reasoning_spike_each_openrouter_option_sends_its_one_change(monkeypatch):
    bodies = {}
    for option in ("openrouter-max-tokens", "openrouter-required"):
        fake = FakeOpenRouter()
        monkeypatch.setattr(urllib.request, "urlopen", fake)
        play(option, 2, 512, Spike(option, key="test-key-not-real"), cap=1.0)
        bodies[option] = fake.bodies[0]
    assert bodies["openrouter-max-tokens"]["reasoning"] == {"max_tokens": 512}
    assert bodies["openrouter-max-tokens"]["tool_choice"] == "auto"
    assert bodies["openrouter-required"]["reasoning"] == {"max_tokens": 512}
    assert bodies["openrouter-required"]["tool_choice"] == "required"


def test_reasoning_spike_the_table_counts_reasoning_tool_calls_and_cost():
    line = play(
        "adaption-plain", 3, 512, Spike("adaption-plain", client=FakeClient()), 1.0
    )
    one = (1_000 * 0.044 + 200 * 0.133) / 1_000_000
    assert line == f"| adaption-plain | 512 | 150 | 150 | 3/3 | {3 * one:.5f} |"
    assert HEADER.count("|---") == line.count("|") - 1


def test_reasoning_spike_spends_nothing_without_a_yes(monkeypatch, capsys):
    def never(option):
        raise AssertionError("a provider was set up without a yes")

    monkeypatch.setattr(reasoning_spike, "_spike_for", never)
    assert main(["--turns", "1"], ask=lambda question: "no") == 1
    assert "Nothing was spent" in capsys.readouterr().err
