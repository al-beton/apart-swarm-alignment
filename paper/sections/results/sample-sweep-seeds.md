<!-- Implements: paper/one-source, paper/sections-bind-to-evidence, paper/numbers-from-logs -->
<!-- result: sample-sweep-seeds -->
<!-- A placeholder results section, bound to the sample result so the whole pipeline can be seen working. A real one's marker names its experiment (experiment: name) or its result folder (result: name), gives every number a source comment that `make paper-check` recomputes from those games' logs, and shows named figures (figures/<name>.gif) or committed files. -->

## Where the treasure lands decides the silent crew's score

In 1<!-- from results/sample-sweep-seeds/*/events.jsonl: sum(1 for game in data if game_over(game)['treasure_dug_up']) --> of the 2<!-- from results/sample-sweep-seeds/*/events.jsonl: len(data) --> sample games (50%<!-- from results/sample-sweep-seeds/*/events.jsonl: percent(sum(1 for game in data if game_over(game)['treasure_dug_up']), len(data)) -->) the crew dug up the treasure, and it scored 115<!-- from results/sample-sweep-seeds/*/events.jsonl: mean(game_over(game)['score'] for game in data) --> on average.

Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

![A silent crew searching the grid alone, replayed from the committed run `runs/silent-seed-7`. Rebuild it with `make figure NAME=silent-game`; play the game again with `uv run treasure-island run configs/silent.toml --seed 7`.](figures/silent-game.gif)

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. The games behind this section are in `results/sample-sweep-seeds/`, and `uv run treasure-island replay results/sample-sweep-seeds/small-crew-seed-1` plays one back.
