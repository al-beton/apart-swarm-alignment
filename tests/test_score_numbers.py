# Implements: event-log/score-numbers
"""The event log keeps the run's score numbers, so the score can be counted again."""

from treasure_island.brain import Decision
from treasure_island.config import parse_config
from treasure_island.game_loop import Game


class Digs:
    def decide(self, view):
        return Decision({"action": "dig"})


def test_score_numbers_the_last_record_holds_the_run_s_score_numbers():
    settings = {"grid_size": 3, "crew_size": 1, "turns_per_pirate": 4}
    numbers = {"score_in_cave": 70, "score_per_turn_left": 3}
    config = parse_config({**settings, **numbers})
    *turns, last = Game(config, [Digs()]).records()
    assert last["game_over"]["score_numbers"] == {"turns_per_pirate": 4, **numbers}
    assert all("game_over" not in record for record in turns)
