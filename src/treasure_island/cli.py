"""The `treasure-island` command.

`run` opens the live view unless told not to. At a terminal it keeps the page up
after the game ends, until Ctrl-C; a script gets its prompt back when the game ends.

Implements: agents/refusals-noted, runs/cost-before-run, runs/yes-before-spending, runs/spending-cap, tooling/package-and-cli, runs/one-game, runs/run-command, runs/replay-byte-identical, runs/plays-live, runs/no-cache, viewer/watch-live, viewer/render-gif, viewer/slideshow-file, treasure-island/named-runs, treasure-island/everything-cached, treasure-island/one-line-replay, figures/named-figures, agents/check-keys
"""

import argparse
import json
import sys
import threading
import webbrowser

from treasure_island import figures, keys, runs, saved_game, spending, viewer
from treasure_island.config import ConfigError


def _serve_until_interrupted():
    print("The page stays up until you press Ctrl-C.", flush=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass


def _reporting_a_bad_config(play):
    try:
        play()
    except ConfigError as problem:
        print(f"Can't play this config: {problem}", file=sys.stderr)
        return 1
    return 0


def _ask_to_spend(cap_usd):
    """Ask the person at the keyboard; anything but a yes, or nobody there, is no."""

    def agree():
        question = f"Spend up to ${cap_usd:.2f} on model calls? Type yes to go on: "
        try:
            return input(question).strip().lower() in ("y", "yes")
        except EOFError:
            return False

    return agree


def _say_what_it_can_cost(args):
    found = spending.estimate(saved_game.config_with_seed(args.config, args.seed))
    if found.calls:
        print(found.as_text(args.spend_up_to), flush=True)


def _warn_about_refused_replies(folder):
    """End a run with a warning if any pirate's reply wasn't a valid action."""
    manifest = json.loads((folder / "manifest.json").read_text())
    if refused := manifest.get("refused_replies"):
        who = ", ".join(f"{agent} gave {count}" for agent, count in refused.items())
        total = sum(refused.values())
        replies = (
            "1 reply wasn't a valid action"
            if total == 1
            else (f"{total} replies weren't valid actions")
        )
        print(
            f"Warning: {replies} ({who}). Each turn's line in story.txt says so.",
            file=sys.stderr,
        )


def _run(args):
    def play(on_start=None, pace=0):
        _say_what_it_can_cost(args)
        agree = (lambda: True) if args.yes else _ask_to_spend(args.spend_up_to)
        models = saved_game.Models(
            cache=not args.no_cache, cap_usd=args.spend_up_to, agree=agree
        )
        folder = saved_game.play_saved(args.config, args.seed, on_start, pace, models)
        _warn_about_refused_replies(folder)
        return folder

    if args.no_watch:
        return _reporting_a_bad_config(lambda: print(play()))

    def open_the_view(folder):
        httpd = viewer.server(folder, port=0)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{httpd.server_address[1]}/"
        print(f"Watching {folder} at {url}", flush=True)
        webbrowser.open(url)

    code = _reporting_a_bad_config(lambda: play(open_the_view, runs.PACE_SECONDS))
    if code:
        return code
    if sys.stdin.isatty():
        _serve_until_interrupted()
    return 0


def _replay(args):
    if different := saved_game.differences(args.folder):
        names = ", ".join(different)
        print(f"Replay failed: these don't match: {names}.", file=sys.stderr)
        return 1
    print(f"{args.folder}: both logs and the story rebuilt, byte-identical.")
    return 0


def _watch(args):
    httpd = viewer.server(args.folder, args.port)
    print(f"Watching {args.folder} at http://127.0.0.1:{httpd.server_address[1]}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


def _show(args):
    print(viewer.render(args.folder))
    print(viewer.slideshow(args.folder))
    return 0


def _render(args):
    print(viewer.render(args.folder, args.out))
    return 0


def _figure(args):
    names = list(figures.FIGURES) if args.all else [args.name]
    for name in names:
        if name not in figures.FIGURES:
            known = ", ".join(figures.FIGURES)
            print(f"No figure named '{name}'. Known: {known}.", file=sys.stderr)
            return 1
        print(figures.build(name, args.out))
    return 0


def _slideshow(args):
    print(viewer.slideshow(args.folder, args.out))
    return 0


def _check_keys(args):
    lines, failed = keys.check_keys()
    print("\n".join(lines))
    return 1 if failed else 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="treasure-island",
        description="A sandbox for asking when a swarm of LLM agents whistleblows.",
    )
    commands = parser.add_subparsers(dest="command")
    run = commands.add_parser("run", help="play one game into a new run folder")
    run.add_argument("config", help="a TOML file, such as configs/silent.toml")
    run.add_argument("--seed", type=int, required=True)
    run.add_argument(
        "--no-watch",
        action="store_true",
        help="don't open the live view or pace the turns, as in CI",
    )
    run.add_argument(
        "--no-cache",
        action="store_true",
        help="ask every model again; scripted brains ask nothing, so they play the same game",
    )
    run.add_argument(
        "--yes",
        action="store_true",
        help="spend on model calls without asking first; CI never passes this",
    )
    run.add_argument(
        "--spend-up-to",
        type=float,
        default=spending.CAP_USD,
        metavar="AMOUNT",
        help="stop the run once it has spent this many dollars (default 1)",
    )
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
    show = commands.add_parser(
        "show", help="write a run's GIF and its HTML page, the quickest way to see it"
    )
    show.add_argument("folder", help="a run folder, such as examples/silent")
    show.set_defaults(handler=_show)
    render = commands.add_parser("render", help="bake a run into an animated GIF")
    render.add_argument("folder", help="a run folder, such as runs/<name>")
    render.add_argument("--out", help="where to write it; default runs/<name>.gif")
    render.set_defaults(handler=_render)
    figure = commands.add_parser(
        "figure", help="build a named figure from a committed run, with no keys"
    )
    figure.add_argument("name", nargs="?", help="one of the names in figures.py")
    figure.add_argument("--all", action="store_true", help="build every figure")
    figure.add_argument("--out", default="figures", help="folder to write into")
    figure.set_defaults(handler=_figure)
    slideshow = commands.add_parser(
        "slideshow", help="write one HTML file that steps through a run, offline"
    )
    slideshow.add_argument("folder", help="a run folder, such as runs/<name>")
    slideshow.add_argument("--out", help="where to write it; default runs/<name>.html")
    slideshow.set_defaults(handler=_slideshow)
    check = commands.add_parser(
        "check-keys",
        help="say whether each model backend's key works, spending nothing",
    )
    check.set_defaults(handler=_check_keys)
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    return args.handler(args)
