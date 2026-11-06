"""Where a request's reply comes from: `backend(request)` -> (text, cost in USD).

Only scripted models exist so far, and they're free. Any other model is refused,
so nothing can spend money until a real backend is added here on purpose.

Implements: runs/walking-skeleton
"""

import hashlib
import random


class UnknownModel(ValueError):
    """No backend serves this model."""


def _random_walker(request):
    """A free stand-in for a model: a random action, fixed by seed and prompt."""
    text = f"{request['seed']}\n{request['prompt']}"
    rng = random.Random(hashlib.sha256(text.encode()).hexdigest())
    moves = ["move north", "move east", "move south", "move west", "dig"]
    return rng.choice(moves), 0.0


_SCRIPTED = {"scripted/random": _random_walker}


def backend_for(model):
    if model not in _SCRIPTED:
        raise UnknownModel(f"No backend serves the model '{model}'.")
    return _SCRIPTED[model]
