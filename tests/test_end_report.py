# Implements: treasure-island/end-report, treasure-island/disclosure-cost, treasure-island/config-variables
"""With `end_report` on, every pirate writes a free last note once the game ends."""

import json

from treasure_island import judge, viewer
from treasure_island.brain import END_QUESTION, PirateSeat
from treasure_island.config import parse_config, save_config
from treasure_island.game_loop import Game, write_game
from treasure_island.llm import LLMPirate
from treasure_island.runs import Replies
from treasure_island.spending import estimate
from treasure_island.strategies import Stripes

SIZE, CREW, TURNS = 4, 2, 12
DIG = json.dumps({"tool": "dig", "arguments": {}})


class Noting(Stripes):
    """A striping pirate that answers the last question with what it was asked."""

    def __init__(self, index):
        super().__init__(SIZE, CREW, index)
        self.asked = []

    def note(self, system, text):
        self.asked.append((system, text))
        return f"note {len(self.asked)} from a striper"


def config(**settings):
    game = {"grid_size": SIZE, "crew_size": CREW, "turns_per_pirate": TURNS}
    return parse_config({**game, "seed": 1, **settings})


def play(folder, **settings):
    folder.mkdir()
    brains = [Noting(index) for index in range(CREW)]
    save_config(config(**settings), folder / "config.json")
    write_game(config(**settings), brains, folder)
    lines = (folder / "events.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines], brains


def test_config_variables_end_report_is_off_by_default_and_saved(tmp_path):
    assert config().end_report is False
    save_config(config(end_report=True), tmp_path / "config.json")
    saved = json.loads((tmp_path / "config.json").read_text())
    assert saved["end_report"] is True
    assert parse_config(saved).end_report is True


def test_end_report_every_pirate_writes_a_note_in_pirate_order(tmp_path):
    records, brains = play(tmp_path / "on", end_report=True)
    notes = records[-1]["game_over"]["notes"]
    assert [n["agent"] for n in notes] == ["pirate-1", "pirate-2"]
    assert [n["note"] for n in notes] == ["note 1 from a striper"] * 2
    for brain in brains:
        ((system, text),) = brain.asked  # asked once, after the game
        assert text.endswith(END_QUESTION)
        assert "Your earlier turns:" in text  # with its own memory of the game
    assert "whistle" not in END_QUESTION.lower()
    assert "cheat" not in END_QUESTION.lower()


def test_end_report_changes_nothing_else_and_off_asks_nobody(tmp_path):
    on, _ = play(tmp_path / "on", end_report=True)
    off, brains = play(tmp_path / "off")
    assert all(brain.asked == [] for brain in brains)
    assert "notes" not in off[-1]["game_over"]
    without = {**on[-1]["game_over"]}
    del without["notes"]
    assert [*on[:-1], {**on[-1], "game_over": without}] == off  # the same score too


def test_end_report_the_story_ends_with_every_note(tmp_path):
    play(tmp_path / "on", end_report=True)
    story = (tmp_path / "on" / "story.txt").read_text().splitlines()
    assert story[-3].startswith("Game over:")
    assert story[-2:] == [
        "pirate-1's note to the designers: note 1 from a striper",
        "pirate-2's note to the designers: note 1 from a striper",
    ]


def test_end_report_the_transcripts_show_the_notes(tmp_path):
    records, _ = play(tmp_path / "on", end_report=True)
    markdown = viewer.transcript(tmp_path / "on")
    assert "## Notes to the designers" in markdown
    assert markdown.index("## Game over") < markdown.index("## Notes to the designers")
    assert "**pirate-2:**\n\n> note 1 from a striper" in markdown
    judged = judge.transcript(records)
    assert 'pirate-1: "note 1 from a striper"' in judged
    # A game with no notes gives the judge exactly what it gave before.
    off, _ = play(tmp_path / "off")
    assert "designers" not in judge.transcript(off)
    assert "Notes to the designers" not in viewer.transcript(tmp_path / "off")


class FakeModel:
    """Digs every turn, and answers the last question in plain words."""

    def __init__(self):
        self.requests = []

    def __call__(self, request):
        self.requests.append(request)
        if not request["tools"]:
            return "The refusal told me where the cave was.", 0.001
        return DIG, 0.001


def llm_game(tmp_path, backend):
    settings = {"pirates": [{"model": "fake/digger"}, {"model": "fake/digger"}]}
    game = config(end_report=True, turns_per_pirate=2, **settings)
    replies = Replies(tmp_path / "replies.jsonl", backend=backend)
    brains = [
        LLMPirate(f"pirate-{index + 1}", pirate, replies, game)
        for index, pirate in enumerate(game.pirates)
    ]
    return list(Game(game, brains).records())


def test_end_report_a_model_answers_in_free_text_and_replays_from_the_cache(tmp_path):
    model = FakeModel()
    records = llm_game(tmp_path, model)
    notes = [n["note"] for n in records[-1]["game_over"]["notes"]]
    assert notes == ["The refusal told me where the cave was."] * 2
    asked = [r for r in model.requests if not r["tools"]]
    assert [r["agent"] for r in asked] == ["pirate-1", "pirate-2"]
    for request in asked:
        assert request["messages"][-1]["content"].endswith(END_QUESTION)
    # A replay asks nothing and gets the same notes.
    assert llm_game(tmp_path, None) == records


def test_end_report_a_note_is_never_shown_to_another_pirate(tmp_path):
    records, brains = play(tmp_path / "on", end_report=True)
    for record in records:
        assert "note 1 from a striper" not in json.dumps(record["saw"])
    assert all("from a striper" not in text for _, text in brains[1].asked)


def test_end_report_the_estimate_counts_one_more_call_each(tmp_path):
    settings = {"pirates": [{"model": "fake/a"}, {"model": "fake/b"}]}
    plain = estimate(config(**settings))
    noted = estimate(config(end_report=True, **settings))
    assert noted.calls == plain.calls + CREW


def test_end_report_a_seat_with_no_note_to_give_gives_none():
    seat = PirateSeat("pirate-1", Stripes(SIZE, CREW, 0), config())
    assert seat.end_note() is None
