# Implements: runs/cost-before-run, runs/yes-before-spending, runs/spending-cap, runs/cached-is-free, runs/stops-cleanly
"""A run says what it can cost, spends only after a yes and stops at its cap."""

import builtins
import dataclasses
import json
from pathlib import Path

import pytest

from treasure_island import backends, cli, saved_game
from treasure_island.config import load_config
from treasure_island.event_log import log_errors
from treasure_island.saved_game import Models
from treasure_island.spending import Declined, Estimate, estimate

DIG = json.dumps({"tool": "dig", "arguments": {}})
CONFIG = """
grid_size = 3
turns_per_pirate = 3
brain = "silent"

[[pirates]]
model = "fake/digger"

[[pirates]]
model = "fake/digger"
"""
TURNS = 2 * 3


def yes():
    return True


class FakeModel:
    """A backend that always digs, at a fixed cost per reply."""

    def __init__(self, cost=0.001):
        self.cost = cost
        self.requests = []

    def __call__(self, request):
        self.requests.append(request)
        return DIG, self.cost


class Asker:
    """Stands in for the person at the keyboard, counting the questions."""

    def __init__(self, answer):
        self.answer = answer
        self.asked = 0

    def __call__(self):
        self.asked += 1
        return self.answer


@pytest.fixture
def toml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "diggers.toml"
    path.write_text(CONFIG)
    return path


def story_lines(folder):
    return (Path(folder) / "story.txt").read_text().splitlines()


def test_cost_before_run_counts_every_call_a_crew_can_make(toml):
    found = estimate(load_config(toml))
    # Each try at a turn, a bad reply being one of them; 2 tries by default.
    assert found.calls == TURNS * 2
    assert found.cached == 0
    assert found.tokens >= found.calls * load_config(toml).reply_tokens
    assert found.costs is None


def test_cost_before_run_counts_every_failed_move_a_turn_allows(toml):
    config = load_config(toml)
    more = dataclasses.replace(config, failed_tries=5)
    assert estimate(more).calls == TURNS * 5
    assert estimate(more).tokens > estimate(config).tokens


def test_cost_before_run_counts_the_thinking_budget(toml):
    config = load_config(toml)
    less = dataclasses.replace(config, thinking_tokens=config.thinking_tokens - 100)
    budget = estimate(config).tokens - estimate(less).tokens
    assert budget == estimate(config).calls * 100
    # A model that reasons gets its budget with thinking off too.
    off = dataclasses.replace(config, thinking=False)
    assert estimate(off).tokens == estimate(config).tokens


def test_cost_before_run_prices_a_model_whose_price_is_known(toml, monkeypatch):
    monkeypatch.setitem(backends.PRICES, "fake/digger", (1.0, 4.0))
    found = estimate(load_config(toml))
    reply_tokens = load_config(toml).reply_tokens
    assert found.costs["dollars"] >= found.calls * reply_tokens * 4.0 / 1_000_000


def test_cost_before_run_shows_a_cost_under_a_cent_as_more_than_nothing():
    found = Estimate(4, 0, 2000, {"dollars": 0.0042137}, ())
    text = found.as_text(1.0)
    assert "costing at most $0.0042." in text
    assert "$0.00." not in text


def test_cost_before_run_shows_an_adaption_cost_in_credits(toml):
    toml.write_text(
        toml.read_text().replace("fake/digger", "adaption/deepseek-v4-flash")
    )
    text = estimate(load_config(toml)).as_text(1.0)
    assert "Adaption credits." in text
    assert "costing at most $" not in text


def test_cost_before_run_counts_replies_earlier_runs_got(toml):
    saved_game.play_saved(toml, 0, models=Models(FakeModel(), agree=yes))
    config = load_config(toml)
    assert estimate(config).cached == TURNS
    other_seed = dataclasses.replace(config, seed=9)
    assert estimate(other_seed).cached == 0


def test_cost_before_run_is_printed_before_the_first_turn(toml, monkeypatch, capsys):
    monkeypatch.setattr(builtins, "input", lambda prompt: "no")
    monkeypatch.setattr(saved_game, "backend_for", lambda model: FakeModel())
    cli.main(["run", str(toml), "--seed", "0", "--no-watch"])
    out = capsys.readouterr().out
    assert f"{TURNS * 2} model calls" in out
    assert "Earlier runs hold 0 replies" in out
    assert "{" not in out and "}" not in out
    assert "tokens" in out
    assert "no price" in out


def test_cost_before_run_says_nothing_for_a_crew_with_no_model(tmp_path, capsys):
    path = tmp_path / "plain.toml"
    path.write_text('brain = "silent"\ngrid_size = 3\nturns_per_pirate = 2\n')
    assert estimate(load_config(path)).calls == 0


def test_yes_before_spending_asks_once_before_the_first_uncached_call(toml):
    asker = Asker(True)
    saved_game.play_saved(toml, 0, models=Models(FakeModel(), agree=asker))
    assert asker.asked == 1


def test_yes_before_spending_anything_but_yes_spends_nothing(toml):
    model = FakeModel()
    with pytest.raises(Declined, match="said yes"):
        saved_game.play_saved(toml, 0, models=Models(model, agree=Asker(False)))
    assert model.requests == []


def test_yes_before_spending_anything_but_yes_leaves_no_run_folder(toml):
    with pytest.raises(Declined):
        saved_game.play_saved(toml, 0, models=Models(FakeModel(), agree=Asker(False)))
    assert list(Path("runs").iterdir()) == []


