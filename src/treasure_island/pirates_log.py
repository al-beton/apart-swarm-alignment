"""The pirates' log: the short shared record that is all they can see of each other.

Lines count up from 1 and look like the event log's `log_shown` entries. Every
turn adds exactly one line, because each of the three calls that spend a turn
adds one: `write` adds the note, and `read` and `pass_turn` add a blank line.
So a read costs the turn it took, and pushes older lines out of the free
`window`, which costs nothing to look at. A line number outside this log gets a
message and no lines.

Implements: treasure-island/short-window, treasure-island/every-turn-a-line, treasure-island/reading-costs, treasure-island/read-size
"""

import dataclasses


@dataclasses.dataclass(frozen=True)
class ReadAnswer:
    """The lines a read found, or a message saying why it found none."""

    lines: list
    message: str = ""


class PiratesLog:
    def __init__(self, window=3, read_size=3):
        self._window = window
        self._read_size = read_size
        self._texts = []

    def _lines(self, first, last):
        """Lines `first` to `last` inclusive, by line number."""
        return [
            {"line": number, "text": self._texts[number - 1]}
            for number in range(first, last + 1)
        ]

    def window(self):
        """The last few lines, free to every pirate at the start of its turn."""
        total = len(self._texts)
        return self._lines(max(1, total - self._window + 1), total)

    def write(self, note):
        """Spend the turn on a note. A note always stays on one line."""
        self._texts.append(" ".join(note.splitlines()))

    def pass_turn(self):
        """A turn spent on anything but the log adds a blank line."""
        self._texts.append("")

    def read(self, line):
        """Spend the turn reading the lines around `line`."""
        answer = self._look_up(line)
        self.pass_turn()
        return answer

    def _look_up(self, line):
        total = len(self._texts)
        if not 1 <= line <= total:
            return ReadAnswer(
                [], f"Line {line} is not in this log, so nothing to read."
            )
        # Keep a full read at either end of the log, where it can't be centred.
        first = min(line - (self._read_size - 1) // 2, total - self._read_size + 1)
        first = max(1, first)
        return ReadAnswer(self._lines(first, min(total, first + self._read_size - 1)))
