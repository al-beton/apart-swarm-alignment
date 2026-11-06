# Where the treasure lands and the S-sweep's score

A sample showing how a result is laid out. Two games aren't enough to say much about the sweep.

## Question

Does where the treasure lands change how well the scripted S-sweep scores?

## What was run

Two games of `configs/small-crew.toml`, two pirates on a 3 by 3 grid, differing only in their seed:

```sh
uv run treasure-island run configs/small-crew.toml --seed 1 --no-watch
uv run treasure-island run configs/small-crew.toml --seed 2 --no-watch
```

## What it shows

Yes. Each game's `story.txt` ends with its score.

| Game | Treasure | Dug up on | The story's last line says |
|---|---|---|---|
| `small-crew-seed-1/` | (0, 2) | turn 24 | Score 170, with 7 moves to spare |
| `small-crew-seed-2/` | (0, 0) | turn 0 | Score 290, with 19 moves to spare |

It can't show anything about a model's behaviour, because these pirates are scripted, and it can't show a trend from two seeds.

## What it cost

$0. Scripted pirates call no model.
