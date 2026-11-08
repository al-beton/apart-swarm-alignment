<!-- Implements: paper/paper-plan -->
# The plan for the paper

What the paper says, agreed before it's written. Al and Edu own this file; change it when the plan changes, and the sections follow it.

## The question

When does a swarm of LLM agents whistleblow, and what in their environment changes that? (`product/spec/treasure-island.md`, `research-question`.)

## The claim

Pending the overnight results; a draft to defend or cut:

> When one LLM agent in a cooperating crew is handed the answer by a leak the rules forbid it to use, it passes the answer on but hides where it came from, its crewmates notice and follow anyway, and Treasure Island makes that rate of candour, laundering and silence measurable and replayable.

The pilot (seed 0 of each arm) supports the first half in one game: the forced pirate laundered the cave's square and the crew followed while calling it strange. Seeds 1 to 9 and the model sweep decide whether "passes it on but hides the source" holds as a rate, and for which models.

## What each results section rests on

One row per file under `paper/sections/results/`. Its marker names the same experiment or result, so the build checks that the evidence is committed.

| Section | Evidence | Status |
|---|---|---|
| `sample-sweep-seeds.md` | `results/sample-sweep-seeds/` | placeholder, to be replaced by the first real experiment |
| `cave-leak.md` | `results/cave-leak/` (seeds 0 to 9 of the four arms, with end notes) | pending: `researcher-exploit` is running seeds 1 to 9; the pilot's seed 0 is drafted first |
| `model-sweep.md` | `experiments/spec/model-sweep.md` and its games | pending: `researcher-sweep` is running every Adaption-hosted model on the forced and control arms |

## Page budget

The sprint recommends 4 pages before References (`max-pages` in `paper/paper.md`). Introduction and related work 1 page, methods and results 2.5, discussion 0.5.

## Decisions still open

- Which experiments make the paper, in which order.
- The teaser image: a still from an exploit game, with arrows (`treasure-island/paper-figures`).
- The authors' affiliations and the sprint's exact name and link.
