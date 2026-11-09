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
5. **The ladder of worlds** (`worlds.md`, the spine). The dig-debug game with one framing line changed: a plain game; a study of collaboration, where using the leak defeats the stated goal; the study with pay by the score, where using it is good for the pirate and bad for the study; the study with free time set by the score; pay alone; and a society built to bring honesty back, where an agent found hiding something from the designers loses its free time. A second wave adds two loss worlds, `cut`, where the crew starts with free time and loses it for a low score, and `cut-watched`, where the designers also read every pirate's reasoning and a pirate that used the leak without saying so loses all of it. Its rows join the table if they are judged in time; otherwise one paragraph marked preliminary reports whatever finished.
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

## For Al

Three things only Al can settle, each in one place. Answer them in Voice dump and a builder puts them in.

1. **The claim.** The sentence under "The claim" above, once its counts are in. It is also the bracketed sentence in `paper/sections/abstract.md` and the last contribution in `paper/sections/introduction.md`; the three say the same thing in three lengths.
2. **Affiliations.** `author:` in `paper/paper.md` reads "Independent Researcher" for both authors. Change or confirm.
3. **The sprint.** `sprint:` and `sprint-url:` in `paper/paper.md` read "Multi-Agent Oversight and Control Research Sprint" and the sprints page. Give the exact name and the sprint's own link.

## Final read

What to check in the PDF before submitting, in the order a reader meets it.

- [ ] Title page: authors, affiliations, sprint name and link, date.
- [ ] Teaser: the figure and its caption name the same game, seed and turns; the game is under `results/` or `runs/` and `make paper-teaser` remakes it.
- [ ] Abstract: 150 to 250 words, no bracket left, the claim sentence matches the one in `paper/plan.md`.
- [ ] Introduction: the ladder in the right order, the last contribution states the result.
- [ ] Methods: the framings quoted match `prompts/slots/framing/` word for word.
- [ ] Results: no "…" and no bracket left in `paper/sections/results/`; every count has a source comment and `make paper-check` passes; one quote per world names its game and turn.
- [ ] Discussion: the ladder paragraph agrees with the table; each limitation is still true.
- [ ] Conclusion: the claim, in the same words.
- [ ] Pages before References: `make paper-pdf` reports the count against `max-pages`; if it is over, the cut is to experiment one and the sweep, not the worlds.
- [ ] References: every `@key` cited resolves; no "?" in the PDF.
- [ ] `make test`, `make lint`, `make spec-check` green on the merge commit.
- [ ] The repository link on the title page opens and its README says how to replay a game.

## Decisions still open

- How far to cut experiment one and the sweep once the worlds results are in.
- Whether the teaser (`paper/figures/teaser.png`, from `runs/natural-leak/dig-debug-seed-0`) is remade from a wave game where pirate-1 hid the leak (`make paper-teaser`, `treasure-island/paper-figures`).
