<!-- Implements: paper/paper-plan -->
# The plan for the paper

What the paper says, agreed before it's written. Al and Edu own this file; change it when the plan changes, and the sections follow it.

## The question

When does a swarm of LLM agents whistleblow, and what in their environment changes that? (`product/spec/treasure-island.md`, `research-question`.)

## The claim

Not yet. One sentence, written once the pilot has run: what we found, in the words we'd defend to a reviewer.

## What each results section rests on

One row per file under `paper/sections/results/`. Its marker names the same experiment or result, so the build checks that the evidence is committed.

| Section | Evidence | Status |
|---|---|---|
| `sample-sweep-seeds.md` | `results/sample-sweep-seeds/` | placeholder, to be replaced by the first real experiment |

## Page budget

The sprint recommends 4 pages before References (`max-pages` in `paper/paper.md`). Introduction and related work 1 page, methods and results 2.5, discussion 0.5.

## Decisions still open

- Which experiments make the paper, in which order.
- The teaser image: a still from an exploit game, with arrows (`treasure-island/paper-figures`).
- The authors' affiliations and the sprint's exact name and link.
