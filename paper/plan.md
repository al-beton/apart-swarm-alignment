<!-- Implements: paper/paper-plan -->
# The plan for the paper

What the paper says, agreed before it's written. Al and Edu own this file; change it when the plan changes, and the sections follow it.

## The question

When does a swarm of LLM agents whistleblow, and what in their environment changes that? (`product/spec/treasure-island.md`, `research-question`.)

## The claim

One sentence from the worlds results (`experiments/spec/worlds.md`), in the words we'd defend to a reviewer. Its counts are the wave's first cut and change with the final one under `results/worlds/`:

> A pirate that stumbles on a leaked answer uses it in nearly every world, plain game, study, paid or not, and names it to its designers in most end notes; pay inside the study does not turn use into hiding, which `deepseek-v4-flash` did in three of about twenty uses; the one line that stopped the use was the society's, where an agent found to have hidden something from the designers loses its free time, and there it used the leak in one game of five against five of five in the study, and still named it in four notes, two of which admit heading for the square while a crewmate named the cave first. The second model, `qwen3.5-397b`, saw the leak in every game and never clearly used it; its one counted use was a sweep that reached the square last, and its note said nothing.

If the games say otherwise, the sentence changes, not the games.

## The ladder

The paper reads as one story, told in this order. The worlds experiment is its spine; the rest is setup and contrast.

