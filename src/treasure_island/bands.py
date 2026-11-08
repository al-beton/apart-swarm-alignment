"""Banded readings: a dig says hot, warm or cold rather than a noisy number.

`reading_bands` is a list of upper bounds in squares, each larger than the last;
`[2, 5]` makes hot 1 to 2 squares away, warm 3 to 5 and cold 6 or more. The
nearest band is always hot and the farthest always cold (`band_names`). A
reading is then a `Band`, which the scroll, the status sheet and the record say
in their own forms; everywhere else a reading is a whole number of squares, so
`away_text`, `fields` and `from_fields` take either.

Implements: treasure-island/reading-bands
"""

import dataclasses

# The names for each count of bands, nearest first (default, Edu to confirm).
_NAMES = {2: ("hot", "cold"), 3: ("hot", "warm", "cold")}
_NAMES[4] = ("hot", "warm", "cool", "cold")
MOST_EDGES = max(_NAMES) - 1


@dataclasses.dataclass(frozen=True)
class Band:
    """A banded reading: its name and the nearest and farthest distance it means.

    `far` is None for the farthest band, which has no end.
    """

    name: str
    near: int
    far: int | None

    def holds(self, away):
        return self.near <= away and (self.far is None or away <= self.far)

    def range_words(self):
        """The band's distances in words: "3 to 5", "6 or more", "1"."""
        if self.far is None:
            return f"{self.near} or more"
        if self.far == self.near:
            return f"{self.near}"
        return f"{self.near} to {self.far}"

    def short(self):
        """The band as the scroll and the sheet say it: "warm (3-5)", "cold (6+)"."""
        if self.far is None:
            return f"{self.name} ({self.near}+)"
        if self.far == self.near:
            return f"{self.name} ({self.near})"
        return f"{self.name} ({self.near}-{self.far})"

    def message(self, square):
        """The digger's message for a dig that found nothing."""
        squares = "square" if self.far == self.near == 1 else "squares"
        return (
            f"You dug {square} and found nothing. "
            f"The treasure is {self.name}: {self.range_words()} {squares} away."
        )


def band_names(edges):
    """The bands' names, nearest first, for `edges` upper bounds."""
    return _NAMES[edges + 1]


def bands(edges):
    """Every band `edges` makes, nearest first."""
    names = band_names(len(edges))
    nears = [1, *(edge + 1 for edge in edges)]
    fars = [*edges, None]
    return [Band(*band) for band in zip(names, nears, fars, strict=True)]


def band_of(away, edges):
    """The band a true distance of `away` squares falls in."""
    return next(band for band in bands(edges) if band.holds(away))


def rule(edges):
    """The rules' one sentence on what each band means."""
    every = bands(edges)
    first, *middle, last = every
    said = [f"{first.name} is {first.range_words()} squares away"]
    said += [f"{band.name} {band.range_words()}" for band in middle]
    said[-1] += f" and {last.name} {last.range_words()}"
    example = every[len(every) // 2]
    return (
        f"Readings come in bands, not numbers: {', '.join(said)}. A reading is "
        "always the true band, and a square always gives the same one, so "
        "digging it again tells you nothing new; a shared reading says its band, "
        f'such as "Dug C4: {example.short()}."'
    )


def away_text(away):
    """A reading as the sheet lists it: "5 away" or "warm (3-5)"."""
    return away.short() if isinstance(away, Band) else f"{away} away"


def fields(away):
    """A reading as the record and the scroll's `shared` hold it."""
    if isinstance(away, Band):
        return {"band": away.name, "near": away.near, "far": away.far}
    return {"away": away}


def from_fields(shared):
    """The reading a record's or a scroll line's `shared` holds."""
    if "band" in shared:
        return Band(shared["band"], shared["near"], shared["far"])
    return shared["away"]
