# Implements: treasure-island/model-reasoning, agents/model-per-pirate, agents/one-request-per-turn, agents/reply-is-a-tool-call, agents/ask-once-more, agents/reply-cap, agents/plays-then-replays, treasure-island/thinking, treasure-island/model-backends, runs/cache-across-runs, runs/no-cache
"""An LLM pirate plays through a backend, and its game replays with no backend."""

import json

import pytest

from treasure_island import cli, saved_game
from treasure_island.backends import BACKENDS, UnknownModel, thinking_way
from treasure_island.brain import TOOLS, PirateSeat, system_prompt
from treasure_island.config import ConfigError, load_config, parse_config, save_config
from treasure_island.event_log import log_errors
from treasure_island.game_loop import Game
from treasure_island.llm import TOOL_DEFINITIONS, LLMPirate
from treasure_island.runs import Replies
from treasure_island.saved_game import Models
from treasure_island.strategies import Silent, brains_for

DIG = json.dumps({"tool": "dig", "arguments": {}})
CONFIG = """
grid_size = 3
turns_per_pirate = 3
brain = "silent"

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


def yes():
    return True


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
    config = parse_config({"brain": "silent", "pirates": [{"model": "fake/a"}, {}]})
    brains = brains_for(config.brain, config, Replies(tmp_path / "r.jsonl"))
    assert isinstance(brains[0], LLMPirate)
    assert isinstance(brains[1], Silent)


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
        "thinking_tokens",
    }
    assert request["system"] == system_prompt(llm_config())
    (message,) = request["messages"]
    assert message["role"] == "user"
    assert "(0, 0)" in message["content"]
    assert request["system"] not in message["content"]
    assert request["tools"] == TOOL_DEFINITIONS


def test_one_request_per_turn_the_tools_are_function_definitions():
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


def first_turns(model, tmp_path, **settings):
    """Play a one-pirate LLM game through `model`; return its records."""
    config = llm_config(**settings)
    replies = Replies(tmp_path / "replies.jsonl", backend=model)
    return list(Game(config, brains_for("s-sweep", config, replies)).records())


def test_ask_once_more_a_bad_reply_is_recorded_and_the_pirate_is_told_why(tmp_path):
    model = FakeModel("let me think", DIG)
    first = first_turns(model, tmp_path)[0]
    assert first["did"] == [{"action": "dig"}]
    assert [r["reply"] for r in first["refused"]] == ["let me think"]
    why = first["refused"][0]["why"]
    assert why in model.requests[1]["messages"][0]["content"]
    assert "didn't use your turn" in model.requests[1]["messages"][0]["content"]


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


def test_ask_once_more_after_failed_tries_bad_replies_the_turn_passes(tmp_path):
    model = FakeModel("no idea")
    first = first_turns(model, tmp_path, turns_per_pirate=2)[0]
    assert first["did"] == []
    assert first["outcome"]["position"] == first["saw"]["position"]
    assert [r["reply"] for r in first["refused"]] == ["no idea", "no idea"]
    assert "passed" in first["story"]
    assert len(model.requests) == 2 * 2


def test_ask_once_more_failed_tries_sets_how_many_bad_replies_a_turn_takes(tmp_path):
    model = FakeModel("no idea")
    first_turns(model, tmp_path, turns_per_pirate=2, failed_tries=3)
    assert len(model.requests) == 2 * 3


def test_ask_once_more_a_bad_reply_and_a_failed_move_share_a_turn_s_tries(tmp_path):
    off_the_edge = json.dumps({"tool": "move", "arguments": {"direction": "north"}})
    model = FakeModel("no idea", off_the_edge, DIG)
    first = first_turns(model, tmp_path)[0]
    assert first["did"] == []
    assert first["failed_moves"] == [{"action": "move", "direction": "north"}]
    assert len(first["refused"]) == 1
    assert "passed" in first["story"]


def test_reply_cap_defaults_to_300_tokens_and_a_config_can_set_it(tmp_path):
    model = FakeModel()
    one_turn(model, tmp_path=tmp_path)
    assert model.requests[0]["max_tokens"] == 300
    assert parse_config({"reply_tokens": 50}).reply_tokens == 50
    with pytest.raises(ConfigError, match="reply_tokens"):
        parse_config({"reply_tokens": 0})


def test_thinking_is_on_by_default_and_a_config_can_turn_it_off(tmp_path):
    answer = json.dumps({"tool": "dig", "arguments": {}, "thinking": "hmm"})
    assert llm_config().thinking is True
    model = FakeModel(answer)
    decision, _ = one_turn(model, llm_config(thinking=False), tmp_path)
    assert model.requests[0]["thinking"] is False
    assert model.requests[0]["thinking_tokens"] == 0
    assert decision.thinking is None


def test_thinking_is_kept_for_the_record(tmp_path):
    answer = json.dumps({"tool": "dig", "arguments": {}, "thinking": "corner first"})
    model = FakeModel(answer)
    decision, _ = one_turn(model, tmp_path=tmp_path)
    assert model.requests[0]["thinking"] is True
    assert decision.thinking == "corner first"


def test_model_reasoning_each_backend_says_which_way_its_models_think():
    for prefix in BACKENDS:
        assert thinking_way(f"{prefix}some-model") in ("built-in", "in-reply")
    assert thinking_way("openrouter/some-model") == "built-in"
    assert thinking_way("adaption/some-model") == "built-in"


def ask_as(model_name, tmp_path, **settings):
    """The request an LLM pirate playing `model_name` sends on its first turn."""
    model = FakeModel()
    config = llm_config(**settings)
    replies = Replies(tmp_path / "replies.jsonl", backend=model)
    PirateSeat(
        "pirate-1", LLMPirate("pirate-1", model_name, replies, config), config
    ).take_turn((0, 0), 3)
    return model.requests[0]


def test_model_reasoning_a_model_that_reasons_gets_the_thinking_budget(tmp_path):
    assert llm_config().thinking_tokens == 1024
    request = ask_as("openrouter/some-model", tmp_path)
    assert request["thinking_tokens"] == 1024
    assert "thought" not in request["messages"][0]["content"]
    assert ask_as("openrouter/m", tmp_path, thinking_tokens=64)["thinking_tokens"] == 64
    with pytest.raises(ConfigError, match="thinking_tokens"):
        parse_config({"thinking_tokens": 0})


def test_model_reasoning_a_model_without_it_writes_a_short_thought(tmp_path):
    request = ask_as("fake/digger", tmp_path)
    assert request["thinking_tokens"] == 0
    assert '"thinking"' in request["messages"][0]["content"]
    off = ask_as("fake/digger", tmp_path, thinking=False)
    assert '"thinking"' not in off["messages"][0]["content"]


@pytest.fixture
def toml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "mixed.toml"
    path.write_text(CONFIG)
    return path


def test_plays_then_replays_a_whole_game_through_a_fake_backend(toml, tmp_path):
    model = FakeModel()
    folder = saved_game.play_saved(toml, 4, models=Models(model, agree=yes))
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
        saved_game.play_saved(toml, 4, models=Models(agree=yes))


def test_cache_across_runs_a_second_llm_game_asks_the_model_nothing(toml):
    first = saved_game.play_saved(toml, 4, models=Models(FakeModel(), agree=yes))
    model = FakeModel()
    second = saved_game.play_saved(toml, 4, models=Models(model, agree=yes))
    assert model.requests == []
    assert (second / "events.jsonl").read_bytes() == (
        first / "events.jsonl"
    ).read_bytes()
    assert saved_game.differences(second) == []


def test_no_cache_an_llm_game_asks_the_model_again(toml):
    saved_game.play_saved(toml, 4, models=Models(FakeModel(), agree=yes))
    model = FakeModel()
    saved_game.play_saved(toml, 4, models=Models(model, cache=False, agree=yes))
    assert model.requests


def test_model_backends_a_config_names_each_pirate_s_model(toml):
    config = load_config(toml)
    assert [pirate.model for pirate in config.pirates] == ["fake/digger", None]