def test_yes_before_spending_with_no_one_to_ask_spends_nothing(toml):
    model = FakeModel()
    with pytest.raises(Declined):
        saved_game.play_saved(toml, 0, models=Models(model))
    assert model.requests == []


def test_yes_before_spending_the_question_reads_y_or_yes(toml, monkeypatch):
    answers = iter(["", "y"])
    monkeypatch.setattr(builtins, "input", lambda prompt: next(answers))
    monkeypatch.setattr(saved_game, "backend_for", lambda model: FakeModel())
    assert cli.main(["run", str(toml), "--seed", "0", "--no-watch"]) == 1
    assert cli.main(["run", str(toml), "--seed", "1", "--no-watch"]) == 0
    (kept,) = Path("runs").iterdir()
    assert story_lines(kept)[-1].startswith("Game over:")


def test_yes_before_spending_yes_skips_the_question(toml, monkeypatch):
    def no_one_there(prompt):
        raise AssertionError("asked a question despite --yes")

    monkeypatch.setattr(builtins, "input", no_one_there)
    monkeypatch.setattr(saved_game, "backend_for", lambda model: FakeModel())
    assert cli.main(["run", str(toml), "--seed", "0", "--no-watch", "--yes"]) == 0


def test_yes_before_spending_nothing_in_ci_passes_yes():
    root = Path(__file__).resolve().parents[1]
    for path in [*(root / ".github").rglob("*.yml"), root / "Makefile"]:
        assert "--yes" not in path.read_text(), path


def test_spending_cap_stops_asking_once_the_cap_is_spent(toml):
    model = FakeModel(cost=0.4)
    models = Models(model, cap_usd=1.0, agree=yes)
    folder = saved_game.play_saved(toml, 0, models=models)
    assert len(model.requests) == 3  # 0, 0.4 and 0.8 are under the cap; 1.2 isn't
    assert "spending cap of $1.00" in story_lines(folder)[-1]
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["cost_usd"] == pytest.approx(1.2)


def test_spending_cap_defaults_to_one_dollar(toml):
    assert Models().cap_usd == 1.0
    model = FakeModel(cost=0.6)
    saved_game.play_saved(toml, 0, models=Models(model, agree=yes))
    assert len(model.requests) == 2


def test_spending_cap_is_set_on_the_command_line(toml, monkeypatch):
    model = FakeModel(cost=0.3)
    monkeypatch.setattr(saved_game, "backend_for", lambda name: model)
    argv = ["run", str(toml), "--seed", "0", "--no-watch", "--yes"]
    cli.main([*argv, "--spend-up-to", "0.5"])
    assert len(model.requests) == 2


def test_cached_is_free_a_repeat_needs_no_yes_and_no_money(toml):
    saved_game.play_saved(toml, 0, models=Models(FakeModel(), agree=yes))
    asker, model = Asker(False), FakeModel()
    repeat = saved_game.play_saved(
        toml, 0, models=Models(model, cap_usd=0.0, agree=asker)
    )
    assert (asker.asked, model.requests) == (0, [])
    assert story_lines(repeat)[-1].startswith("Game over:")
    manifest = json.loads((repeat / "manifest.json").read_text())
    assert manifest["cost_usd"] == 0


def test_stops_cleanly_a_capped_run_keeps_its_turns_and_replays(toml):
    models = Models(FakeModel(cost=0.4), cap_usd=1.0, agree=yes)
    folder = saved_game.play_saved(toml, 0, models=models)
    records = (folder / "events.jsonl").read_text().splitlines()
    assert len(records) == 3
    assert log_errors(folder / "events.jsonl") == []
    assert len(story_lines(folder)) == 3 + 1
    assert saved_game.differences(folder) == []
    assert cli.main(["replay", str(folder)]) == 0


def test_stops_cleanly_an_end_note_the_cap_stopped_replays(toml):
    toml.write_text(
        CONFIG.replace(
            "turns_per_pirate = 3", "turns_per_pirate = 1\nend_report = true"
        )
    )
    # Two turns and the first note fit under the cap; the second note doesn't.
    models = Models(FakeModel(cost=0.4), cap_usd=1.0, agree=yes)
    folder = saved_game.play_saved(toml, 0, models=models)
    last = json.loads((folder / "events.jsonl").read_text().splitlines()[-1])
    notes = last["game_over"]["notes"]
    assert notes[0]["note"] == DIG
    assert notes[1]["note"] is None and "spending cap" in notes[1]["stopped"]
    assert saved_game.differences(folder) == []


def test_stops_cleanly_a_run_stopped_before_its_first_turn_replays(toml):
    models = Models(FakeModel(), cap_usd=0.0, agree=yes)
    folder = saved_game.play_saved(toml, 0, models=models)
    assert (folder / "events.jsonl").read_text() == ""
    assert saved_game.differences(folder) == []


def test_cost_before_run_prints_the_numbers_it_found(toml):
    saved_game.play_saved(toml, 0, models=Models(FakeModel(), agree=yes))
    found = estimate(load_config(toml))
    text = found.as_text(1.0)
    assert f"{found.calls} model calls" in text
    assert f"hold {found.cached} replies" in text
    assert f"about {found.tokens} tokens" in text
    assert "{" not in text
