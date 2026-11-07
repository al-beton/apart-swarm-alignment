"""What a run may spend: an estimate before it starts, a yes, and a cap.

`estimate` counts the most model calls a crew can make: every turn of each pirate
with a model, twice over for the one retry after a bad reply. It also counts the
replies earlier runs got from those pirates with this seed, and makes an upper
estimate of tokens, taking each earlier turn in a request as up to 300 characters
and four characters to a token. Where every model's price is known, it gives the
most that could cost.

`Guard` wraps a run's backend, which `Replies` only calls for a reply nothing has
stored, so a cached reply costs nothing and counts nothing against the cap. It asks
for a yes before the first call, and stops the game once the run has spent its cap,
so a run overshoots by one reply at most.

Implements: runs/cost-before-run, runs/yes-before-spending, runs/spending-cap, runs/cached-is-free, runs/stops-cleanly
"""

import dataclasses
import json
import math

from treasure_island.backends import price_for
from treasure_island.brain import system_prompt
from treasure_island.game_loop import GameStopped
from treasure_island.llm import ASKS, TOOL_DEFINITIONS
from treasure_island.runs import earlier_rows

TURN_CHARS = 300  # an earlier turn's line in a request, at most, for the estimate
CHARS_PER_TOKEN = 4
CAP_USD = 1.0  # default, Al to confirm


@dataclasses.dataclass(frozen=True)
class Estimate:
    calls: int
    cached: int
    tokens: int
    cost_usd: float | None
    unpriced: tuple

    def as_text(self, cap_usd):
        found = (
            f"This crew can make up to {self.calls} model calls (each pirate with "
            "a model, every try at every turn, as a failed move tries again, and "
            "once more after a reply that isn't a tool call). Earlier runs hold {self.cached} replies from these pirates with "
            f"this seed, and those cost nothing. At most about {self.tokens} tokens"
        )
        if self.cost_usd is not None:
            return f"{found}, costing at most ${self.cost_usd:.2f}."
        models = ", ".join(self.unpriced)
        return (
            f"{found}. There's no price for {models}, so only the spending cap of "
            f"${cap_usd:.2f} limits what it costs."
        )


def estimate(config):
    """The most a run of this config can ask its models, and what that could cost."""
    with_models = [
        (f"pirate-{index + 1}", pirate.model)
        for index, pirate in enumerate(config.pirates)
        if pirate.model
    ]
    # A failed move asks again in the same turn, and each try can ask twice.
    tries = config.turns_per_pirate * config.failed_tries
    per_pirate = tries * ASKS
    fixed = len(system_prompt(config)) + len(json.dumps(TOOL_DEFINITIONS))
    retry = config.reply_tokens * CHARS_PER_TOKEN + TURN_CHARS
    # Every try, failed or not, adds a line to the pirate's own earlier turns.
    asked = math.ceil((fixed + tries * TURN_CHARS + retry) / CHARS_PER_TOKEN)
    wanted = {(name, model) for name, model in with_models}
    cached = sum(
        1
        for row in earlier_rows()
        if (row["request"].get("agent"), row["request"].get("model")) in wanted
        and row["request"].get("seed") == config.seed
    )
    prices = {model: price_for(model) for _, model in with_models}
    unpriced = tuple(sorted(model for model, price in prices.items() if not price))
    cost = None
    if not unpriced:
        cost = sum(
            per_pirate
            * (asked * prices[model][0] + config.reply_tokens * prices[model][1])
            / 1_000_000
            for _, model in with_models
        )
    calls = per_pirate * len(with_models)
    tokens = calls * (asked + config.reply_tokens)
    return Estimate(calls, min(cached, calls), tokens, cost, unpriced)


class Guard:
    """A backend that spends only after a yes, and only up to its cap."""

    def __init__(self, backend, cap_usd, agree):
        self._backend = backend
        self._cap = cap_usd
        self._agree = agree
        self._agreed = None
        self.spent = 0.0

    def __call__(self, request):
        if self._agreed is None:
            self._agreed = bool(self._agree and self._agree())
        if not self._agreed:
            raise GameStopped(
                "nobody said yes to spending money, so no model was asked anything"
            )
        if self.spent >= self._cap:
            raise GameStopped(
                f"it had spent ${self.spent:.2f}, which reached its spending cap "
                f"of ${self._cap:.2f}"
            )
        text, cost = self._backend(request)
        self.spent += cost
        return text, cost
