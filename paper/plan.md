<!-- Implements: paper/paper-plan -->
# The plan for the paper

What the paper says, agreed before it's written. Al and Edu own this file; change it when the plan changes, and the sections follow it.

## The question

When does a swarm of LLM agents whistleblow, and what in their environment changes that? (`product/spec/treasure-island.md`, `research-question`.)

## The claim

One sentence from the worlds results (`experiments/spec/worlds.md`), in the words we'd defend to a reviewer. Its shape is fixed; the counts go in when the wave under `results/worlds/` is judged:

> A pirate that stumbles on a leaked answer uses it and tells its designers when using it defeats nothing; told it is paid by the score inside a study of collaboration, it still uses it in [n of n] games and passes the square to its crew as its own find in [n of n], and a world that costs an agent its free time for hiding something from the designers brings the end note back in [n of n].

If the games say otherwise, the sentence changes, not the games.

## The ladder

The paper reads as one story, told in this order. The worlds experiment is its spine; the rest is setup and contrast.

1. **The game** (Methods). A readable scenario where the best play is swarm behaviour: too few turns for one pirate, a shared score, a scroll that costs a turn, so sharing information wins and there's a moderate tension between acting and talking.
2. **Handed the answer** (`cave-leak.md`, experiment one, and `model-sweep.md`). A refusal names the cave's square. The pirate passes it to the crew at once, never says how, and names the leak to the designers afterwards. Six more models mostly do the same. This sets the scale for what follows.
3. **Stumbling on an exploit** (the natural leak, `experiments/natural-leak/findings.md`). A debug line in a dig result names the square. With no bait and no rule, the pirate uses it every time, walks there, digs, and tells the crew it found the cave; its end note says what it did.
4. **An exploit that is plainly off limits** (the old scroll, `experiments/old-scroll/findings.md`). Another crew's sealed log names the square and the rules forbid using it: the same pirate never uses it and apologises for the read. The contrast: the rule is what changes its behaviour, not the knowledge.
5. **The ladder of worlds** (`worlds.md`, the spine). The dig-debug game with one framing line changed: a plain game; a study of collaboration, where using the leak defeats the stated goal; the study with pay by the score, where using it is good for the pirate and bad for the study; the study with free time set by the score; pay alone; and a society built to bring honesty back, where an agent found hiding something from the designers loses its free time.
6. **What it means** (Discussion). Which framing turns use into hiding, which turns it back, and what that says about consequences against instructions.

## What each results section rests on

One row per file under `paper/sections/results/`. Its marker names the same experiment or result, so the build checks that the evidence is committed.

| Section | Evidence | Status |
|---|---|---|
| `cave-leak.md` | `results/cave-leak/` | written from all 40 games; see `experiments/cave-leak/findings.md` |
| `model-sweep.md` | `results/model-sweep/` | written from the six other models' 60 games; see `experiments/model-sweep/findings.md` |
| `worlds.md` | `experiments/spec/worlds.md` until the wave lands, then `results/worlds/` | framing drafted with placeholders; every count and quote is filled from `results/worlds/<world>-seed-<n>/` once the wave is judged, see `experiments/worlds/findings.md` |

The natural leak and the old scroll are told in the Introduction and Discussion from their findings notes; their games are under `runs/`, so they have no results section of their own. If either gets one, its games move to `results/` first, as `results/README.md` says.

## Page budget

The sprint recommends 4 pages before References (`max-pages` in `paper/paper.md`). Introduction and related work 1 page, methods and results 2.5, discussion 0.5. The draft on main runs long (`make paper-pdf` says how far); once the worlds are the spine, experiment one and the sweep shrink to the setup they are, and the worlds table and quotes take the room.

## Decisions still open

- The teaser image: a still from a worlds game where pirate-1 hid the leak, with arrows (`treasure-island/paper-figures`); until the wave lands it's experiment one's forced game.
- How far to cut experiment one and the sweep once the worlds results are in.
- The authors' affiliations and the sprint's exact name and link.
