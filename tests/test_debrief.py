# Implements: runs/debrief-command, runs/debrief-cached
"""After a game, each model pirate is asked a few fixed questions about it."""

import json
from pathlib import Path

import pytest

from treasure_island import debrief
from treasure_island.spending import Declined

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = (ROOT / "prompts/debrief/questions.md").read_text().splitlines()


def request(agent, text, model="fake/model"):
    return {
        "agent": agent,
        "model": model,
        "seed": 3,
        "system": f"rules for {agent}",
        "messages": [{"role": "user", "content": text}],
        "tools": [{"name": "dig"}],
        "max_tokens": 300,
        "thinking": True,
        "thinking_tokens": 4096,
    }


def finished_run(tmp_path):
    """A run where pirate-1 and pirate-2 played models; pirate-3 was scripted."""
    run = tmp_path / "run"
    run.mkdir()
    rows = [
        {"key": "a", "request": request("pirate-1", "turn 1"), "reply": "dig"},
        {"key": "b", "request": request("pirate-2", "turn 1"), "reply": "wait"},
        {
            "key": "c",
            "request": request("pirate-1", "turn 9 of pirate-1"),
            "reply": "enter",
        },
    ]
    (run / "replies.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    over = {"game_over": {"score": 270, "in_cave": ["pirate-1", "pirate-3"]}}
    (run / "events.jsonl").write_text(
        json.dumps({"turn": 1}) + "\n" + json.dumps(over) + "\n"
    )
    (run / "config.json").write_text(json.dumps({"crew_size": 3}))
    return run


class Fake:
    def __init__(self):
        self.asked = []

    def __call__(self, request):
        self.asked.append(request)
        return f"answer {len(self.asked)}", 0.0


def yes():
    return True


def test_debrief_command_asks_each_model_pirate_the_questions_in_order(tmp_path):
    fake = Fake()
    debrief.debrief(finished_run(tmp_path), backend=fake, agree=yes)
    assert [r["agent"] for r in fake.asked] == ["pirate-1"] * 3 + ["pirate-2"] * 3
    for asked, question in zip(fake.asked[:3], QUESTIONS, strict=True):
        assert asked["messages"][-1] == {
            "role": "user",
            "content": asked["messages"][-1]["content"],
        }
        assert asked["messages"][-1]["content"].endswith(question)
        assert asked["tools"] == []
    # Each question follows the answers before it, in one conversation.
    third = fake.asked[2]["messages"]
    assert [m["role"] for m in third] == [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
    ]
    assert third[3]["content"] == "answer 1" and third[5]["content"] == "answer 2"


def test_debrief_command_starts_from_the_last_turn_and_the_ending(tmp_path):
    fake = Fake()
    debrief.debrief(finished_run(tmp_path), backend=fake, agree=yes)
    first = fake.asked[0]
    assert first["system"] == "rules for pirate-1"
    assert first["messages"][0] == {"role": "user", "content": "turn 9 of pirate-1"}
    assert first["messages"][1] == {"role": "assistant", "content": "enter"}
    ending = first["messages"][2]["content"]
    assert ending.startswith(
        "2 of 3 pirates got into the cave, and your crew scored 270."
    )


def test_debrief_command_writes_one_line_per_pirate(tmp_path):
    run = finished_run(tmp_path)
    debrief.debrief(run, backend=Fake(), agree=yes)
    lines = [
        json.loads(line) for line in (run / "debrief.jsonl").read_text().splitlines()
    ]
    assert [line["pirate"] for line in lines] == ["pirate-1", "pirate-2"]
    assert lines[0]["model"] == "fake/model"
    assert lines[0]["answers"] == [
        {"question": q, "answer": f"answer {n}"} for n, q in enumerate(QUESTIONS, 1)
    ]


def test_debrief_cached_a_second_debrief_asks_nothing(tmp_path):
    run = finished_run(tmp_path)
    debrief.debrief(run, backend=Fake(), agree=yes)
    first = (run / "debrief.jsonl").read_text()
    again = Fake()
    debrief.debrief(run, backend=again, agree=yes)
    assert again.asked == []
    assert (run / "debrief.jsonl").read_text() == first


def test_debrief_cached_nothing_is_spent_without_a_yes(tmp_path):
    fake = Fake()
    with pytest.raises(Declined):
        debrief.debrief(finished_run(tmp_path), backend=fake, agree=lambda: False)
    assert fake.asked == []


def test_debrief_command_a_run_that_never_ended_is_refused(tmp_path):
    run = finished_run(tmp_path)
    (run / "events.jsonl").write_text(json.dumps({"turn": 1}) + "\n")
    with pytest.raises(debrief.NotFinished):
        debrief.debrief(run, backend=Fake(), agree=yes)


def test_debrief_command_one_command_debriefs_each_folder(
    tmp_path, monkeypatch, capsys
):
    from treasure_island import cli

    run = finished_run(tmp_path)
    fake = Fake()
    monkeypatch.setattr(debrief, "_every_model", lambda models: fake)
    assert cli.main(["debrief", str(run), "--yes"]) == 0
    assert "6 debrief calls" in capsys.readouterr().out
    assert len(fake.asked) == 6 and (run / "debrief.jsonl").exists()
