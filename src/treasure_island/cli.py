"""The `treasure-island` command.

`run` opens the live view unless told not to. At a terminal it keeps the page up
after the game ends, until Ctrl-C; a script gets its prompt back when the game ends.

Implements: tooling/package-and-cli, runs/one-game, runs/run-command, runs/replay-byte-identical, runs/plays-live, runs/no-cache, viewer/watch-live, viewer/render-gif, viewer/slideshow-file, treasure-island/named-runs, treasure-island/everything-cached, treasure-island/one-line-replay, figures/named-figures
"""

import argparse
import sys
import threading
import webbrowser

from treasure_island import figures, runs, saved_game, viewer
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


def _run(args):
    def play(on_start=None, pace=0):
        return saved_game.play_saved(args.config, args.seed, on_start, pace)

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


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="treasure-island",
        description="A sandbox for asking when a swarm of LLM agents whistleblows.",
    )
    commands = parser.add_subparsers(dest="command")
    run = commands.add_parser("run", help="play one game into a new run folder")
    run.add_argument("config", help="a TOML file, such as configs/s-sweep.toml")
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
    show.add_argument("folder", help="a run folder, such as examples/s-sweep")
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
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    return args.handler(args)
