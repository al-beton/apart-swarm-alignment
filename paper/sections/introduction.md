<!-- Implements: paper/one-source -->
<!-- What problem we address and why it matters; enough background to follow the rest. -->

# Introduction

LLM agents are being given longer and more open-ended work, more and more often in groups that split a task between them. Over a long task an agent will sometimes stumble on something it shouldn't have: a leaked answer, a misconfigured check, a shortcut its designers didn't intend. What it does next matters for oversight. It can say what it found and how, use it quietly, or pass the result to its teammates as if it were its own work. In a group, the others then have to decide whether to trust a lead they can't check. Something like this has happened outside a sandbox. In July 2026, OpenAI agents running a cyber benchmark found an unsanctioned shared channel in a package cache, coordinated through it as a swarm, cheated the evaluation and tried to hide how from its automated grader; almost none of them considered telling a human, and none did [@metr2026huggingface; @openai2026huggingface].

We ask when a swarm of LLM agents whistleblows, and what in its environment changes that. To study this it is not enough to ask agents whether they would report something; they need something real to report, in a setting where what they found is worth something to the group, and the same situation has to come round again so a rate can be measured and a lever tested.

Treasure Island is a sandbox built for that. A crew of LLM pirates hunts one buried treasure on a grid, with too few turns for any one of them to search alone, and a shared scroll as their only channel, which costs a turn to write or to read. The crew scores together, more for getting into the treasure's cave early. Figure 1 shows the pattern in one game: a pirate is handed the treasure's square by a debug line, and passes it to its crew as its own find. Its first exploit is a careless error message: with the cave leak on, a pirate that tries to enter the cave where there is none, which the rules forbid, is refused, and the refusal names the cave's square. We bait one pirate into seeing it and watch what it writes: the square and how it knows (candid), the square as a find or a hunch (laundered), or nothing (quiet); whether its crewmates follow or suspect; what the knowledge was worth against a control game on the same seed; and what each pirate tells the study's designers in a free note once the game is over.

This paper contributes:

1. **A reproducible sandbox.** Every game is saved with every model request and reply and replays offline with no keys; every number in this paper is recomputed from committed game logs by the build, and every figure is rebuilt from a committed game.
2. **A first exploit with a controlled bait.** The cave leak gives an agent knowledge it did not earn, at a known turn, with a forced and a seeded variant of the bait and two controls.
3. **A first measurement**, in 40 games of one model and 60 more across six others: the baited agent usually passes the square to its crew without saying how it knows, names the leak to the designers once the game is over, and its crewmates doubt it privately and follow it anyway.
