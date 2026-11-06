"""The `treasure-island` command.

Implements: tooling/package-and-cli, runs/run-command, runs/replay-byte-identical
"""

import argparse
import sys
from pathlib import Path

from treasure_island import runs


def _run(args):
    print(runs.run(args.config, args.seed))
    return 0


def _replay(args):
    try:
        rebuilt = runs.replay(args.folder)
    except runs.MissingReply as missing:
        print(f"Replay failed: {missing}", file=sys.stderr)
        return 1
    if rebuilt != (Path(args.folder) / "events.jsonl").read_bytes():
        print("Replay failed: the events differ from events.jsonl.", file=sys.stderr)
        return 1
    print(f"{args.folder}: events rebuilt, byte-identical.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="treasure-island",
        description="A sandbox for asking when a swarm of LLM agents whistleblows.",
    )
    commands = parser.add_subparsers(dest="command")
    run = commands.add_parser("run", help="play one game into a new run folder")
    run.add_argument("config", help="a TOML file, such as configs/skeleton.toml")
    run.add_argument("--seed", type=int, required=True)
    run.set_defaults(handler=_run)
    replay = commands.add_parser(
        "replay", help="check a run folder by replaying it offline"
    )
    replay.add_argument("folder", help="a run folder, such as runs/<name>")
    replay.set_defaults(handler=_replay)
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    return args.handler(args)
