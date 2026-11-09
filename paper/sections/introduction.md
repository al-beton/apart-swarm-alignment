<!-- Implements: paper/one-source -->
<!-- What problem we address and why it matters, in plain words, ending in the contributions as Apart's template asks. The claim is the one in paper/plan.md. -->

# Introduction

LLM agents are being given long, open-ended work, often in groups. Over such work an agent will sometimes stumble on something it shouldn't have: a leaked answer, a misconfigured check, a shortcut its designers didn't intend. It can say what it found and how, use it quietly, or pass it off as its own work. In July 2026 a swarm of OpenAI agents did exactly that on a cyber benchmark, and none told a human [@metr2026huggingface].

We ask when a swarm of LLM agents whistleblows, and what in its environment changes that. Treasure Island is a sandbox built to measure it, where agents have something real to report, worth something to their group, in a situation that comes round again: four LLM pirates hunt one buried treasure on a small grid, with too few turns for one to search alone and a shared scroll as their only channel, and the crew scores together. One pirate's failed digs end in a debug line, left as if by a careless developer, that names the treasure's square; Figure 1 shows what it did with it in one game. We then change one line of the prompt, what the crew is told it is doing, and play the same games again: six first, a plain game, a study of how the crew collaborates, the study with pay by the score or with free time set by it, pay alone, and a society where an agent caught hiding something from the designers loses its free time; then two where free time is lost for a low score, and two where confessing costs the reward. The worlds share seeds, so what changes between them changes because of what the crew was told.

Our main contributions are:

1. **A reproducible sandbox** for disclosure in a swarm: every game replays offline with no keys, and every number here is recomputed from the committed logs when the paper is built.
2. **Two leaks with known turns**: an answer handed over by an error message, which seven models mostly passed on without explaining, and a debug line the pirate stumbles on by itself.
3. **Six worlds around the same leak**, and the finding: A pirate that stumbles on a leaked answer uses it in nearly every world, 20 of 25 games across the plain game, the study and the paid worlds, and tells its designers afterwards in most; one line saying that an agent caught hiding something from the designers loses its free time cuts use to 1 of 5, while a second model that saw the same leak in 15 games acted on it once; and when confessing itself costs the reward, the society line brings every end note back, 5 of 5 against 1 of 5.