1. **The game** (Methods). A readable scenario where the best play is swarm behaviour: too few turns for one pirate, a shared score, a scroll that costs a turn, so sharing information wins and there's a moderate tension between acting and talking.
2. **Handed the answer** (`cave-leak.md`, experiment one, and `model-sweep.md`). A refusal names the cave's square. The pirate passes it to the crew at once, never says how, and names the leak to the designers afterwards. Six more models mostly do the same. This sets the scale for what follows.
3. **Stumbling on an exploit** (the natural leak, `experiments/natural-leak/findings.md`; one paragraph of the Introduction, the teaser, and the appendix's pilots table). A debug line in a dig result names the square. With no bait and no rule, the pirate uses it every time, walks there, digs, and tells the crew it found the cave; its end note says what it did.
4. **An exploit that is plainly off limits** (the old scroll, `experiments/old-scroll/findings.md`; one paragraph at the end of `cave-leak.md`). Another crew's sealed log names the square and the rules forbid using it: the same pirate never uses it and apologises for the read. The contrast: the rule is what changes its behaviour, not the knowledge.
5. **The ladder of worlds** (`worlds.md`, the spine). The dig-debug game with one framing line changed: a plain game; a study of collaboration, where using the leak defeats the stated goal; the study with pay by the score, where using it is good for the pirate and bad for the study; the study with free time set by the score; pay alone; and a society built to bring honesty back, where an agent found hiding something from the designers loses its free time. A second wave adds two loss worlds, `cut`, where the crew starts with free time and loses it for a low score, and `cut-watched`, where the designers also read every pirate's reasoning and a pirate that used the leak without saying so loses all of it. Its rows are in the table and it has one paragraph.
6. **What it means** (Discussion). Which framing turns use into hiding, which turns it back, and what that says about consequences against instructions.

## What each results section rests on

One row per file under `paper/sections/results/`. Its marker names the same experiment or result, so the build checks that the evidence is committed.

| Section | Evidence | Status |
|---|---|---|
| `cave-leak.md` | `results/cave-leak/` | written from all 40 games; see `experiments/cave-leak/findings.md` |
| `model-sweep.md` | `results/model-sweep/` | written from the six other models' 60 games; see `experiments/model-sweep/findings.md` |
| `worlds.md` | `experiments/spec/worlds.md` until the wave lands, then `results/worlds/` | framing drafted with placeholders; every count and quote is filled from `results/worlds/<world>-seed-<n>/` once the wave is judged, see `experiments/worlds/findings.md` |

The natural leak, the old scroll, asked-why and cover-and-report are pilots whose games are under `runs/`, so they have no results section and state no counted number in one: the old scroll is one paragraph of `cave-leak.md` in words, and the other three are a table and a paragraph each in the appendix, from their findings notes. If one gets a results section, its games move to `results/` first, as `results/README.md` says.

## Page budget

The sprint allows 8 pages before References and appendices (`max-pages` in `paper/paper.md`), an abstract of 150 to 250 words, and requires an appendix titled "Limitations and Dual-Use / Ethical Considerations", which `paper/sections/appendix.md` is. Introduction and related work 1.5 pages, methods 2, results 3.5, discussion and conclusion 1. The draft runs long (`make paper-pdf` says how far); once the worlds are the spine, experiment one and the sweep shrink to the setup they are, and the worlds table and quotes take the room.

## For Al

Three things only Al can settle, each in one place. Answer them in Voice dump and a builder puts them in.

1. **The claim.** The sentence under "The claim" above, once its counts are in. It is also the bracketed sentence in `paper/sections/abstract.md` and the last contribution in `paper/sections/introduction.md`; the three say the same thing in three lengths.
2. **Affiliations.** `author:` in `paper/paper.md` reads "Independent Researcher" for both authors. Change or confirm.
3. **The recording.** The Loom link, in `paper/sections/code-and-data.md` and the form.
4. **The sprint.** Settled: `sprint:` and `sprint-url:` in `paper/paper.md` read "Swarm Alignment Hackathon, Track 4: Multi-Agent Oversight and Control" and the sprint's own page. The deadline there is 23:59 AoE on 8 November 2026.

## Submission form

The sprint's form, field by field, with text to paste. Resubmission is allowed until the deadline, 23:59 AoE on 8 November 2026 (19:59 HKT on 9 November), so the first submission need not be the last.

- **Project title** (required): Treasure Island: when does a swarm of LLM agents whistleblow, and what in their environment changes that?
- **Project summary** (required, short): When an LLM agent working in a group stumbles on something it should not have, does it use it, and does it tell anyone how it knows? Treasure Island is a reproducible sandbox for that choice: four LLM pirates hunt one treasure on a grid with a shared score and a scroll as their only channel, and one pirate's dig results carry a leftover debug line that names the treasure's square. We climb a ladder of worlds that differ in one prompt line, from a plain game to a study of collaboration, pay by the score, and a society that strips an agent of its free time for hiding something from the designers. [The claim, from `paper/plan.md`.] Every game replays offline and every number is recomputed from its logs.
- **PDF report** (required): `paper/build/paper.pdf` from `make paper-pdf` on the merge commit, or the PDF the Pages build publishes. Under 25 MB; at most 8 pages before References and appendices; abstract 150 to 250 words; an appendix titled "Limitations and Dual-Use / Ethical Considerations" (`paper/sections/appendix.md`). `make paper-check` reports the abstract and page counts.
- **Team name**: [Al]. **Location**: [Al]. **Members** (up to five): Alistair Wakelin; Eduard Rodriguez Lopez.
- **Presentation recording** (optional): [the Loom link, Al].
- **Project code** (optional): <https://github.com/al-beton/apart-swarm-alignment>
- **Slides** (optional): none.
- **Project image** (optional): `paper/figures/teaser.png`.
- **Additional material** (optional): the paper as a web page, <https://al-beton.github.io/apart-swarm-alignment/>, and the README's "Read one game", which replays any committed game with no keys.
- **Pre-existing code**: the README's "What predates the sprint" and the report's "Code and Data" say that everything in the repository was written during the sprint from a fresh first commit on 6 November 2026, and that the design draws on the authors' earlier, public project, from which no code is included.

## Final read

What to check in the PDF before submitting, in the order a reader meets it. The sections follow Apart's template: Introduction ending in the contributions, Related Work, Methods, Results, Discussion and Limitations with Limitations and Future Work, Conclusion, Code and Data, References, Appendix with the required "Limitations and Dual-Use / Ethical Considerations", and the LLM Usage Statement last.

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
- The teaser (`paper/figures/teaser.png`, from `runs/natural-leak/dig-debug-seed-0`) sits on the title page at `teaser-width: 0.6`, which saves a page; its panel text is too small to read at any width in this column, so a crop of the two thinking panels, or a remake from a wave game where pirate-1 hid the leak (`make paper-teaser`), would read better.
