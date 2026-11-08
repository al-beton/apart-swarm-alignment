"""The pirates' log is a scroll: nothing on it is shown for free.

Writing adds one line, numbered from 1 (or from the old scroll's offset), saying who wrote it. Reading shows a
pirate every line it hasn't read yet, its own included, and moves its place to
the end, so a pirate can write without ever having read. Both cost the turn; any other turn
leaves the scroll as it was, so it holds only notes. Each line looks like the
event log's `log_shown` entries, with `by` naming the writer.

Implements: treasure-island/every-turn-a-line, treasure-island/reading-costs, treasure-island/actions, treasure-island/old-scroll, treasure-island/free-talk
"""

import dataclasses


@dataclasses.dataclass(frozen=True)
class ReadAnswer:
    """The lines a read found, or a message saying there was nothing new."""

    lines: list
    message: str = ""


def one_line(note):
    """A note as the scroll holds it: one line, however it was written."""
    return " ".join(note.splitlines())


def written(action):
    """What an action that happened put on the scroll, in order, as it was written.

    A `write`'s text, then any free message (`free-talk`), which any action may carry.
    """
    texts = [action["text"]] if action.get("action") == "write" else []
    return texts + ([action["message"]] if "message" in action else [])


class PiratesLog:
    def __init__(self, first=1):
        self._first = first  # the first line's number: 1, or higher (`old-scroll`)
        self._lines = []
        self._read_up_to = {}

    def lines(self):
        """Every line so far, for our own records. Pirates only see what they read."""
        return list(self._lines)

    def write(self, by, note):
        """Spend the turn adding a note. A note always stays on one line."""
        number = self._first + len(self._lines)
        self._lines.append({"line": number, "text": one_line(note), "by": by})

    def read(self, reader):
        """Spend the turn reading every line `reader` hasn't read yet."""
        start = self._read_up_to.get(reader, 0)
        self._read_up_to[reader] = len(self._lines)
        new = self._lines[start:]
        if new:
            return ReadAnswer(new)
        if not self._lines:
            return ReadAnswer([], "The scroll is empty, so there was nothing to read.")
        return ReadAnswer([], "Nothing new on the scroll since you last read it.")
