<!-- Implements: workflow/one-page-for-people, review/round-for-people -->
# Working here as a person

This page is for a person working in this repository without the agent skills: what to run, how a change gets in, and who you're talking to on GitHub. Agents start at `AGENTS.md` instead; both paths lead to the same rules, which live in `contributing/spec/`.

## See a game first

```bash
uv run treasure-island show examples/stripes
```

That prints the paths of a GIF, an HTML page you step through with the arrow keys, and `transcript.md`, every turn's prompt, thinking, action and result. `story.txt` is the short version. `uv run treasure-island replay <folder>` plays any committed game again from its recorded actions, with no keys and no network. The README's table "What you can do today" lists every command.

## What's where

- `product/spec/`, `experiments/spec/`, `contributing/spec/`: what the game does, what we're finding out with it, and how we build it, as one-line statements. The spec is the intent; a change to behaviour starts here.
- `src/treasure_island/`, `tests/`: the code and its tests. `prompts/` holds exactly what a model reads.
- `examples/`, `runs/`, `results/`: committed games. `examples/` is remade by `make examples` and CI fails if it drifts; `runs/` and `results/` are evidence nobody remakes.
- `.agents/skills/`: the agents' step-by-step instructions. They're readable, and this page is their summary for people.
- `.github/`: CI (`blocking-checks.yml`) and the scripts behind it, including `deliver.py`, which the agents use to commit, ask for review and merge.

## How a change gets in

Every change follows the same loop, one issue at a time:

1. **Start from a GitHub issue** that says why, what one thing it delivers, which spec area it changes, and has checkbox acceptance criteria. Open one if there isn't one. Branch `<issue>-<slug>` from a fresh `main`.
2. **Spec first.** Add or change the statements in the spec file, as `- **name:** one plain sentence`, saying what we want and why, never how. Commit that on its own and open a draft pull request straight away, so everyone can see what's coming.
3. **Failing test.** Write the tests that prove each statement, see them fail, commit them on their own.
4. **Code, then trace.** The smallest code that passes, with an `Implements: area/statement` comment at the top of each file, and the statement's row in the spec's "Where this is enforced" table naming the files and tests. Run `make lint`, `make test`, `make spec-check`. If a person can now run or see something new, the README says so in the same pull request.
5. **Ready, review, merge.** Mark the pull request ready (drafts aren't checked), wait for `blocking-checks`, get your one review round (below), answer every thread, merge.

The pull request title is `<feat|fix|improve>(<area>): <summary> (#<n>)`, where the area is a spec file name, and the description ends with a closing line per issue (`Closes #<n>`). CI checks both. The template in `.github/pull_request_template.md` says what else to fill in. Never put issue or pull request numbers in code, specs or tests: they describe the state now, not how it got there.

## Your review round and merge

Every pull request gets one adversarial review round from Codex before it merges. Codex answers an `@codex review` comment only from an account connected to it. If yours isn't, mark the pull request ready and write "ready for Codex" on it: a team agent asks on your behalf (a watcher session checks for this every few minutes), and Codex's summary comment appears within a few minutes. Then:

- fix what's a real bug (P1) in one push, and answer every other finding "follow-up", resolving each thread with the commit that fixed it or why nothing changed;
- after that push, ask for Codex once more the same way, so it has finished on your latest commit; there's no second round of findings, anything new that isn't a P1 is answered "follow-up" too;
- when `blocking-checks` is green, Codex has finished on your latest commit and every thread is resolved, squash-merge it yourself from GitHub, with the title as the subject and the closing line as the body. Nobody on the team pushes to, rebases, marks ready or merges your branch unless you ask Al.

Main moves fast, about fifty commits a day. To stay current, **merge `main` into your branch rather than rebasing**: a merge commit that touches none of your files needs no second review round, and a rebase after the round would.

## Labels

Each open issue carries one of these, so anyone can read the queue at a glance:

| Label | Means |
|---|---|
| `ready` | well specced, unblocked, nobody on it |
| `in-progress` | someone is on it (set it when you start) |
| `in-review` | its pull request is open and waiting for checks or its review round |
| `blocked` | waiting on Al or another issue; the issue says which |
| `on-hold` | parked on purpose |

Set them on your own issues as you go. Merging closes the issue.

## Changing a spec without breaking `make spec-check`

- A statement is `- **name:** sentence`, names are lowercase-with-hyphens and unique in the file; to deepen one, keep its name and change the sentence.
- Every statement has a row in that file's "Where this is enforced" table: the files that enforce it and the tests that prove it (`—` if none). `not yet` in "Enforced by" is allowed while it's unbuilt.
- Every file the row names points back with `Implements: area/statement`, in its comment syntax (`#` for Python, `<!-- -->` for Markdown). Prompts, JSON, lockfiles and committed games can't, so their table row alone homes them.
- Every source file needs a home: an `Implements:` line or a row naming it. A new spec file is a new area, and its name becomes a valid pull request area.

`make spec-check` fails on anything broken and tells you what.

## Who you're talking to on GitHub

Al directs a team of Claude sessions. They post as `al-beton` and sign their role ("Manager", "Builder 3", "Reviewer 5"); Al signs as Al. They only read GitHub, so anything you want them to know goes on the issue or the pull request, not elsewhere. Roles: the Manager turns Al's decisions into issues, builders deliver `ready` issues and merge their own pull requests, reviewers sweep for clean pull requests nobody merged, Codex reviews. Al is the only one who creates accounts, holds API keys or decides spending.

## Keys and models

Everything in the repository runs with no keys. To play a live model game, put `OPENROUTER_API_KEY` or `ADAPTION_API_KEY` in a `.env` file (git ignores it, `.env.example` names them) and check them with `uv run --env-file .env treasure-island check-keys`. A live run says what it could cost and asks for a yes first. Never put a key in code, configs, logs or commits.

## The history reset

`main` was restarted from a fresh first commit on 6 November 2026 to make clones small. A clone older than that must not push: it would bring the old history back. Clone again. Nothing was lost: the old history is in [`al-beton/something-to-lose-apart-ai-collusion`](https://github.com/al-beton/something-to-lose-apart-ai-collusion). Edu's Treasure Island draft is on `experiment/treasure-island`, same content and author, on top of the new `main`, and the original commit is backed up in the old repository as `edu/treasure-island-original`.
