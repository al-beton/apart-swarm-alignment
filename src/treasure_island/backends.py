"""Where a model's reply comes from: `backend(request)` -> (text, cost in USD).

No model is plugged in yet, and scripted brains don't come through here, so every
model is refused and nothing can spend money until a backend is added on purpose.

Implements: agents/backend-interface, agents/no-model-yet
"""


class UnknownModel(ValueError):
    """No backend serves this model."""


def backend_for(model):
    """A fresh backend for one run of this model."""
    raise UnknownModel(f"No backend serves the model '{model}'.")
