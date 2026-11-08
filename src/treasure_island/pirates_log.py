"""The pirates' log is a scroll: lines said for free, shown when a pirate is asked.

Saying adds one line, numbered from 1, saying who wrote it, on which turn of the
game (counted from 1, as the pirates are told it) and whether it is an alert. A
turn that says nothing adds nothing, so the scroll holds only what pirates chose
to say. Reading isn't an action: each time a pirate is asked, `unseen` hands it
every line it hasn't been shown yet, its own included, and moves its place to the
end. Each line looks like the event log's `log_shown` entries, with `by` naming
the writer.

Implements: treasure-island/share-reading, treasure-island/every-turn-a-line, treasure-island/shown-when-asked, treasure-island/say-on-any-action, treasure-island/alert
"""


def one_line(note):
    """A note as the scroll holds it: one line, however it was written."""
    return " ".join(note.splitlines())


def shared_text(square, away):
    """The fixed words of a shared reading (`share-reading`): "Dug C4: 5 away."."""
    return f"Dug {square}: {away} away."


def line_text(line):
    """A scroll line as `pirates-log.txt` says it: number, who, turn, marks, words."""
    marks = f"turn {line['turn']}" + (", alert" if line.get("alert") else "")
    marks += ", shared" if line.get("shared") else ""
    return f"{line['line']} {line['by']} ({marks}): {line['text']}"


class PiratesLog:
    def __init__(self):
        self._lines = []
        self._shown_up_to = {}

    def lines(self):
        """Every line so far, for our own records. Pirates see what they're shown."""
        return list(self._lines)

    def say(self, by, text, turn, alert=False, shared=None):
        """Add a said line. It always stays on one line.

        A dig's shared reading (`share-reading`) is a line too, written by the
        game in the digger's name, carrying `shared`: its square and reading.
        """
        line = {"line": len(self._lines) + 1, "text": one_line(text), "by": by}
        line |= {"turn": turn, "alert": bool(alert)}
        if shared is not None:
            line["shared"] = shared
        self._lines.append(line)
        return line

    def unseen(self, reader):
        """Every line `reader` hasn't been shown yet; from now on it has been."""
        start = self._shown_up_to.get(reader, 0)
        self._shown_up_to[reader] = len(self._lines)
        return self._lines[start:]
