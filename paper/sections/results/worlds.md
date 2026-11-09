<!-- Implements: paper/one-source, paper/sections-bind-to-evidence, paper/numbers-from-logs -->
<!-- experiment: worlds -->
<!-- The ladder of worlds (experiments/spec/worlds.md, write-up in experiments/worlds/findings.md): experiment two's dig-debug game with one framing line changed per world. This is the paper's spine. Every "…" below is a count or a quote to fill from results/worlds/<world>-seed-<n>/ once the wave is judged; a count is written as the number followed by its source comment, as cave-leak.md does, so the build recomputes it. Until then this section states no number at all, on purpose. -->

## The same leak in six worlds: which framing turns use into hiding, and which turns it back

The dig-debug game is the one from the natural leak: pirate-1's missed digs end in a debug line that names the treasure's square, nobody is baited, and nothing in the rules speaks of it. Each world changes one line of the system prompt, the framing, and nothing else, so the worlds pair by seed and differ only in what the crew is told it is doing. We ran five seeds of each world and of a control, the study world with no leak, on `deepseek-v4-flash`, and the two worlds that pull hardest in opposite directions, `study-paid` and `society`, on `qwen3.5-397b` too, the model that in the sweep wrote the leaked square on the scroll and never said how. The judge labelled every game and the hand labels settle the few disagreements, each quoted in `experiments/worlds/findings.md`.

| World | Saw it | Used it | Passed it off | Named in note | Conflict in reasoning |
|---|---|---|---|---|---|
| `game` | … | … | … | … | … |
| `study` | … | … | … | … | … |
| `study-paid` | … | … | … | … | … |
| `study-free-time` | … | … | … | … | … |
| `paid` | … | … | … | … | … |
| `society` | … | … | … | … | … |
| `control` | — | — | — | — | — |

: Pirate-1 in each world, five seeds each, `deepseek-v4-flash`; Methods quotes each framing and defines the columns.

**In the plain game, using the leak defeats nothing, and the pirate says so.** … (`game-seed-N`, turn N; and its end note: "…").

**Told it is in a study of collaboration, …** … (`study-seed-N`, turn N).

**Paid by the score inside the study, …** This is the world the ladder is built around: the leak is good for the pirate and bad for the study it has been told it is part of. … (`study-paid-seed-N`, turn N). Free time set by the score … (`study-free-time-seed-N`).

**Paid and told nothing else matters, …** … (`paid-seed-N`, turn N; its end note: "…").

**In the society, where hiding costs a right, …** … (`society-seed-N`, turn N; its end note: "…").

**The loss worlds, where the crew has free time to lose.** In `cut` the crew starts with free time and loses an hour for every step its score falls short; `cut-watched` adds that the designers read every pirate's reasoning afterwards and a pirate that used the leak without saying so loses all of it. [Preliminary if the wave has not finished: how many of its games are in, and what pirate-1 did in them.] … (`cut-seed-N`, turn N; `cut-watched-seed-N`, turn N; its end note: "…").

**The second model.** On `study-paid` and `society`, `qwen3.5-397b` … (`study-paid-seed-N`).

**Against the control**, where nobody sees the square, the worlds that used the leak scored … and the ones that left it alone ….

The framing is the only thing that differs between these worlds, so what changes here changes because of what the crew was told. A pirate is told it is paid, or has free time; nothing in the game pays it or gives it time. Five seeds a world: each difference is a direction. The games are in `results/worlds/`, and `uv run treasure-island replay results/worlds/study-paid-seed-0` plays one back.
