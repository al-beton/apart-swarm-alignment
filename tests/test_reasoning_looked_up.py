# Implements: agents/reasoning-looked-up, treasure-island/model-reasoning
"""Whether an OpenRouter model reasons is read from its free model listing, once."""

import io
import json

import pytest

from treasure_island import backends, openrouter, saved_game
from treasure_island.config import ConfigError, parse_config
from treasure_island.llm import THOUGHT
from treasure_island.saved_game import Models

REASONS, PLAIN = "deepseek/deepseek-chat-v3.1", "openai/gpt-4o-mini"
# OpenRouter's model listing, cut down to what matters, written from its docs.
LISTING = {
    "data": [
        {"id": REASONS, "supported_parameters": ["tools", "reasoning", "max_tokens"]},
        {"id": PLAIN, "supported_parameters": ["tools", "max_tokens"]},
    ]
}
DIG = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": json.dumps({"thinking": "dig here"}),
                "tool_calls": [
                    {"type": "function", "function": {"name": "dig", "arguments": "{}"}}
                ],
            }
        }
    ],
    "usage": {"cost": 0.0001},
}


class FakeOpenRouter:
    """Stands in for `urlopen`: the listing for GET /models, a dig for a chat."""

    def __init__(self, listing=LISTING):
        self.listing = listing
        self.chats, self.listed = [], 0

    def __call__(self, request, timeout=None):
        url = request if isinstance(request, str) else request.full_url
        if url == openrouter.MODELS_URL:
            self.listed += 1
            if isinstance(self.listing, Exception):
                raise self.listing
            return io.BytesIO(json.dumps(self.listing).encode())
        self.chats.append(json.loads(request.data))
        return io.BytesIO(json.dumps(DIG).encode())


@pytest.fixture
def fake(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "not-a-real-key")
    answer = FakeOpenRouter()
    monkeypatch.setattr(openrouter.urllib.request, "urlopen", answer)
    return answer


def toml(tmp_path, model, thinks=None, crew=1):
    extra = f'thinks = "{thinks}"\n' if thinks else ""
    pirate = f'[[pirates]]\nmodel = "openrouter/{model}"\n{extra}\n'
    path = tmp_path / "game.toml"
    path.write_text(
        'grid_size = 2\nturns_per_pirate = 1\nbrain = "silent"\n\n' + pirate * crew
    )
    return path


def play(path):
    return saved_game.play_saved(path, 0, models=Models(agree=lambda: True))


def test_reasoning_looked_up_from_the_listing_for_both_kinds_of_model(fake):
    assert openrouter.thinks_for(REASONS) == "built-in"
    assert openrouter.thinks_for(PLAIN) == "in-reply"


def test_reasoning_looked_up_a_model_the_listing_cannot_speak_for_keeps_the_default(
    fake,
):
    assert openrouter.thinks_for("someone/unlisted") is None
    fake.listing = OSError("no network")
    assert openrouter.thinks_for(PLAIN) is None
    model = f"openrouter/{PLAIN}"
    assert backends.looked_up_thinking([model]) == {model: "built-in"}


def test_reasoning_looked_up_a_plain_model_writes_its_thought_in_its_reply(
    fake, tmp_path
):
    folder = play(toml(tmp_path, PLAIN))
    (chat,) = fake.chats
    assert THOUGHT in chat["messages"][-1]["content"]
    assert "reasoning" not in chat
    saved = json.loads((folder / "config.json").read_text())
    assert saved["pirates"][0]["thinks"] == "in-reply"


def test_reasoning_looked_up_a_reasoning_model_gets_its_budget(fake, tmp_path):
    play(toml(tmp_path, REASONS))
    (chat,) = fake.chats
    assert THOUGHT not in chat["messages"][-1]["content"]
    assert chat["reasoning"]["max_tokens"] > 0


def test_reasoning_looked_up_once_and_a_replay_needs_no_network(
    fake, tmp_path, monkeypatch
):
    folder = play(toml(tmp_path, PLAIN))
    assert fake.listed == 1

    def no_network(*args, **kwargs):
        raise AssertionError("replay asked the network")

    monkeypatch.setattr(openrouter.urllib.request, "urlopen", no_network)
    assert saved_game.differences(folder) == []


def test_reasoning_looked_up_a_pirate_s_thinks_overrides_the_listing(fake, tmp_path):
    play(toml(tmp_path, REASONS, thinks="in-reply"))
    assert fake.listed == 0
    (chat,) = fake.chats
    assert THOUGHT in chat["messages"][-1]["content"]


def test_reasoning_looked_up_thinks_must_be_one_of_the_two_ways():
    assert parse_config({"pirates": [{"thinks": "in-reply"}]}).pirates[0].thinks == (
        "in-reply"
    )
    with pytest.raises(ConfigError, match="thinks"):
        parse_config({"pirates": [{"thinks": "sometimes"}]})


def test_reasoning_looked_up_a_plain_model_s_thought_reaches_the_record(fake, tmp_path):
    folder = play(toml(tmp_path, PLAIN))
    (first, *_) = (folder / "events.jsonl").read_text().splitlines()
    assert json.loads(first)["thinking"] == "dig here"


def test_reasoning_looked_up_once_for_the_whole_crew(fake, tmp_path):
    play(toml(tmp_path, PLAIN, crew=3))
    assert fake.listed == 1
