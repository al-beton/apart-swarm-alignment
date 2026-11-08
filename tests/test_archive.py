# Implements: results/archived-games, results/archive-listed
"""Real model games are kept as played, each saying where it came from."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"
HEADINGS = [
    "## Played",
    "## Settings",
    "## What it cost",
    "## What it showed",
    "## Replaying it",
]
RUN_FILES = {"config.json", "events.jsonl", "manifest.json", "replies.jsonl"}


def games():
    return sorted(path for path in ARCHIVE.iterdir() if path.is_dir())


def test_archived_games_each_has_its_run_gif_and_about():
    assert games(), "archive/ holds no games"
    for game in games():
        assert RUN_FILES <= {p.name for p in (game / "run").iterdir()}, game.name
        assert (game / "game.gif").read_bytes().startswith(b"GIF"), game.name
        about = (game / "ABOUT.md").read_text()
        for heading in HEADINGS:
            assert heading in about, f"{game.name} has no {heading}"
        assert "commit" in about, f"{game.name} doesn't say its commit"


def test_archive_listed_each_game_once_in_the_guide():
    guide = (ARCHIVE / "README.md").read_text()
    for game in games():
        assert guide.count(f"`{game.name}/`") == 1, game.name
