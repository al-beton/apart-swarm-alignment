# Implements: team/board-follows-labels
"""The board script picks each issue's Status from its queue label, and the workflow runs it."""

import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("board", HERE / "board.py")
board = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board)
WORKFLOW = (HERE.parent / "workflows" / "board.yml").read_text()


@pytest.mark.parametrize(
    "label,option",
    [
        ("ready", "a01d4fde"),
        ("in-progress", "3fc57595"),
        ("in-review", "e6ef7de0"),
        ("blocked", "aa728341"),
        ("on-hold", "d168af83"),
    ],
)
def test_board_follows_labels_each_queue_label_has_its_column(label, option):
    assert board.status_option(["feat", label], "open") == option
    assert board.status_option([label], "closed") == "f4c3e9c6"  # Done


def test_board_follows_labels_no_queue_label_clears_the_status():
    assert board.status_option(["feat", "bug"], "open") is None
    assert board.status_option([], "open") is None


def test_board_follows_labels_adds_the_issue_then_sets_its_status():
    calls = []

    def graphql(query, **variables):
        calls.append((query, variables))
        return {"addProjectV2ItemById": {"item": {"id": "ITEM"}}}

    board.sync("ISSUE", ["in-review"], "open", graphql)
    board.sync("ISSUE", ["feat"], "open", graphql)
    added, setting, again, clearing = calls
    assert "addProjectV2ItemById" in added[0]
    assert added[1] == {"project": board.PROJECT, "issue": "ISSUE"}
    assert "updateProjectV2ItemFieldValue" in setting[0]
    assert setting[1] == {
        "project": board.PROJECT,
        "item": "ITEM",
        "field": board.FIELD,
        "option": "e6ef7de0",
    }
    assert "clearProjectV2ItemFieldValue" in clearing[0]


def test_board_follows_labels_the_workflow_runs_on_label_changes_with_the_secret():
    for event in ("opened", "labeled", "unlabeled", "closed", "reopened"):
        assert event in WORKFLOW
    assert "secrets.PROJECT_TOKEN" in WORKFLOW
    assert "github_pat_" not in WORKFLOW and "ghp_" not in WORKFLOW
    assert ".github/scripts/board.py" in WORKFLOW
