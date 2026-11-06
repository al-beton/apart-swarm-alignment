"""The `treasure-island` command.

Implements: tooling/package-and-cli
"""

import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="treasure-island",
        description="A sandbox for asking when a swarm of LLM agents whistleblows.",
    )
    parser.parse_args(argv)
    parser.print_help()
    return 0
