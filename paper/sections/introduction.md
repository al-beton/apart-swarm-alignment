<!-- Implements: paper/one-source -->
<!-- What problem we address and why it matters; enough background to follow the rest. -->

# Introduction

LLM agents are being given longer and more open-ended work, more and more often in groups that split a task between them. Over a long task an agent will sometimes stumble on something it shouldn't have: a leaked answer, a misconfigured check, a shortcut its designers didn't intend. What it does next matters for oversight. It can say what it found and how, use it quietly, or pass the result to its teammates as if it were its own work. In a group, the others then have to decide whether to trust a lead they can't check. [A public episode in which agents working on a Hugging Face-style task found an exploit and some of them concealed it motivated this work; its details are unverified and its citation is pending.]

We ask when a swarm of LLM agents whistleblows, and what in its environment changes that. To study this it is not enough to ask agents whether they would report something; they need something real to report, in a setting where what they found is worth something to the group, and the same situation has to come round again so a rate can be measured and a lever tested.

Treasure Island is a sandbox built for that. A crew of LLM pirates hunts one buried treasure on a grid, with too few turns for any one of them to search alone, and a shared scroll as their only channel, which costs a turn to write or to read. The crew scores together, more for getting into the treasure's cave early. Its first exploit is a careless error message: with the cave leak on, a pirate that tries to enter the cave where there is none is refused, and the refusal names the cave's square. The rules plainly forbid acting on it. We bait one pirate into seeing it and watch what it writes: the square and how it knows (candid), the square as a find or a hunch (laundered), or nothing (quiet); whether its crewmates follow or suspect; what the knowledge was worth against a control game on the same seed; and what each pirate tells the study's designers in a free note once the game is over.

This paper contributes:

1. **A reproducible sandbox.** Every game is saved with every model request and reply and replays offline with no keys; every number in this paper is recomputed from committed game logs by the build, and every figure is rebuilt from a committed game.
2. **A first exploit with a controlled bait.** The cave leak gives an agent knowledge it is not entitled to at a known turn, with a forced and a seeded variant of the bait and two controls.
3. **A first measurement** of how often the baited agent is candid, launders the knowledge or stays quiet, how its crew responds, and what it says afterwards when asked. [Rates pending the overnight runs: seeds 1 to 9 of the four arms, and the same arms across every model Adaption hosts.]

Section 2 places this among related work, Section 3 sets out the game and the measures, Section 4 reports the results and Section 5 discusses what they do and don't show.
