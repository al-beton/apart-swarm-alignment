"""Where a model's reply comes from: `backend(request)` -> (text, cost in USD).

No model is plugged in yet, and scripted brains don't come through here, so every
model is refused and nothing can spend money until a backend is added on purpose.
A backend that knows its model's price adds it to `PRICES`, so a run can say what
it may cost before it starts.

Implements: agents/backend-interface, agents/no-model-yet, runs/cost-before-run
"""

# Model name -> (USD per million input tokens, USD per million output tokens).
PRICES = {}


def price_for(model):
    """The model's price per million tokens, in and out, or None if not known."""
    return PRICES.get(model)


class UnknownModel(ValueError):
    """No backend serves this model."""


def backend_for(model):
    """A fresh backend for one run of this model."""
    raise UnknownModel(f"No backend serves the model '{model}'.")
