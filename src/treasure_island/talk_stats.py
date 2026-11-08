"""How much a crew talked: per game, per pirate, read from the event log alone.

`uv run python -m treasure_island.talk_stats runs/<name> ...` finds every game
(a folder holding `events.jsonl`) under the folders given and prints one Markdown
row per pirate: the turns it was asked and the turns it walked under an order,
its model calls, the lines it said, how many of them were alerts and how many
readings it said, each square said with its distance counted once, in the forms
pirates write ("Dug C4: 5 away.", "A10=9", "A10 reads 9", "reading 9 at A10"),
banded ones too ("Dug C4: warm (3-5).", "C4 cold", `reading-bands`). A
total row ends each game. It is how we check a live crew keeps talking all game
rather than going quiet after its first few turns.

Model calls are counted from the records: each asked turn of a pirate with a
model in the run's `config.json` makes one call for its action, one more for
each action the game refused and one for each reply that wasn't a tool call; a
dropped call tried again isn't counted twice. A scripted pirate makes none, and
a run with no `config.json` counts every pirate as asking a model (default, Edu
to confirm).

Implements: results/talk-stats, treasure-island/reading-bands
"""

import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

# A reading said on the scroll: a square and the distance dug there, in the forms
# pirates use. Squares are capitals, as the game names them; the words aren't.
_S = r"\b[A-Z][1-9]\d?\b"
_N = r"\b\d{1,2}\b"
_UNIT = r"(?i:\s*(?:away|squares?|steps?)\b)"
_BAND = r"(?i:hot|warm|cool|cold)\b"
_NOT_A_COUNT = r"(?!(?i:\s*(?:turns?|pirates?|of)\b))"
_READING = re.compile(
    "|".join(
        (
            rf"{_S}\s*(?:=|:|->)\s*{_N}{_NOT_A_COUNT}",  # A10=9, Dug A10: 9 away
            rf"{_S}\s+(?i:(?:is|reads?|gave|gives|shows?)\s+)?{_N}{_UNIT}",  # A10 9 away
            rf"{_S}\s+(?i:reads?|gave|gives|shows?)\s*:?\s*{_N}",  # A10 reads 9
            rf"(?i:reading)\s+(?i:of\s+)?{_N}\s+(?i:at|on|from)\s+{_S}",  # reading 9 at A10
            rf"{_N}{_UNIT}\s+(?i:from|at|of)\s+{_S}",  # 9 away from A10
            rf"{_S}\s*(?:=|:|->|\s(?i:is|reads?|gave|gives|shows?))?\s*{_BAND}",  # C4 warm
        )
    )
)
COLUMNS = (
    "Asked",
    "Walked",
    "Model calls",
    "Lines said",
    "Alerts",
    "Readings said",
)


class Talk(NamedTuple):
    """One pirate's talk in one game."""

    asked: int = 0
    walked: int = 0
    calls: int = 0
    said: int = 0
    alerts: int = 0
    readings: int = 0

    def __add__(self, other):
        return Talk(*(a + b for a, b in zip(self, other, strict=True)))


def readings_in(line):
    """How many readings a said line gives: each square with its distance, once."""
    return len(_READING.findall(line))


def says_a_reading(line):
    """Whether a said line gives at least one reading."""
    return readings_in(line) > 0


def _model_pirates(folder, names):
    """The pirates that ask a model, by name, from the run's config."""
    config = Path(folder) / "config.json"
    if not config.exists():
        return set(names)
    pirates = json.loads(config.read_text()).get("pirates") or []
    return {
        f"pirate-{index + 1}"
        for index, pirate in enumerate(pirates)
        if pirate.get("model")
    }


def _calls(record):
    """The model calls one asked turn made: its action, refusals and bad replies."""
    acted = 1 if record.get("did") else 0
    return acted + len(record.get("failed_moves", [])) + len(record.get("refused", []))


def _turn(record, asks_a_model):
    """One turn's talk. A first-rules record, with no `asked`, was asked."""
    lines = [a for a in record["did"] if "say" in a]
    walked = record.get("asked") is False
    return Talk(
        asked=0 if walked else 1,
        walked=1 if walked else 0,
        calls=_calls(record) if asks_a_model and not walked else 0,
        said=len(lines),
        alerts=sum(1 for a in lines if a.get("alert")),
        readings=sum(readings_in(a["say"]) for a in lines),
    )


def game_talk(folder):
    """Each pirate's talk in the game in `folder`, in crew order."""
    path = Path(folder) / "events.jsonl"
    records = [json.loads(line) for line in path.read_text().splitlines() if line]
    names = list(dict.fromkeys(record["agent"] for record in records))
    models = _model_pirates(folder, names)
    talk = {name: Talk() for name in names}
    for record in records:
        agent = record["agent"]
        talk[agent] += _turn(record, agent in models)
    return talk


def games_under(paths):
    """Every game folder under `paths`, in order: a folder holding `events.jsonl`."""
    found = []
    for path in map(Path, paths):
        if (path / "events.jsonl").exists():
            found.append(path)
        else:
            found += sorted(p.parent for p in path.glob("**/events.jsonl"))
    return found


def table(paths):
    """The Markdown table: a row per pirate of every game, and a total per game."""
    head = ["Game", "Pirate", *COLUMNS]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for folder in games_under(paths):
        talk = game_talk(folder)
        rows = [*talk.items(), ("all", sum(talk.values(), Talk()))]
        for name, counts in rows:
            cells = [str(folder), name, *map(str, counts)]
            lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: python -m treasure_island.talk_stats <run folder> ...")
        return 2
    if not games_under(argv):
        print("No game found: no events.jsonl under " + ", ".join(argv))
        return 1
    print(table(argv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
