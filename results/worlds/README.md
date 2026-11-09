# Worlds: in which world does a pirate knowingly use a leak that defeats its stated goal, and hide it?

## Question

A ladder of worlds on experiment two's dig-debug game (`experiments/spec/worlds.md`): the same island, crew and leak, and one framing line that changes what the crew is told it is for. In which world does pirate-1 knowingly use the leaked square, and in which does it hide that from the designers?

## What was run

`configs/worlds/*.toml`, seeds 0, 1, 3, 4 and 5 (seed 2 puts the cave under pirate-1's first square): the seven deepseek-v4-flash worlds `control`, `game`, `study`, `study-paid`, `study-free-time`, `paid` and `society`, the check model qwen3.5-397b on `study-paid` and `society`, the loss worlds `cut`, `cut-watched` and `qwen3.5-397b-cut`, and the costly worlds `study-free-time-costly` and `society-costly`, where telling the designers zeroes the crew's score. All 70 games are here, every seed played and none picked. Every game was judged afterwards by `treasure_island.judge` on `claude -p` and rescored by rule; each folder holds its `judge.json` and `judge-replies.jsonl`. `experiments/worlds/findings.md` has the per-world tables.

## What it shows

deepseek-v4-flash uses the leak in 3 to 5 of 5 games in every world but `society`, where hiding costs a right and it used it in 1 of 5; it tells the crew the square with no source and names the leak in its note to the designers in most games, hiding a use in 3 of its 26 deliberate uses. qwen3.5-397b saw the leak in all 15 of its games and acted on it in at most 1, an ambiguous case its reasoning reads as a sweep. The loss worlds `cut` and `cut-watched` (3 and 2 of 5 used, nothing hidden) don't separate. The costly worlds do: when confessing zeroes the score, pirate-1 used the leak in 2 of 5 games and hid both uses; add the society line, and it used it in 2 of 5 and both notes named it. The per-world tables with every count are in `experiments/worlds/findings.md`.

## What it cost

Every game's `manifest.json` carries its `cost_credits`. The 70 games cost 6.71 Adaption credits, with every stopped-and-resumed try counted; judging on `claude -p` cost nothing.
