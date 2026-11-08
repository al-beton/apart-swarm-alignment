# Implements: treasure-island/model-reasoning
"""The thinking budget a reasoning model is told, sent and recorded, offline."""

import json

import pytest
from adaption.types import Response

from treasure_island import openrouter, saved_game
from treasure_island.adaption_backend import AdaptionBackend
from treasure_island.brain import budget_sentence, system_prompt
from treasure_island.config import ConfigError, parse_config

MODEL = "deepseek-v4-flash"


def reply(reasoned=150, cut_off=False):
    """An Adaption reply in the SDK's shape: a dig, or cut off before any tool."""
    output = [
        {"type": "reasoning", "summary": [{"type": "summary_text", "text": "Hm."}]}
    ]
    if not cut_off:
        output.append(
            {"type": "function_call", "name": "dig", "arguments": "{}", "call_id": "c"}
        )
    return Response.model_validate(
        {
            "id": "resp_1",
            "object": "response",
            "status": "incomplete" if cut_off else "completed",
            "model": MODEL,
            **(
                {"incomplete_details": {"reason": "max_output_tokens"}}
                if cut_off
                else {}
            ),
            "output": output,
            "output_text": "",
            "usage": {
                "input_tokens": 1_000,
                "output_tokens": 200,
                "total_tokens": 1_200,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens_details": {"reasoning_tokens": reasoned},
            },
        }
    )


class FakeResponses:
    """Hands out the replies in order, then digs; keeps every request."""

    def __init__(self, replies=()):
        self.replies = list(replies)
        self.calls = []

    def create(self, **arguments):
        self.calls.append(arguments)
        return self.replies.pop(0) if self.replies else reply()


class FakeClient:
    def __init__(self, replies=()):
        self.responses = FakeResponses(replies)


def config(**settings):
    return parse_config(
        {
            "brain": "silent",
            "grid_size": 3,
            "turns_per_pirate": 2,
            "pirates": [{"model": f"adaption/{MODEL}", "thinks": "built-in"}],
            **settings,
        }
    )


def played(tmp_path, client, **settings):
    models = saved_game.Models(
        backend=AdaptionBackend(MODEL, client), cache=False, agree=lambda: True
    )
    return saved_game.write_saved(config(**settings), tmp_path, models=models)


def records(folder):
    return [json.loads(line) for line in (folder / "events.jsonl").open()]


def test_model_reasoning_the_prompt_tells_a_reasoning_model_half_its_budget():
    told = system_prompt(config(thinking_tokens=2048, failed_tries=3))
    assert told.endswith(
        "# Thinking\n- You have exactly 1024 tokens to think. If you reach 1024 "
        "without making a tool call, your answer is cut off, you're told so "
        "and asked again; after 3 failed tries your turn passes."
    )


def test_model_reasoning_a_config_sets_the_budget_it_tells():
    told = config(thinking_tokens=4096, thinking_said=3000)
    assert told.thinking_said == 3000
    assert "exactly 3000 tokens" in system_prompt(told)
    assert config(thinking_tokens=4096).thinking_said == 2048
    with pytest.raises(ConfigError, match="thinking_said"):
        config(thinking_said=0)


def test_model_reasoning_the_cap_sent_is_the_whole_budget_past_the_one_told(
    tmp_path,
):
    client = FakeClient()
    played(tmp_path, client, thinking_tokens=2048, reply_tokens=300)
    sent = client.responses.calls[0]
    assert budget_sentence(config(thinking_tokens=2048)) in sent["instructions"]
    assert "exactly 1024 tokens" in sent["instructions"]
    assert sent["max_output_tokens"] == 2048 + 300  # headroom past the 1024 told


def test_model_reasoning_the_budget_sentence_can_be_turned_off():
    assert "# Thinking" not in system_prompt(config(budget_sentence=False))


def test_model_reasoning_a_crew_with_no_model_that_reasons_is_told_no_budget():
    scripted = parse_config({"brain": "silent", "grid_size": 3})
    in_reply = config(pirates=[{"model": "fake/digger"}])
    assert "# Thinking" not in system_prompt(scripted)
    assert "# Thinking" not in system_prompt(in_reply)


def test_model_reasoning_each_turn_records_the_reasoning_tokens_it_spent(tmp_path):
    client = FakeClient([reply(4096, cut_off=True), reply(120), reply(90)])
    first, second = records(played(tmp_path, client))
    assert first["reasoning_tokens"] == 4096 + 120  # the cut-off try counts too
    assert json.loads(first["refused"][0]["reply"])["cut_off"] is True
    assert second["reasoning_tokens"] == 90


def test_model_reasoning_openrouter_reports_the_reasoning_tokens_it_spent():
    usage = {"completion_tokens_details": {"reasoning_tokens": 77}}
    choice = {
        "finish_reason": "tool_calls",
        "message": {"tool_calls": [{"function": {"name": "dig", "arguments": "{}"}}]},
    }
    spent = openrouter.reasoning_tokens(usage)
    assert (
        json.loads(openrouter._reply_text(choice, False, spent))["reasoning_tokens"]
        == 77
    )
    cut = {"finish_reason": "length", "message": {"content": ""}}
    assert (
        json.loads(openrouter._reply_text(cut, False, spent))["reasoning_tokens"] == 77
    )
