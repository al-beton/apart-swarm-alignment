"""Where a request's reply comes from: `backend(request)` -> (text, cost in USD).

Scripted and model agents share this one interface, so the game can't tell
them apart. Only scripted agents exist so far, and they're free. Any other
model is refused, so nothing can spend money until a real backend is added
here on purpose.

Implements: agents/one-interface
"""

from treasure_island.agents import SCRIPTED


class UnknownModel(ValueError):
    """No backend serves this model."""


def backend_for(model):
    """A fresh backend for one run of this model."""
    if model not in SCRIPTED:
        raise UnknownModel(f"No backend serves the model '{model}'.")
    return SCRIPTED[model]()
