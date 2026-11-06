# Implements: agents/one-interface, agents/scripted-sees-the-prompt, agents/grid-sweep, agents/counter, agents/free-runs-in-ci, agents/committed-runs
"""The scripted agents: they answer like a model, and a run of each is free."""

import json
import os
import socket
from pathlib import Path

import pytest

from treasure_island import cli
from treasure_island.backends import backend_for
from treasure_island.event_log import log_errors
from treasure_island.game import Config, play, prompt

ROOT = Path(__file__).resolve().parent.parent
SCRIPTED = ("scripted/random", "scripted/sweep", "scripted/counter")


def request(agent, position, size=3, model="scripted/sweep"):
    """What the game sends: the prompt is all the agent has to go on."""
    return {
        "agent": agent,
        "model": model,
        "prompt": prompt(agent, list(position), 0, Config(size=size, model=model)),
        "temperature": 0.0,
        "seed": 1,
    }


def playing(model):
    """An `ask` for `play` that routes every request to one scripted agent."""
    agent = backend_for(model)
    return lambda request: agent(request)[0]


@pytest.fixture
def offline(monkeypatch, tmp_path):
    """No keys, no sockets, and a fresh folder for runs/."""
    for name in list(os.environ):
        if name.endswith("_API_KEY"):
            monkeypatch.delenv(name)

    def no_network(*args, **kwargs):
        raise AssertionError("a socket was opened")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.mark.parametrize("model", SCRIPTED)
def test_one_interface_every_scripted_agent_answers_like_a_model(model):
    text, cost = backend_for(model)(request("pirate-a", (0, 0), model=model))
    assert isinstance(text, str) and text
    assert cost == 0.0


def test_one_interface_each_run_gets_a_fresh_agent():
    first = backend_for("scripted/counter")
    second = backend_for("scripted/counter")
    assert first(request("pirate-a", (0, 0)))[0] == "write 1"
    assert first(request("pirate-a", (0, 0)))[0] == "write 2"
    assert second(request("pirate-a", (0, 0)))[0] == "write 1"


def test_scripted_sees_the_prompt_the_sweep_reads_where_it_is():
    sweep = backend_for("scripted/sweep")
    assert sweep(request("pirate-a", (0, 0)))[0] == "dig"
    assert sweep(request("pirate-a", (0, 0)))[0] == "move east"
    assert sweep(request("pirate-a", (2, 1)))[0] == "dig"
    assert sweep(request("pirate-a", (2, 1)))[0] == "move west"


def test_scripted_sees_the_prompt_memory_is_per_pirate():
    counter = backend_for("scripted/counter")
    assert counter(request("pirate-a", (0, 0)))[0] == "write 1"
    assert counter(request("pirate-b", (0, 0)))[0] == "write 1"
    assert counter(request("pirate-a", (0, 0)))[0] == "write 2"


def test_grid_sweep_walks_row_by_row_and_turns_back_at_the_far_corner():
    sweep = backend_for("scripted/sweep")
    path = [(0, 0), (0, 0), (1, 0), (1, 0), (1, 1), (1, 1), (0, 1), (0, 1), (1, 1)]
    replies = [sweep(request("pirate-a", spot, size=2))[0] for spot in path]
    assert replies == [
        "dig",
        "move east",
        "dig",
        "move south",
        "dig",
        "move west",
        "dig",
        "move east",
        "move north",
    ]


@pytest.mark.parametrize("seed", range(8))
def test_grid_sweep_finds_the_treasure_from_anywhere(seed):
    config = Config(size=3, pirates=1, turns=40, model="scripted/sweep")
    events = list(play(config, seed, playing("scripted/sweep")))
    assert events[-1]["outcome"]["found_treasure"] is True


def test_counter_says_the_next_number_each_turn_and_never_digs():
    config = Config(size=1, pirates=1, turns=5, model="scripted/counter")
    events = list(play(config, 0, playing("scripted/counter")))
    assert [event["did"] for event in events] == [
        [{"action": "write", "text": str(n)}] for n in range(1, 6)
    ]
    assert not any(event["outcome"]["found_treasure"] for event in events)


@pytest.mark.parametrize("name", ["sweep", "counter"])
def test_free_runs_in_ci_each_scripted_config_plays_a_full_game(name, offline, capsys):
    config = ROOT / "configs" / f"{name}.toml"
    assert cli.main(["run", str(config), "--seed", "1"]) == 0
    folder = offline / capsys.readouterr().out.strip()
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["cost_usd"] == 0
    events = [
        json.loads(line) for line in (folder / "events.jsonl").read_text().splitlines()
    ]
    turns = json.loads((folder / "config.json").read_text())["turns"]
    if name == "sweep":
        assert events[-1]["outcome"]["found_treasure"] is True
    else:
        assert len(events) == turns


@pytest.mark.parametrize("name", ["sweep-seed-5", "counter-seed-1"])
def test_committed_runs_pass_the_validator_and_replay_byte_identical(name, offline):
    folder = ROOT / "runs" / name
    assert log_errors(folder / "events.jsonl") == []
    model = json.loads((folder / "config.json").read_text())["model"]
    assert model == f"scripted/{name.split('-')[0]}"
    assert cli.main(["replay", str(folder)]) == 0
