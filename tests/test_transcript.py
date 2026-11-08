# Implements: viewer/transcript
"""Each game's transcript.md: every turn in full, readable on GitHub with no tool."""

import json
import re
import shutil
from pathlib import Path

import pytest

from treasure_island import cli, viewer

ROOT = Path(__file__).resolve().parents[1]
GAME = "examples/stripes"  # a finished game whose pirates think and write


@pytest.fixture
def saved(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    shutil.copytree(ROOT / GAME, tmp_path / "game")
    return tmp_path / "game"


def records_of(folder):
    lines = (folder / "events.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines]


def rewrite(folder, records):
    (folder / "events.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))


def headings(text):
    return [line for line in text.splitlines() if line.startswith("## Turn ")]


def turn_section(text, number):
    """The lines of one turn's section, from its heading to the next heading."""
    sections = re.split(r"^## ", text, flags=re.MULTILINE)
    return next(s for s in sections if s.startswith(f"Turn {number}:"))


def test_transcript_show_writes_it_into_the_run_folder(saved, capsys):
    assert cli.main(["show", str(saved)]) == 0
    written = saved / "transcript.md"
    assert written.read_text() == viewer.transcript(saved)
    assert str(written) in capsys.readouterr().out


def test_transcript_one_heading_per_turn_from_the_game_page_s_record(saved):
    turns = viewer.turn_records(records_of(saved))
    expected = [f"## Turn {t['turn']}: {t['agent']}" for t in turns]
    assert headings(viewer.transcript(saved)) == expected


def test_transcript_each_turn_holds_its_folded_prompt_thinking_action_and_result(saved):
    records = records_of(saved)
    records[1]["thinking"] = "First I look.\n\nThen I dig."
    records[1]["refused"] = [{"reply": "I'd rather nap", "why": "no tool call"}]
    records[1]["did"] = [{"action": "write", "text": "Dug here"}]
    rewrite(saved, records)
    section = turn_section(viewer.transcript(saved), records[1]["turn"])
    folded = re.search(
        r"<details>\n<summary>(.*?)</summary>\n\n(`{3,})text\n(.*?)\n\2\n\n</details>",
        section,
        re.DOTALL,
    )
    assert folded and folded.group(3) == records[1]["saw"]["prompt"]
    assert "> First I look.\n>\n> Then I dig." in section
    assert "I'd rather nap" in section and "no tool call" in section
    assert 'write {"text": "Dug here"}' in section
    assert records[1]["result"] in section
    order = [
        section.index(part)
        for part in ("<details>", "First I look", "write {", records[1]["result"])
    ]
    assert order == sorted(order)


def test_transcript_a_scripted_turn_with_no_prompt_or_thinking_says_so(saved):
    records = records_of(saved)
    records[0]["saw"]["prompt"] = ""
    records[0].pop("thinking", None)
    rewrite(saved, records)
    section = turn_section(viewer.transcript(saved), records[0]["turn"])
    assert "<details>" not in section
    assert "No prompt recorded" in section
    assert "No thinking recorded" in section


def test_transcript_ends_with_the_game_over_line_and_the_score(saved):
    game_over = records_of(saved)[-1]["game_over"]
    text = viewer.transcript(saved).rstrip()
    ending = text[text.rindex("## Game over") :]
    assert game_over["story"] in ending
    assert ending.endswith(f"**Score:** {game_over['score']}")


def test_transcript_an_unfinished_game_says_it_has_no_ending_yet(saved):
    records = records_of(saved)
    del records[-1]["game_over"]
    rewrite(saved, records)
    text = viewer.transcript(saved)
    assert "## Game over" not in text
    assert "no game over line" in text.splitlines()[-1]


def test_transcript_a_pirate_s_words_cannot_break_its_structure(saved):
    words = (
        "</details>\n## Turn 99: pirate-9\n```\n<script>alert(1)</script> *bold* `code`"
    )
    records = records_of(saved)
    records[0]["saw"]["prompt"] = words
    records[0]["thinking"] = words
    records[0]["result"] = words
    records[0]["did"] = [{"action": "write", "text": words}]
    rewrite(saved, records)
    text = viewer.transcript(saved)
    assert len(headings(text)) == len(records)
    assert text.count("</details>") == text.count("<details>")
    assert "<script>" not in text.replace("```text", "").split("</details>", 1)[1]
    assert not re.search(r"^## Turn 99", text, re.MULTILINE)


def test_transcript_the_same_game_writes_the_same_text(saved):
    assert viewer.transcript(saved) == viewer.transcript(saved)


def test_transcript_the_readmes_point_to_the_stripes_transcript_first():
    assert "examples/stripes/transcript.md" in (ROOT / "README.md").read_text()
    assert "stripes/transcript.md" in (ROOT / "examples/README.md").read_text()
