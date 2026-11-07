# Implements: agents/model-per-pirate, agents/one-request-per-turn, agents/reply-is-a-tool-call, agents/ask-once-more, agents/reply-cap, agents/plays-then-replays, treasure-island/thinking, treasure-island/model-backends, runs/cache-across-runs, runs/no-cache
"""An LLM pirate plays through a backend, and its game replays with no backend."""

import json

import pytest

from treasure_island import cli, saved_game
from treasure_island.backends import UnknownModel
from treasure_island.brain import TOOLS, PirateSeat, system_prompt
from treasure_island.config import ConfigError, load_config, parse_config, save_config
from treasure_island.event_log import log_errors
from treasure_island.game_loop import Game
from treasure_island.llm import TOOL_DEFINITIONS, LLMPirate
from treasure_island.runs import Replies
from treasure_island.saved_game import Models
from treasure_island.strategies import Sweeper, brains_for

DIG = json.dumps({"tool": "dig", "arguments": {}})
CONFIG = """
grid_size = 3
turns_per_pirate = 3
landing_square = [0, 0]
brain = "s-sweep"

[[pirates]]
model = "fake/digger"

[[pirates]]
"""


class FakeModel:
    """A backend that answers from a list, then repeats the last answer."""

    def __init__(self, *answers):
        self.answers = list(answers or [DIG])
        self.requests = []

    def __call__(self, request):
        self.requests.append(request)
        answer = self.answers.pop(0) if len(self.answers) > 1 else self.answers[0]
        return answer, 0.001


def llm_config(**settings):
    return parse_config(
        {
            "grid_size": 3,
            "turns_per_pirate": 3,
            "pirates": [{"model": "fake/digger"}],
            **settings,
        }
    )


def one_turn(model, config=None, tmp_path=None, name="pirate-1"):
    """Ask an LLM pirate for one decision through `model`; return it and the view."""
    config = config or llm_config()
    replies = Replies(tmp_path / "replies.jsonl", backend=model)
    pirate = LLMPirate(name, "fake/digger", replies, config)
    seat = PirateSeat(name, pirate, config)
    return seat.take_turn((0, 0), 3), pirate


def test_model_per_pirate_a_pirate_with_a_model_gets_the_llm_brain(tmp_path):
    config = parse_config({"brain": "s-sweep", "pirates": [{"model": "fake/a"}, {}]})
    brains = brains_for(config.brain, config, Replies(tmp_path / "r.jsonl"))
    assert isinstance(brains[0], LLMPirate)
    assert isinstance(brains[1], Sweeper)


def test_model_per_pirate_the_model_is_saved_with_the_config(tmp_path):
    config = parse_config({"pirates": [{"model": "fake/a"}, {}]})
    save_config(config, tmp_path / "config.json")
    again = parse_config(json.loads((tmp_path / "config.json").read_text()))
    assert [pirate.model for pirate in again.pirates] == ["fake/a", None]


def test_model_per_pirate_a_model_must_be_text():
    with pytest.raises(ConfigError, match="model"):
        parse_config({"pirates": [{"model": 3}]})


def test_one_request_per_turn_holds_only_the_prompt_the_turn_and_the_tools(tmp_path):
    model = FakeModel()
    one_turn(model, tmp_path=tmp_path)
    (request,) = model.requests
    assert set(request) == {
        "agent",
        "model",
        "seed",
        "system",
        "messages",
        "tools",
        "max_tokens",
        "thinking",
    }
    assert request["system"] == system_prompt(llm_config())
    (message,) = request["messages"]
    assert message["role"] == "user"
    assert "(0, 0)" in message["content"]
    assert request["system"] not in message["content"]
    assert request["tools"] == TOOL_DEFINITIONS


def test_one_request_per_turn_the_four_tools_are_function_definitions():
    assert [tool["name"] for tool in TOOL_DEFINITIONS] == [t["name"] for t in TOOLS]
    for tool in TOOL_DEFINITIONS:
        schema = tool["parameters"]
        assert tool["description"]
        assert schema["type"] == "object"
        assert sorted(schema["required"]) == sorted(schema["properties"])
    move = TOOL_DEFINITIONS[0]["parameters"]["properties"]["direction"]
    assert move["enum"] == ["north", "east", "south", "west"]


def test_reply_is_a_tool_call_becomes_the_action(tmp_path):
    answer = json.dumps({"tool": "move", "arguments": {"direction": "east"}})
    decision, _ = one_turn(FakeModel(answer), tmp_path=tmp_path)
    assert decision.action == {"action": "move", "direction": "east"}
    assert decision.refused == ()


