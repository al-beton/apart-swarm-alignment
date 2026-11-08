# Implements: cave-leak/first-entry, cave-leak/fires
"""Experiment one's table: each game's first cave entry, crew in, score and leak."""

import json

from treasure_island import cave_leak_table
from treasure_island.brain import Decision
from treasure_island.config import parse_config
from treasure_island.game_loop import write_game
from treasure_island.strategies import Stripes

SIZE, CREW, TURNS = 4, 2, 12


class TriesFirst:
    """Pirate 1 tries to enter where it stands on its first turn, then stripes."""

    def __init__(self, inner):
        self.inner, self.tried = inner, False

    def decide(self, view):
        if not self.tried:
            self.tried = True
            return Decision({"action": "enter"}, "I'll try the cave here.")
        return self.inner.decide(view)


def play(folder, seed, leak, baited):
    folder.mkdir(parents=True)
    settings = {"grid_size": SIZE, "crew_size": CREW, "turns_per_pirate": TURNS}
    config = parse_config({**settings, "seed": seed, "cave_leak": leak})
    brains = [Stripes(SIZE, CREW, index) for index in range(CREW)]
    if baited:
        brains[0] = TriesFirst(brains[0])
    write_game(config, brains, folder)


def records(folder):
    lines = (folder / "events.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines]


def experiment(root):
    for seed in (1, 2):
        play(root / "control" / str(seed), seed, leak=False, baited=True)
        play(root / "forced" / str(seed), seed, leak=True, baited=True)
    play(root / "unbaited" / "1", 1, leak=True, baited=False)
    (root / "notes.md").write_text("")  # not an arm: listed and skipped
    (root / "forced" / "9").mkdir()  # no events.jsonl yet: skipped too
    return root


def test_first_entry_each_game_has_its_turn_crew_in_and_score_from_the_log(tmp_path):
    root = experiment(tmp_path)
    games = cave_leak_table.games(root)
    assert [(g.arm, g.seed) for g in games] == [
        ("control", 1),
        ("control", 2),
        ("forced", 1),
        ("forced", 2),
        ("unbaited", 1),
    ]
    for game in games:
        log = records(root / game.arm / str(game.seed))
        entered = [r["turn"] for r in log if r["outcome"].get("in_cave")]
        assert game.first_entry == (entered[0] if entered else None)
        assert game.pirates_in == len(entered) == len(log[-1]["game_over"]["in_cave"])
        assert game.score == log[-1]["game_over"]["score"]
    assert any(game.first_entry is not None for game in games)


def test_fires_reads_the_leak_from_the_record_s_mark(tmp_path):
    root = experiment(tmp_path)
    by_name = {(g.arm, g.seed): g for g in cave_leak_table.games(root)}
    for seed in (1, 2):
        # The same try with the leak off tells nobody anything.
        assert by_name["control", seed].leak_turn is None
        assert by_name["control", seed].leaked_to == []
        # With it on, pirate-1's first turn is refused and told the square.
        assert by_name["forced", seed].leak_turn == 0
        assert by_name["forced", seed].leaked_to == ["pirate-1"]
    assert by_name["unbaited", 1].leak_turn is None


def test_first_entry_the_table_is_markdown_with_a_row_a_game_and_a_summary_an_arm(
    tmp_path,
):
    root = experiment(tmp_path)
    games = cave_leak_table.games(root)
    text = cave_leak_table.table(root)
    rows = [line for line in text.splitlines() if line.startswith("| ")]
    header = "| Arm | Seed | First entry | Pirates in | Score | Leak fired | Told |"
    assert header in rows
    for game in games:
        first = "never" if game.first_entry is None else f"turn {game.first_entry}"
        fired = "never" if game.leak_turn is None else f"turn {game.leak_turn}"
        told = ", ".join(game.leaked_to) or "nobody"
        row = (
            f"| {game.arm} | {game.seed} | {first} | {game.pirates_in} "
            f"| {game.score} | {fired} | {told} |"
        )
        assert row in rows
    # The summary pairs each arm with control by seed.
    forced = [g for g in games if g.arm == "forced"]
    control = {g.seed: g for g in games if g.arm == "control"}
    mean_score = sum(g.score for g in forced) / len(forced)
    gain = sum(g.score - control[g.seed].score for g in forced) / len(forced)
    assert any(
        line.startswith("| forced | 2 | ")
        and f"{mean_score:.1f}" in line
        and f"{gain:+.1f}" in line
        for line in rows
    )
    assert "notes.md" in text and "forced/9" in text  # what was skipped, and why


def test_first_entry_one_command_prints_the_table(tmp_path, capsys):
    root = experiment(tmp_path)
    assert cave_leak_table.main([str(root)]) == 0
    assert capsys.readouterr().out == cave_leak_table.table(root) + "\n"
