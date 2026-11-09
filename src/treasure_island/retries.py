"""Model calls that drop are tried again, with backoff, before a live run gives up.

A dropped connection, a DNS failure, a timeout, a reply cut off part way
(`http.client.IncompleteRead` and the like), a 5xx answer or a rate limit (a 429,
which a wave of parallel games hits) is the network's fault, not the model's, so `Retrying` tries the call again after `WAITS` seconds,
5 tries over about a minute (default, Al to confirm). Anything else, a 4xx answer
say, is raised at once. After the last try the game stops, saying how to resume:
the same command again plays the run back from the replies it already got.

`last_retries` says how many times the last call was tried again, so the stored
reply can keep it and the story can say so on that turn, live and on replay.

Implements: treasure-island/retries-dropped-calls
"""

import http.client
import time
import urllib.error

from treasure_island.game_loop import GameStopped

WAITS = (4, 8, 16, 32)  # seconds before each try after the first
RATE_LIMITED = 429  # too many calls at once: the same call works again after a wait
_sleep = time.sleep  # tests stand in for it, so they never wait
# The SDKs' own names for a network failure, so no SDK is imported here.
_DROPPED = {"APIConnectionError", "APITimeoutError", "InternalServerError"}


def dropped(error):
    """Whether this error is the network's fault, so the same call may work again."""
    if isinstance(error, urllib.error.HTTPError):
        return error.code >= 500 or error.code == RATE_LIMITED
    # HTTPException: the connection broke while the reply was being read.
    network = (urllib.error.URLError, TimeoutError, ConnectionError)
    if isinstance(error, (*network, http.client.HTTPException)):
        return True
    if type(error).__name__ in _DROPPED:
        return True
    status = getattr(error, "status_code", 0)
    return status >= 500 or status == RATE_LIMITED


class Retrying:
    """A backend that tries a dropped call again, and stops the game after the last."""

    def __init__(self, backend):
        self._backend = backend
        self.last_retries = 0

    def __call__(self, request):
        self.last_retries = 0
        for wait in (*WAITS, None):
            try:
                return self._backend(request)
            except Exception as error:
                if not dropped(error):
                    raise
                if wait is None:
                    raise GameStopped(
                        f"its model call dropped {len(WAITS) + 1} times "
                        f"({type(error).__name__}), so run the same command again "
                        "to resume: the replies it already got are reused"
                    ) from error
                self.last_retries += 1
                _sleep(wait)
        raise AssertionError("unreachable")
