"""Where a model's reply comes from: `backend(request)` -> (text, cost in USD).

A model is served only by a backend added here on purpose, named by the start of
the model's name, so nothing can spend money by accident. Each backend reads its
key from one environment variable, which `.env.example` names, and a missing key
is refused when the backend is made, before any game starts. A backend that knows
its model's price adds it to `PRICES`, so a run can say what it may cost before it
starts; OpenRouter's prices vary by model, so its replies' own costs are counted.

Implements: agents/backend-interface, agents/no-model-yet, agents/openrouter-backend, agents/key-from-the-environment, runs/cost-before-run
"""

import os

from treasure_island.config import ConfigError
from treasure_island.openrouter import OpenRouter

# Model name -> (USD per million input tokens, USD per million output tokens).
PRICES = {}

# Model-name prefix -> (the backend, the environment variable holding its key)
BACKENDS = {"openrouter/": (OpenRouter, "OPENROUTER_API_KEY")}


def price_for(model):
    """The model's price per million tokens, in and out, or None if not known."""
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
