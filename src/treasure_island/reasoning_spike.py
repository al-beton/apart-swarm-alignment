"""A spike: which provider setting holds a model's reasoning to a fixed budget.

`python -m treasure_island.reasoning_spike` plays one short real game per option,
a lone deepseek-v4-flash pirate on a 5 by 5 grid, and prints a Markdown table: the
option, the budget asked for, the reasoning tokens each turn used (median and
most), the share of replies that named a tool, and what it cost. Each option
changes one thing about how the request is sent:

- `adaption-plain`: as the game sends it today, the budget only raising
  `max_output_tokens`.
- `adaption-max-tokens`: adds `extra_body={"reasoning": {"max_tokens": N}}`.
- `adaption-effort-low`: adds `extra_body={"reasoning": {"effort": "low"}}`.
- `adaption-required`: adds `tool_choice="required"`.
- `openrouter-max-tokens`: OpenRouter's documented `reasoning.max_tokens`.
- `openrouter-required`: that, with `tool_choice` "required".

It spends money, so it asks for a yes first (`--yes` skips the question, and
nothing in CI passes it), stops at `--spend-up-to` (0.10 by default, a credit
counting as a dollar, split evenly between the options' games) and plays each game in a temporary folder. Keys come from
the environment, as for a run.

Implements: agents/reasoning-spike
"""

import argparse
import json
import os
import statistics
import sys
import tempfile
import urllib.request

from treasure_island import adaption_backend, openrouter
from treasure_island.backends import BACKENDS, MissingKey
from treasure_island.config import parse_config
from treasure_island.game_loop import GameStopped
from treasure_island.saved_game import Models, write_saved

ADAPTION_MODEL = "deepseek-v4-flash"
OPENROUTER_MODEL = "deepseek/deepseek-v4-flash"
# Option -> (provider, what it adds to the request).
OPTIONS = {
    "adaption-plain": ("adaption", {}),
    "adaption-max-tokens": ("adaption", {"reasoning": "max_tokens"}),
    "adaption-effort-low": ("adaption", {"reasoning": "effort"}),
    "adaption-required": ("adaption", {"tool_choice": "required"}),
    "openrouter-max-tokens": ("openrouter", {}),
    "openrouter-required": ("openrouter", {"tool_choice": "required"}),
}


def _reasoning(budget, how):
    return {"max_tokens": budget} if how == "max_tokens" else {"effort": "low"}


def _tokens(details, name):
    if details is None:
        return 0
    if isinstance(details, dict):
        return details.get(name) or 0
    return getattr(details, name, 0) or 0


