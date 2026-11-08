# Implements: specs-and-docs/readme-reads-a-game
"""The README reads one real game with you, quoting it exactly."""

import re
import shlex
import shutil
from pathlib import Path

from treasure_island import cli

ROOT = Path(__file__).resolve().parents[1]
HEADING = "Read one game"
GAME = ROOT / "runs/readme-walkthrough"


def section():
    readme = (ROOT / "README.md").read_text()
    return readme.split(f"## {HEADING}", 1)[1].split("\n## ", 1)[0]


def quoted():
    """Every line in the section's text blocks, in order."""
    blocks = re.findall(r"```text\n(.*?)```", section(), flags=re.DOTALL)
    return [line for block in blocks for line in block.splitlines()]


def test_readme_reads_a_game_comes_right_after_quick_start():
    headings = re.findall(
        r"^## (.+)$", (ROOT / "README.md").read_text(), flags=re.MULTILINE
    )
    assert headings[:2] == ["Quick start", HEADING]


def test_readme_reads_a_game_quotes_its_whole_story_exactly():
    assert quoted() == (GAME / "story.txt").read_text().splitlines()


def test_readme_reads_a_game_says_something_about_every_step():
    # Each line of the story gets its own block, with a sentence before it.
    blocks = re.findall(r"([^\n]+)\n\n```text\n", section())
    assert len(blocks) == len(quoted())
    assert all(sentence.strip() for sentence in blocks)


def test_readme_reads_a_game_explains_the_other_files_and_shows_the_gif():
    text = section()
    assert "`pirates-log.txt`" in text
    assert "`events.jsonl`" in text
    assert "(runs/readme-walkthrough/game.gif)" in text


def test_readme_reads_a_game_is_honest_that_these_pirates_write_no_notes():
    text = section()
    assert "no notes" in text
    assert "examples/stripes" in text
    log = (GAME / "pirates-log.txt").read_text().splitlines()
    assert all(line.split(":", 1)[1] == "" for line in log)


def test_readme_reads_a_game_commands_work(tmp_path, monkeypatch, capsys):
    block = re.search(r"```bash\n(.*?)```", section(), flags=re.DOTALL).group(1)
    clone, enter, show = block.strip().splitlines()
    assert clone.startswith("git clone ")
    assert enter == "cd apart-swarm-alignment"
    shutil.copytree(ROOT / "runs/readme-walkthrough", tmp_path / "runs/readme-walkthrough")
    monkeypatch.chdir(tmp_path)
    assert cli.main(shlex.split(show)[3:]) == 0
    assert "readme-walkthrough.gif" in capsys.readouterr().out
