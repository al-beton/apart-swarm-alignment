# Implements: workflow/one-page-for-people
"""CONTRIBUTING.md is the one page a person reads to know how to work here."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = ("ready", "in-progress", "in-review", "blocked", "on-hold")


def page():
    return (ROOT / "CONTRIBUTING.md").read_text()


def test_one_page_for_people_covers_the_loop_labels_spec_check_and_a_game():
    text = page()
    # Seeing a game: the one command, on a committed example.
    assert re.search(r"uv run treasure-island show examples/\w+", text)
    # The loop: spec first, a failing test, the trace, then the review round.
    for word in ("Spec first", "Failing test", "Implements:", "Where this is enforced"):
        assert word in text, word
    # The pull request's title shape and closing line, which CI checks.
    assert "<feat|fix|improve>(<area>): <summary> (#<n>)" in text
    assert "Closes #<n>" in text
    # The review round a person can't ask for themself, and the merge.
    assert "@codex review" in text
    assert "merge" in text.lower()
    # Every queue label, and the checks to keep green.
    for label in LABELS:
        assert f"`{label}`" in text, label
    for command in ("make lint", "make test", "make spec-check"):
        assert command in text, command


def test_one_page_for_people_is_linked_from_the_readme():
    readme = (ROOT / "README.md").read_text()
    assert "CONTRIBUTING.md" in readme
    # The history reset is told once, on the page for people, not in the README.
    assert "## History reset" not in readme
    assert "## The history reset" in page()