def test_ask_once_more_a_bad_reply_is_recorded_and_the_pirate_is_told_why(tmp_path):
    model = FakeModel("let me think", DIG)
    decision, _ = one_turn(model, tmp_path=tmp_path)
    assert decision.action == {"action": "dig"}
    assert [r["reply"] for r in decision.refused] == ["let me think"]
    first, again = model.requests
    assert again["messages"][:2] == [
        first["messages"][0],
        {"role": "assistant", "content": "let me think"},
    ]
    told = again["messages"][2]
    assert told["role"] == "user"
    assert decision.refused[0]["why"] in told["content"]


@pytest.mark.parametrize(
    "bad",
    [
        "not json",
        json.dumps(["dig"]),
        json.dumps({"tool": "teleport", "arguments": {}}),
        json.dumps({"tool": "move", "arguments": {"direction": "up"}}),
        json.dumps({"tool": "dig"}),
    ],
)
def test_ask_once_more_every_kind_of_bad_reply_gets_a_reason(bad, tmp_path):
    decision, _ = one_turn(FakeModel(bad, DIG), tmp_path=tmp_path)
    assert decision.refused[0]["why"]


def test_ask_once_more_a_second_bad_reply_passes_the_turn(tmp_path):
    model = FakeModel("no idea")
    config = llm_config(turns_per_pirate=2)
    replies = Replies(tmp_path / "replies.jsonl", backend=model)
    records = list(Game(config, brains_for("s-sweep", config, replies)).records())
    first = records[0]
    assert first["did"] == []
    assert first["outcome"]["position"] == first["saw"]["position"]
    assert [r["reply"] for r in first["refused"]] == ["no idea", "no idea"]
    assert "passed" in first["story"]
    assert len(model.requests) == 2 * 2


def test_reply_cap_defaults_to_300_tokens_and_a_config_can_set_it(tmp_path):
    model = FakeModel()
    one_turn(model, tmp_path=tmp_path)
    assert model.requests[0]["max_tokens"] == 300
    assert parse_config({"reply_tokens": 50}).reply_tokens == 50
    with pytest.raises(ConfigError, match="reply_tokens"):
        parse_config({"reply_tokens": 0})


def test_thinking_is_off_by_default_and_a_reply_s_reasoning_is_dropped(tmp_path):
    answer = json.dumps({"tool": "dig", "arguments": {}, "thinking": "hmm"})
    model = FakeModel(answer)
    decision, _ = one_turn(model, tmp_path=tmp_path)
    assert llm_config().thinking is False
    assert model.requests[0]["thinking"] is False
    assert decision.thinking is None


def test_thinking_when_turned_on_is_kept_for_the_record(tmp_path):
    answer = json.dumps({"tool": "dig", "arguments": {}, "thinking": "corner first"})
    model = FakeModel(answer)
    decision, _ = one_turn(model, llm_config(thinking=True), tmp_path)
    assert model.requests[0]["thinking"] is True
    assert decision.thinking == "corner first"


@pytest.fixture
def toml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "mixed.toml"
    path.write_text(CONFIG)
    return path


def test_plays_then_replays_a_whole_game_through_a_fake_backend(toml, tmp_path):
    model = FakeModel()
    folder = saved_game.play_saved(toml, 4, models=Models(model))
    assert model.requests
    assert log_errors(folder / "events.jsonl") == []
    assert (folder / "replies.jsonl").read_text().count("\n") == len(model.requests)
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["cache_misses"] == len(model.requests)
    assert manifest["cost_usd"] == pytest.approx(0.001 * len(model.requests))
    assert saved_game.differences(folder) == []
    assert cli.main(["replay", str(folder)]) == 0


def test_plays_then_replays_with_no_backend_a_missing_reply_spends_nothing(toml):
    with pytest.raises(UnknownModel):
        saved_game.play_saved(toml, 4)


def test_cache_across_runs_a_second_llm_game_asks_the_model_nothing(toml):
    first = saved_game.play_saved(toml, 4, models=Models(FakeModel()))
    model = FakeModel()
    second = saved_game.play_saved(toml, 4, models=Models(model))
    assert model.requests == []
    assert (second / "events.jsonl").read_bytes() == (
        first / "events.jsonl"
    ).read_bytes()
    assert saved_game.differences(second) == []


def test_no_cache_an_llm_game_asks_the_model_again(toml):
    saved_game.play_saved(toml, 4, models=Models(FakeModel()))
    model = FakeModel()
    saved_game.play_saved(toml, 4, models=Models(model, cache=False))
    assert model.requests


def test_model_backends_a_config_names_each_pirate_s_model(toml):
    config = load_config(toml)
    assert [pirate.model for pirate in config.pirates] == ["fake/digger", None]
