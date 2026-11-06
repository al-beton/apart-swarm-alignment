"""The pirates' log: the one channel between pirates, as they see it.

Lines are numbered from 1. Every turn adds exactly one line, through one of
three calls: `write` adds the pirate's note, `blank` adds an empty line for a
turn spent moving or digging, and `read` adds an empty line too, because a read
is the turn's action, so looking back costs what a dig would have. `shown` is
the free window at the start of a turn and adds nothing.

A read returns the lines around the chosen line, clipped to the log. A line
outside this session's log raises `LineOutOfRange` with a message the pirate
can be given, and nothing else, so an out-of-range number leaks no line. That
read still costs the turn (default, Al to confirm, like a failed move).

Implements: treasure-island/short-window, treasure-island/every-turn-a-line, treasure-island/reading-costs, treasure-island/read-size
"""


class LineOutOfRange(LookupError):
    """A read asked for a line this session's log doesn't have."""


class PirateLog:
    def __init__(self, window=3, read_size=3):
        self.window = window
        self.read_size = read_size
        self._texts = []

    def lines(self):
        """Every line so far, each as its number and text."""
        return [
            {"line": number, "text": text}
            for number, text in enumerate(self._texts, start=1)
        ]

    def write(self, text):
        """The turn's note. Returns the line number it got."""
        self._texts.append(text)
        return len(self._texts)

    def blank(self):
        """A turn spent on something other than writing. Returns its line number."""
        return self.write("")

    def shown(self):
        """The last `window` lines, free at the start of every turn."""
        return self.lines()[len(self._texts) - self.window :] if self.window else []

    def read(self, number):
        """The `read_size` lines around line `number`. Costs the turn."""
        lines = self.lines()
        self.blank()
        if not 1 <= number <= len(lines):
            extent = f"has lines 1 to {len(lines)}" if lines else "is empty"
            raise LineOutOfRange(
                f"Line {number} is outside this session's log, which {extent}."
            )
        start = number - 1 - (self.read_size - 1) // 2
        return lines[max(start, 0) : start + self.read_size]
