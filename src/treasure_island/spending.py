"""What a run may spend: an estimate before it starts, a yes, and a cap.

`estimate` counts the most model calls a crew can make: every turn of each pirate
with a model, twice over for the one retry after a bad reply. It also counts the
replies earlier runs got from those pirates with this seed, and makes an upper
estimate of tokens, taking each earlier turn in a request as up to 300 characters
and four characters to a token. Where every model's price is known, it gives the
most that could cost, in each provider's own unit: dollars, or Adaption's
credits. A cost under a cent keeps its first two significant digits.

`Guard` wraps a run's backend, which `Replies` only calls for a reply nothing has
stored, so a cached reply costs nothing and counts nothing against the cap. It asks
for a yes before the first call, and stops the game once the run has spent its cap,
so a run overshoots by one reply at most; the cap counts a credit as a dollar.
Anything but a yes raises `Declined`, and the run's folder is removed.

Implements: treasure-island/end-report, agents/adaption-cost, runs/cost-before-run, runs/yes-before-spending, runs/spending-cap, runs/cached-is-free, runs/stops-cleanly
"""

import dataclasses
import json
import math

from treasure_island.backends import bills_in, price_for
from treasure_island.brain import system_prompt
from treasure_island.game_loop import GameStopped
from treasure_island.llm import TOOL_DEFINITIONS
from treasure_island.runs import earlier_rows

TURN_CHARS = 300  # an earlier turn's line in a request, at most, for the estimate
CHARS_PER_TOKEN = 4
CAP_USD = 1.0  # default, Al to confirm


@dataclasses.dataclass(frozen=True)
class Estimate:
    calls: int
    cached: int
    tokens: int
    costs: dict | None  # unit ("dollars" or "credits") -> the most it could cost
    unpriced: tuple

    def as_text(self, cap_usd):
        found = (
            f"This crew can make up to {self.calls} model calls (each pirate with "
            "a model, every try at every turn, as a failed move or a reply that "
            "isn't a tool call tries again). Earlier runs hold "
            f"{self.cached} replies from these pirates with this seed, and those "
            f"cost nothing. At most about {self.tokens} tokens"
        )
        if self.costs is not None:
            amounts = " and ".join(
                in_unit(self.costs[unit], unit)
                for unit in sorted(self.costs, reverse=True)
            )
            return f"{found}, costing at most {amounts}."
        models = ", ".join(self.unpriced)
        return (
            f"{found}. There's no price for {models}, so only the spending cap of "
            f"${cap_usd:.2f} limits what it costs."
        )


def in_unit(amount, unit="dollars"):
    """An amount as text, a sub-cent one to its first two significant digits."""
    places = 2
    if 0 < amount < 0.01:
        places = 1 - math.floor(math.log10(amount))
    if unit == "credits":
        return f"{amount:.{places}f} Adaption credits"
    return f"${amount:.{places}f}"


def estimate(config):
    """The most a run of this config can ask its models, and what that could cost."""
    with_models = [
        (f"pirate-{index + 1}", pirate.model)
        for index, pirate in enumerate(config.pirates)
        if pirate.model
    ]
    # A failed action, a bad reply included, asks again in the same turn.
    tries = config.turns_per_pirate * config.failed_tries
    per_pirate = tries + (1 if config.end_report else 0)  # the end report's note
    fixed = len(system_prompt(config)) + len(json.dumps(TOOL_DEFINITIONS))
    # Each reply, and the model's own reasoning on top, thinking on or off.
    out = config.reply_tokens + config.thinking_tokens
    # Every try, failed or not, adds a line to the pirate's own earlier turns.
    asked = math.ceil((fixed + tries * TURN_CHARS) / CHARS_PER_TOKEN)
    wanted = {(name, model) for name, model in with_models}
    cached = sum(
        1
        for row in earlier_rows()
        if (row["request"].get("agent"), row["request"].get("model")) in wanted
        and row["request"].get("seed") == config.seed
    )
    prices = {model: price_for(model) for _, model in with_models}
    unpriced = tuple(sorted(model for model, price in prices.items() if not price))
    costs = None
    if not unpriced:
        costs = {}
        for _, model in with_models:
            rate_in, rate_out = prices[model]
            cost = per_pirate * (asked * rate_in + out * rate_out) / 1_000_000
            costs[bills_in(model)] = costs.get(bills_in(model), 0) + cost
    calls = per_pirate * len(with_models)
    tokens = calls * (asked + out)
    return Estimate(calls, min(cached, calls), tokens, costs, unpriced)


class Declined(GameStopped):
    """Nobody said yes to spending, so the run stopped before it spent anything."""

    declined = True  # a stop the whole run honours, end notes included


class Guard:
    """A backend that spends only after a yes, and only up to its cap."""

    def __init__(self, backend, cap_usd, agree):
        self._backend = backend
        self._cap = cap_usd
        self._agree = agree
        self._agreed = None
        self.spent = 0.0  # a credit counted as a dollar, for the cap
        self.spent_in = {"dollars": 0.0, "credits": 0.0}

    @property
    def declined(self):
        """True once anything but a yes was the answer."""
        return self._agreed is False

    def __call__(self, request):
        if self._agreed is None:
            self._agreed = bool(self._agree and self._agree())
        if not self._agreed:
            raise Declined(
                "nobody said yes to spending money, so no model was asked anything"
            )
        if self.spent >= self._cap:
            raise GameStopped(
                f"it had spent ${self.spent:.2f}, which reached its spending cap "
                f"of ${self._cap:.2f}"
            )
        text, cost = self._backend(request)
        self.spent += cost
        self.spent_in[bills_in(request["model"])] += cost
        return text, cost
