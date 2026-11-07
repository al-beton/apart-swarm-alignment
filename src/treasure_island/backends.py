"""Where a model's reply comes from: `backend(request)` -> (text, cost in USD).

A model is served only by a backend added here on purpose, named by the start of
the model's name, so nothing can spend money by accident. Each backend reads its
key from one environment variable, which `.env.example` names, and a missing key
is refused when the backend is made, before any game starts. A backend that knows
its model's price adds it to `PRICES`, so a run can say what it may cost before it
starts; OpenRouter's prices vary by model, so its replies' own costs are counted,
and Adaption's rates are listed in adaption_backend. Each backend's `THINKS`
says which way its models think (`treasure-island/model-reasoning`).

Implements: treasure-island/model-reasoning, agents/check-keys, agents/backend-interface, agents/no-model-yet, agents/openrouter-backend, agents/adaption-backend, agents/adaption-cost, agents/key-from-the-environment, runs/cost-before-run
"""

import os

from treasure_island import adaption_backend
from treasure_island.config import ConfigError
from treasure_island.openrouter import OpenRouter

# Model name -> (USD per million input tokens, USD per million output tokens).
PRICES = {}


def _adaption(model_id, key):
    if model_id not in adaption_backend.RATES:
        raise UnknownModel(
            f"There's no listed rate for adaption/{model_id}, so its cost can't "
            "be counted; add its rate to RATES in adaption_backend.py."
        )
    return adaption_backend.AdaptionBackend(model_id, adaption_backend.client(key))


_adaption.check_key = adaption_backend.check_key  # for check-keys, like OpenRouter's
_adaption.THINKS = adaption_backend.THINKS


# Model-name prefix -> (the backend, the environment variable holding its key)
BACKENDS = {
    "openrouter/": (OpenRouter, "OPENROUTER_API_KEY"),
    "adaption/": (_adaption, "ADAPTION_API_KEY"),
}


def thinking_way(model):
    """How this model thinks: "built-in" reasoning, or a thought "in-reply".

    A model no backend serves (only a test's fake gets that far) writes its
    thought in its reply, since that works with any model.
    """
    for prefix, (backend, _) in BACKENDS.items():
        if model.startswith(prefix):
            return backend.THINKS
    return "in-reply"


def price_for(model):
    """The model's price per million tokens, in and out, or None if not known."""
    if model.startswith("adaption/"):  # credits, counted as dollars
        return adaption_backend.RATES.get(model.removeprefix("adaption/"))
    return PRICES.get(model)


class UnknownModel(ConfigError):
    """No backend serves this model."""


class MissingKey(ConfigError):
    """The backend for this model has no key to call with."""


def backend_for(model):
    """A fresh backend for one run of this model."""
    for prefix, (backend, variable) in BACKENDS.items():
        model_id = model.removeprefix(prefix)
        if model.startswith(prefix) and model_id:
            key = os.environ.get(variable)
            if not key:
                raise MissingKey(f"Set {variable} to play the model '{model}'.")
            return backend(model_id, key)
    raise UnknownModel(f"No backend serves the model '{model}'.")
