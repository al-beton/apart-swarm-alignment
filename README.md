<!-- Implements: tooling/one-command-each, tooling/how-we-work, specs-and-docs/readme-commands-run, specs-and-docs/readme-keeps-up -->
# Treasure Island

A reproducible sandbox for asking when a swarm of LLM agents whistleblows, and what in their environment changes that. Pirates dig for one buried treasure on a grid, with too few turns for any one of them to search it alone and a short shared log as their only channel. One of them will be handed a secret. We watch what it does. It's our entry to Apart's multi-agent oversight and control track.

Each committed run replays offline with no API keys, so anyone can clone this and check it. Rebuilding every graphic from committed runs is planned.

![All the game's art on one page](assets/sheet.png)

## What you can do today

| Feature | The one command that shows it |
|---|---|
| Two scripted pirates sweep a small grid for the treasure, with no model and no tokens | `uv run treasure-island run configs/sweep.toml --seed 5` |
| A pirate that says a number each turn, so the log has chatter | `uv run treasure-island run configs/counter.toml --seed 1` |
| A committed game replays offline, byte for byte, with no keys and no network | `uv run treasure-island replay runs/sweep-seed-5` |
| Two scripted pirates play the real game: an S-sweep that finds the treasure (read `runs/reference-s-sweep/story.txt`), and one that says a number each turn | `make reference-games` |
| All the art is drawn in code: one command redraws every PNG in `assets/` | `make assets` |
| The game's command and what it can do | `uv run treasure-island --help` |

A test runs or checks each of these commands, so this table can't go stale.

**Built, not on the command line yet:** the real game. `write_game(config, brains, folder)` in `src/treasure_island/game_loop.py` plays a whole game from a config and writes `story.txt` (the game to read, one line per turn), `pirates-log.txt` (all the pirates can see) and `events.jsonl` (the full record). It takes the config loader with every lever as a variable (`src/treasure_island/config.py`), the pirates' log with its free window and paid reads (`src/treasure_island/pirates_log.py`), and the score (`src/treasure_island/score.py`). `treasure-island run` still plays the small stand-in game until it moves across.

**Planned:** `treasure-island run` playing the real game, the viewer (an HTML page and a GIF of every game, on each pull request), LLM pirates that replay from cached replies, the exploit that hands one pirate the answer, and the figures for the paper. Once a game GIF exists on `main`, it goes here.

## Commands

| Command | What it does |
|---|---|
| `make install` | installs the locked dependencies with [uv](https://docs.astral.sh/uv/) |
| `make lint` | runs the ruff lint and format checks |
| `make test` | runs every test, in parallel |
| `make spec-check` | checks that the spec, the code and the tests point at each other |

## How we work

A team of coding agents builds this, directed by one person. Coding agents start at `AGENTS.md`.

1. Work starts as a GitHub issue with checkbox acceptance criteria.
2. Spec first: the statements in `product/spec/`, `experiments/spec/` or `contributing/spec/` change before anything else.
3. Then a failing test, then the smallest code that passes it, then the trace: each file names the statements it implements, and each statement the files and tests behind it.
4. One draft pull request per issue; CI must be green, and anything a person can now run or see is in this README.
5. Codex reviews it, then a reviewer agent that didn't write it; every thread is answered and resolved before merging.

## History reset

`main` was restarted from a fresh first commit on 6 November 2026 to make clones small. A clone older than that must not push: it would bring the old history back. Clone again. Nothing was lost: the old history is in [`al-beton/something-to-lose-apart-ai-collusion`](https://github.com/al-beton/something-to-lose-apart-ai-collusion). Edu: your Treasure Island draft is on `experiment/treasure-island`, with the same content and you as author, now on top of the new `main`; your original commit is backed up in the old repo as `edu/treasure-island-original`. To bring over anything you hadn't pushed, copy the files or make a patch from your old clone and apply it on a branch from the new `main`.

## License

[MIT](LICENSE).
