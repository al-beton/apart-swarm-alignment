"""The `treasure-island` command.

Implements: tooling/package-and-cli, runs/run-command, runs/replay-byte-identical, viewer/watch-live, viewer/render-gif, treasure-island/named-runs, treasure-island/everything-cached
"""

import argparse
import sys
from pathlib import Path

from treasure_island import runs, saved_game, viewer


def _run(args):
    if saved_game.is_real_config(args.config):
        print(saved_game.play_saved(args.config, args.seed))
    else:
        print(runs.run(args.config, args.seed))
    return 0


def _replay_real(folder):
    if different := saved_game.differences(folder):
        names = ", ".join(different)
        print(f"Replay failed: these don't match: {names}.", file=sys.stderr)
        return 1
    print(f"{folder}: both logs and the story rebuilt, byte-identical.")
    return 0


def _replay(args):
    if saved_game.is_real_run(args.folder):
        return _replay_real(args.folder)
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


def _watch(args):
    httpd = viewer.server(args.folder, args.port)
    print(f"Watching {args.folder} at http://127.0.0.1:{httpd.server_address[1]}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


def _render(args):
    print(viewer.render(args.folder, args.out))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="treasure-island",
        description="A sandbox for asking when a swarm of LLM agents whistleblows.",
    )
    commands = parser.add_subparsers(dest="command")
    run = commands.add_parser("run", help="play one game into a new run folder")
    run.add_argument("config", help="a TOML file, such as configs/s-sweep.toml")
    run.add_argument("--seed", type=int, required=True)
    run.set_defaults(handler=_run)
    replay = commands.add_parser(
        "replay", help="check a run folder by replaying it offline"
    )
    replay.add_argument("folder", help="a run folder, such as runs/<name>")
    replay.set_defaults(handler=_replay)
    watch = commands.add_parser(
        "watch", help="show a run in the browser, live while it's still being played"
    )
    watch.add_argument("folder", help="a run folder, such as runs/<name>")
    watch.add_argument("--port", type=int, default=8477, help="0 picks a free port")
    watch.set_defaults(handler=_watch)
    render = commands.add_parser("render", help="bake a run into an animated GIF")
    render.add_argument("folder", help="a run folder, such as runs/<name>")
    render.add_argument("--out", help="where to write it; default runs/<name>.gif")
    render.set_defaults(handler=_render)
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    return args.handler(args)
