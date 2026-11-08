# Implements: agents/reasoning-spike, treasure-island/model-reasoning
"""The reasoning-budget experiment and the budget a model is told, offline."""

import json

from adaption.types import Response

from treasure_island import openrouter, saved_game
from treasure_island.adaption_backend import AdaptionBackend
from treasure_island.brain import budget_sentence, system_prompt
from treasure_island.config import parse_config
from treasure_island.reasoning_spike import HEADER, main

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


def test_model_reasoning_the_prompt_tells_a_reasoning_model_its_exact_budget():
    told = system_prompt(config(thinking_tokens=2048, failed_tries=3))
    assert told.endswith(
        "# Thinking\n- You have exactly 2048 tokens to think. If you reach 2048 "
        "tokens without making a tool call, your answer is cut off, you're told so "
        "and asked again; after 3 failed tries your turn passes."
    )


def test_model_reasoning_the_budget_told_is_the_cap_sent(tmp_path):
    client = FakeClient()
    played(tmp_path, client, thinking_tokens=2048, reply_tokens=300)
    sent = client.responses.calls[0]
    assert budget_sentence(config(thinking_tokens=2048)) in sent["instructions"]
    assert "exactly 2048 tokens" in sent["instructions"]
    assert sent["max_output_tokens"] == 2048 + 300  # no hidden headroom


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


class Backend:
    """The game's own Adaption backend, over a fake client."""

    def __init__(self):
        self.client = FakeClient()
        self._backend = AdaptionBackend(MODEL, self.client)

    def __call__(self, request):
        return self._backend(request)


def test_reasoning_spike_plays_each_budget_with_and_without_the_sentence(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.chdir(tmp_path)
    backend = Backend()
    assert main(["--turns", "2", "--yes"], backend=backend) == 0
    calls = backend.client.responses.calls
    sent = {(c["max_output_tokens"], "# Thinking" in c["instructions"]) for c in calls}
    assert sent == {(b + 300, s) for b in (1024, 2048, 4096) for s in (True, False)}
    assert not (tmp_path / "runs").exists()  # it keeps no run


def test_reasoning_spike_the_table_reads_each_game_s_record(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.chdir(tmp_path)
    backend = Backend()
    backend.client.responses.replies = [reply(4096, cut_off=True), reply(100)]
    main(["--turns", "2", "--budgets", "1024", "--yes"], backend=backend)
    out = capsys.readouterr().out
    assert HEADER in out
    one = (1_000 * 0.044 + 200 * 0.133) / 1_000_000
    with_sentence = next(
        line for line in out.splitlines() if line.startswith("| 1024 | yes")
    )
    assert with_sentence == f"| 1024 | yes | 2173 | 4196 | 1 | 1 | 0 | {3 * one:.5f} |"


def test_reasoning_spike_spends_nothing_without_a_yes(monkeypatch, capsys):
    def never(model):
        raise AssertionError("a backend was made without a yes")

    from treasure_island import reasoning_spike

    monkeypatch.setattr(reasoning_spike, "backend_for", never)
    assert main(["--turns", "1"], ask=lambda question: "no") == 1
    assert "Nothing was spent" in capsys.readouterr().err
