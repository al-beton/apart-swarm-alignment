"""`treasure-island check-keys`: whether each model backend's key works, for free.

Every backend in `backends.BACKENDS` gets one line: its key isn't set, or what its
`check_key` found. A backend's check asks its provider about the key, never a
model, so it spends nothing, and no line ever holds any part of a key.

Implements: agents/check-keys
"""

import os

from treasure_island.backends import BACKENDS


def check_keys(environ=os.environ):
    """One line per backend, and whether any key that is set doesn't work."""
    lines, failed = [], False
    for prefix, (backend, variable) in BACKENDS.items():
        name = prefix.rstrip("/")
        key = environ.get(variable)
        if not key:
            lines.append(f"{name}: {variable} isn't set.")
            continue
        works, said = backend.check_key(key)
        lines.append(f"{name}: {variable} {said}")
        failed = failed or not works
    return lines, failed
