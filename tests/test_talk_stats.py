# Implements: results/talk-stats
"""How much a crew talked, per game and pirate, from its event log alone."""

import json
import shutil
from pathlib import Path

from treasure_island import talk_stats

ROOT = Path(__file__).resolve().parent.parent


def sharer_game(folder):
    """A copy of the committed sharer game, whose crew says readings and alerts."""
    shutil.copytree(ROOT / "runs/reference-sharer", folder)
    return folder


def records_of(folder):
    return [
        json.loads(line) for line in (folder / "events.jsonl").read_text().splitlines()
    ]


def test_talk_stats_counts_each_pirate_s_turns_lines_alerts_and_readings(tmp_path):
    folder = sharer_game(tmp_path / "sharer")
    talk = talk_stats.game_talk(folder)
    records = records_of(folder)
    assert list(talk) == ["pirate-1", "pirate-2", "pirate-3"]
    for name, counts in talk.items():
        own = [r for r in records if r["agent"] == name]
        lines = [a for r in own for a in r["did"] if "say" in a]
        assert counts.asked == sum(r["asked"] for r in own)
        assert counts.walked == sum(not r["asked"] for r in own)
        assert counts.said == len(lines)
        assert counts.alerts == sum(bool(a.get("alert")) for a in lines)
        # The sharer says each dig's reading and, as an alert, the cave.
        assert counts.readings == counts.said - counts.alerts
        assert counts.calls == 0  # scripted pirates ask no model
    assert sum(t.walked for t in talk.values()) > 0
    assert sum(t.alerts for t in talk.values()) > 0


def test_talk_stats_a_reading_names_a_square_and_a_distance():
    assert talk_stats.says_a_reading("Dug C4: 5 away.")
    assert talk_stats.says_a_reading("C4 is 3 squares from the treasure")
    assert not talk_stats.says_a_reading("Cave at C4.")
    assert not talk_stats.says_a_reading("I'm 5 away from something")


def test_talk_stats_counts_model_calls_with_refusals_and_bad_replies(tmp_path):
    folder = sharer_game(tmp_path / "sharer")
    config = json.loads((folder / "config.json").read_text())
    config["pirates"][0]["model"] = "some/model"
    (folder / "config.json").write_text(json.dumps(config))
    records = records_of(folder)
    first = next(r for r in records if r["agent"] == "pirate-1" and r["asked"])
    first["failed_moves"] = [{"action": "enter"}]
    first["refused"] = [{"reply": "hmm", "why": "no tool call"}]
    lines = "".join(json.dumps(r) + "\n" for r in records)
    (folder / "events.jsonl").write_text(lines)
    talk = talk_stats.game_talk(folder)
    asked = sum(r["asked"] for r in records if r["agent"] == "pirate-1")
    assert talk["pirate-1"].calls == asked + 2
    assert talk["pirate-2"].calls == 0


def test_talk_stats_prints_a_row_per_pirate_and_a_total_per_game(tmp_path, capsys):
    root = tmp_path / "runs"
    sharer_game(root / "sharer" / "7")
    sharer_game(root / "sharer" / "8")
    assert talk_stats.main([str(root)]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("| Game | Pirate | Asked | Walked | Model calls")
    rows = [line for line in out[2:] if line.startswith("|")]
    assert len(rows) == 2 * (3 + 1)
    assert sum("| all |" in row for row in rows) == 2
    assert talk_stats.main([str(tmp_path / "nothing")]) == 1
