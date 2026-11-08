# Implements: viewer/scroll-numbers
"""The viewer numbers the scroll as the game does, from the old scroll's offset."""

import json
import re

import pytest

from treasure_island import viewer
from treasure_island.brain import Decision
from treasure_island.config import parse_config, save_config
from treasure_island.game_loop import write_game


class Writes:
    def decide(self, view):
        return Decision({"action": "write", "text": "hello"})


def written_game(tmp_path, **settings):
    config = parse_config(
        {"grid_size": 4, "crew_size": 2, "turns_per_pirate": 2, **settings}
    )
    save_config(config, tmp_path / "config.json")
    write_game(config, [Writes(), Writes()], tmp_path)
    return tmp_path


@pytest.mark.parametrize("settings, first", [({"old_scroll": True}, 1022), ({}, 1)])
def test_scroll_numbers_follow_the_game_on_the_page_and_the_board(
    tmp_path, settings, first
):
    folder = written_game(tmp_path, **settings)
    saved = (folder / "pirates-log.txt").read_text().splitlines()
    assert saved[0].startswith(f"{first} pirate-1: hello")
    page = viewer.slideshow_page(folder)
    turns = json.loads(re.search(r"const TURNS = (.*?);\n", page, re.DOTALL)[1])
    lines = [w["line"] for turn in turns for w in turn["wrote"]]
    assert lines == list(range(first, first + 4))
    records = viewer.records_in(folder)
    shown = viewer.scene(records, 3, 4, None, None, viewer.scoring_in(folder))
    assert [number for number, _ in shown["log_so_far"]] == lines


def test_scroll_numbers_the_page_s_list_starts_at_its_first_line():
    assert 'el("ol", { start: (before[0] || fresh[0]).line }' in viewer.SLIDESHOW
