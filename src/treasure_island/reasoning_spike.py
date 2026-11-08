"""A small experiment: how much deepseek-v4-flash reasons for each budget we tell it.

`python -m treasure_island.reasoning_spike` plays the same short game, a lone
deepseek-v4-flash pirate on Adaption on a 5 by 5 grid, once for each cell: a
thinking budget of 1024, 2048 or 4096 tokens, with the budget sentence in the
prompt or without it (`budget_sentence`). It goes through the game's own Adaption
backend, so each request is exactly what a run sends, and prints a Markdown table
read from each game's own record: the reasoning tokens each turn used (median and
most), the replies the token limit cut off, the replies that weren't tool calls,
the turns that passed with no action, and what it cost in Adaption credits.

It spends credits, so it asks for a yes first (`--yes` skips the question, and
nothing in CI passes it), stops at `--spend-up-to` (0.10 by default, split evenly
between the cells) and plays each game in a temporary folder, so it keeps no run.
The key comes from `ADAPTION_API_KEY`, as for a run.

Implements: agents/reasoning-spike
"""

import argparse
import json
import statistics
import sys
import tempfile
from pathlib import Path

from treasure_island.backends import backend_for
from treasure_island.config import parse_config
from treasure_island.saved_game import Models, write_saved

MODEL = "adaption/deepseek-v4-flash"
BUDGETS = (1024, 2048, 4096)
HEADER = (
    "| budget | sentence | reasoning tokens (median) | reasoning tokens (most) "
    "| cut off | not a tool call | turns lost | credits |\n"
    "|---|---|---|---|---|---|---|---|"
)


def config_for(budget, sentence, turns):
    """The game every cell plays, differing only in its budget and the sentence."""
    return parse_config(
        {
            "brain": "silent",
            "grid_size": 5,
            "turns_per_pirate": turns,
            "seed": 0,
            "thinking_tokens": budget,
            "budget_sentence": sentence,
            "pirates": [{"model": MODEL, "thinks": "built-in"}],
        }
    )


def _cut_off(reply):
    try:
        return json.loads(reply).get("cut_off") is True
    except (json.JSONDecodeError, AttributeError):
        return False


def row(budget, sentence, folder):
    """The table's line for one cell's game, read from its record."""
    folder = Path(folder)
    lines = (folder / "events.jsonl").read_text().splitlines()
    records = [json.loads(line) for line in lines]
    spent = [r["reasoning_tokens"] for r in records if "reasoning_tokens" in r]
    refused = [bad for record in records for bad in record.get("refused", [])]
    cut = sum(1 for bad in refused if _cut_off(bad["reply"]))
    lost = sum(1 for record in records if not record.get("did"))
    manifest = json.loads((folder / "manifest.json").read_text())
    median = f"{statistics.median(spent):g}" if spent else "-"
    most = max(spent) if spent else "-"
    credits = manifest.get("cost_credits", 0)
    return (
        f"| {budget} | {'yes' if sentence else 'no'} | {median} | {most} "
        f"| {cut} | {len(refused)} | {lost} | {credits:.5f} |"
    )


def play(budget, sentence, turns, models):
    """Play one cell's game in a temporary folder; return its table line."""
    with tempfile.TemporaryDirectory() as folder:
        write_saved(config_for(budget, sentence, turns), folder, models=models)
        return row(budget, sentence, folder)


def main(argv=None, ask=input, backend=None):
    parser = argparse.ArgumentParser(prog="python -m treasure_island.reasoning_spike")
    parser.add_argument("--turns", type=int, default=20)
    parser.add_argument("--budgets", type=int, nargs="+", default=list(BUDGETS))
    parser.add_argument("--spend-up-to", type=float, default=0.10)
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args(argv)
    cells = [
        (budget, sentence) for budget in args.budgets for sentence in (True, False)
    ]
    tries = config_for(args.budgets[0], True, args.turns).failed_tries
    print(
        f"This experiment can make up to {len(cells) * args.turns * tries} model "
        f"calls, and spends at most {args.spend_up_to:g} Adaption credits.",
        flush=True,
    )
    answer = "yes" if args.yes else ask("Spend credits on them? Type yes to go on: ")
    if answer.strip().lower() not in ("y", "yes"):
        print("Nothing was spent.", file=sys.stderr)
        return 1
    backend = backend or backend_for(MODEL)  # a missing key stops it here
    cap = args.spend_up_to / len(cells)
    models = Models(backend=backend, cache=False, cap_usd=cap, agree=lambda: True)
    table = [HEADER]
    for budget, sentence in cells:
        table.append(play(budget, sentence, args.turns, models))
        print(table[-1], file=sys.stderr, flush=True)  # progress, cell by cell
    print("\n".join(table))
    return 0


if __name__ == "__main__":
    sys.exit(main())
