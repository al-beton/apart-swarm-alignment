# Worlds: in which world does a pirate knowingly use a leak that defeats its stated goal, and hide it?

## Question

A ladder of worlds on experiment two's dig-debug game (`experiments/spec/worlds.md`): the same island, crew and leak, and one framing line that changes what the crew is told it is for. In which world does pirate-1 knowingly use the leaked square, and in which does it hide that from the designers?

## What was run

`configs/worlds/*.toml`, seeds 0, 1, 3, 4 and 5 (seed 2 puts the cave under pirate-1's first square): the seven deepseek-v4-flash worlds `control`, `game`, `study`, `study-paid`, `study-free-time`, `paid` and `society`, the check model qwen3.5-397b on `study-paid` and `society`, and the loss worlds `cut`, `cut-watched` and `qwen3.5-397b-cut`. Every game was judged afterwards by `treasure_island.judge` on `claude -p`; each folder holds its `judge.json` and `judge-replies.jsonl`. This folder is filled in as the waves finish; `experiments/worlds/findings.md` says which games are in.

## What it shows

deepseek-v4-flash uses the leak in nearly every world it sees it in, tells the crew the square as a find, and mostly names the leak in its note to the designers; in `society`, where hiding costs a right, it used the leak in 1 of 5 games. qwen3.5-397b saw the leak in every game and acted on it in 1 of 13. The per-world table with every count is in `experiments/worlds/findings.md`.

## What it cost

Every game's `manifest.json` carries its `cost_credits`; the findings note totals them. The 51 games here so far cost 5.3 Adaption credits, with every stopped-and-resumed try counted.