class Spike:
    """A backend sending each request the way one option says, noting each turn."""

    def __init__(self, option, client=None, key=None):
        self.provider, self.adds = OPTIONS[option]
        self._client = client
        self._key = key
        self.turns = []  # (reasoning tokens, named a tool, cost)

    def __call__(self, request):
        send = self._adaption if self.provider == "adaption" else self._openrouter
        return send(request)

    def _adaption(self, request):
        extra = {}
        if "reasoning" in self.adds:
            extra["extra_body"] = {
                "reasoning": _reasoning(
                    request["thinking_tokens"], self.adds["reasoning"]
                )
            }
        if "tool_choice" in self.adds:
            extra["tool_choice"] = self.adds["tool_choice"]
        response = self._client.responses.create(
            model=ADAPTION_MODEL,
            instructions=request["system"],
            input=request["messages"],
            tools=[{"type": "function", **tool} for tool in request["tools"]],
            max_output_tokens=request["max_tokens"] + request["thinking_tokens"],
            **extra,
        )
        usage = response.usage
        per_input, per_output = adaption_backend.RATES[ADAPTION_MODEL]
        cost = (usage.input_tokens * per_input + usage.output_tokens * per_output) / (
            1_000_000
        )
        named = any(item.type == "function_call" for item in response.output)
        reasoned = _tokens(
            getattr(usage, "output_tokens_details", None), "reasoning_tokens"
        )
        self.turns.append((reasoned, named, cost))
        return adaption_backend._reply_text(response, request["thinking"]), cost

    def _openrouter(self, request):
        body = openrouter._body(OPENROUTER_MODEL, request)
        body["reasoning"] = {"max_tokens": request["thinking_tokens"]}
        body.update(self.adds)
        sent = urllib.request.Request(
            openrouter.URL,
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {self._key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(sent, timeout=openrouter.TIMEOUT_SECONDS) as answer:
            reply = json.load(answer)
        usage = reply.get("usage") or {}
        cost = float(usage.get("cost") or 0)
        choice = reply["choices"][0]
        named = bool((choice.get("message") or {}).get("tool_calls"))
        reasoned = _tokens(usage.get("completion_tokens_details"), "reasoning_tokens")
        self.turns.append((reasoned, named, cost))
        return openrouter._reply_text(choice, request["thinking"]), cost


def config_for(option, turns, budget):
    """A lone deepseek-v4-flash pirate's game, the one every option plays."""
    provider = OPTIONS[option][0]
    model = (
        f"adaption/{ADAPTION_MODEL}"
        if provider == "adaption"
        else f"openrouter/{OPENROUTER_MODEL}"
    )
    return parse_config(
        {
            "brain": "silent",
            "grid_size": 5,
            "turns_per_pirate": turns,
            "seed": 0,
            "thinking_tokens": budget,
            "pirates": [{"model": model, "thinks": "built-in"}],
        }
    )


def row(option, budget, spike):
    """The table's line for one option's game."""
    used = [reasoned for reasoned, _, _ in spike.turns] or [0]
    named = sum(1 for _, did, _ in spike.turns if did)
    share = f"{named}/{len(spike.turns)}" if spike.turns else "0/0"
    cost = sum(cost for _, _, cost in spike.turns)
    return (
        f"| {option} | {budget} | {statistics.median(used):g} | {max(used)} "
        f"| {share} | {cost:.5f} |"
    )


HEADER = (
    "| option | budget | reasoning tokens (median) | reasoning tokens (most) "
    "| replies with a tool call | cost |\n|---|---|---|---|---|---|"
)


def play(option, turns, budget, spike, cap):
    """Play one option's game in a temporary folder; return its table line."""
    config = config_for(option, turns, budget)
    models = Models(backend=spike, cache=False, cap_usd=cap, agree=lambda: True)
    with tempfile.TemporaryDirectory() as folder:
        try:
            write_saved(config, folder, models=models)
        except GameStopped as why:  # the game itself catches its own stops
            print(f"{option} stopped: {why}", file=sys.stderr)
    return row(option, budget, spike)


def _key(provider):
    variable = BACKENDS[f"{provider}/"][1]
    if not os.environ.get(variable):
        raise MissingKey(f"Set {variable} to try the {provider} options.")
    return os.environ[variable]


def _spike_for(option):
    provider = OPTIONS[option][0]
    if provider == "adaption":
        return Spike(option, client=adaption_backend.client(_key(provider)))
    return Spike(option, key=_key(provider))


def main(argv=None, ask=input):
    parser = argparse.ArgumentParser(prog="python -m treasure_island.reasoning_spike")
    parser.add_argument("--options", nargs="+", choices=OPTIONS, default=list(OPTIONS))
    parser.add_argument("--turns", type=int, default=20)
    parser.add_argument("--budget", type=int, default=1024)
    parser.add_argument("--spend-up-to", type=float, default=0.10)
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args(argv)
    calls = len(args.options) * args.turns * 2
    print(f"This spike can make up to {calls} model calls.", flush=True)
    if not args.yes and ask(
        "Spend on them? Type yes to go on: "
    ).strip().lower() not in (
        "y",
        "yes",
    ):
        print("Nothing was spent.", file=sys.stderr)
        return 1
    lines = [HEADER]
    cap = args.spend_up_to / len(args.options)  # the cap is shared by every game
    for option in args.options:
        spike = _spike_for(option)
        lines.append(play(option, args.turns, args.budget, spike, cap))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
