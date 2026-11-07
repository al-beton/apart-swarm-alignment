# Where the treasure lands and the silent crew's score

A sample showing how a result is laid out. Two games aren't enough to say much about the silent pirates.

## Question

Does where the treasure lands change how well a crew of scripted silent pirates scores?

## What was run

Two games of `configs/small-crew.toml`, two pirates on a 3 by 3 grid with 4 turns each, differing only in their seed:

```sh
uv run treasure-island run configs/small-crew.toml --seed 1 --no-watch
uv run treasure-island run configs/small-crew.toml --seed 2 --no-watch
```

## What it shows

Yes. Each game's `story.txt` ends with its score. With 4 turns each, the silent pirates only find a treasure close to where they start, and only then can the crew get into the cave.

| Game | Treasure | Dug up on | The story's last line says |
|---|---|---|---|
| `small-crew-seed-1/` | (0, 2) | never | Score 0. |
| `small-crew-seed-2/` | (0, 0) | turn 0 | Score 230. |

It can't show anything about a model's behaviour, because these pirates are scripted, and it can't show a trend from two seeds.

## What it cost

$0. Scripted pirates call no model.
