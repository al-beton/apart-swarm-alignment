"""Model calls that drop are tried again, with backoff, before a live run gives up.

A dropped connection, a DNS failure, a timeout, a reply cut off part way
(`http.client.IncompleteRead`, a stream the server closes and the like) or a 5xx answer is the network's
fault, not the model's, so `Retrying` tries the call again after `WAITS` seconds,
5 tries over about a minute (default, Al to confirm). Anything else, a 4xx answer
say, is raised at once. After the last try the game stops, saying how to resume:
the same command again plays the run back from the replies it already got.

A rate limit (a 429) is the server asking for a pause, so it waits
`RATE_LIMIT_WAIT` seconds and tries again, up to `RATE_LIMIT_TRIES` times, apart
from the drop tries (default, Edu to confirm): several games played at once
then slow each other down instead of stopping.

`last_retries` says how many times the last call was tried again, so the stored
reply can keep it and the story can say so on that turn, live and on replay.

Implements: treasure-island/retries-dropped-calls
"""

import http.client
import time
import urllib.error

from treasure_island.game_loop import GameStopped

WAITS = (4, 8, 16, 32)  # seconds before each try after the first
RATE_LIMIT_WAIT = 60  # Adaption's 429 says "retry after 60 seconds"
RATE_LIMIT_TRIES = 30
_sleep = time.sleep  # tests stand in for it, so they never wait
# The SDKs' own names for a network failure, so no SDK is imported here; httpx's
# `TransportError` covers a streamed reply the server closes part way.
_DROPPED = {
    "APIConnectionError",
    "APITimeoutError",
    "InternalServerError",
    "TransportError",
}


def rate_limited(error):
    """Whether the server asked for a pause (a 429), so the call should wait."""
    if isinstance(error, urllib.error.HTTPError):
        return error.code == 429
    if any(kind.__name__ == "RateLimitError" for kind in type(error).__mro__):
        return True
    return getattr(error, "status_code", 0) == 429


def dropped(error):
    """Whether this error is the network's fault, so the same call may work again."""
    if isinstance(error, urllib.error.HTTPError):
        return error.code >= 500
    # HTTPException: the connection broke while the reply was being read.
    network = (urllib.error.URLError, TimeoutError, ConnectionError)
    if isinstance(error, (*network, http.client.HTTPException)):
        return True
    if any(kind.__name__ in _DROPPED for kind in type(error).__mro__):
        return True
    return getattr(error, "status_code", 0) >= 500


class Retrying:
    """A backend that tries a dropped call again, and stops the game after the last."""

    def __init__(self, backend):
        self._backend = backend
        self.last_retries = 0

    def __call__(self, request):
        self.last_retries = 0
        waits, limits = iter(WAITS), 0
        while True:
            try:
                return self._backend(request)
            except Exception as error:
                if rate_limited(error):
                    limits += 1
                    if limits > RATE_LIMIT_TRIES:
                        raise GameStopped(
                            f"its model call hit the rate limit {limits} times, "
                            "so run the same command again to resume: the replies "
                            "it already got are reused"
                        ) from error
                    self.last_retries += 1
                    _sleep(RATE_LIMIT_WAIT)
                    continue
                if not dropped(error):
                    raise
                wait = next(waits, None)
                if wait is None:
                    raise GameStopped(
                        f"its model call dropped {len(WAITS) + 1} times "
                        f"({type(error).__name__}), so run the same command again "
                        "to resume: the replies it already got are reused"
                    ) from error
                self.last_retries += 1
                _sleep(wait)
