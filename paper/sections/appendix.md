<!-- Implements: paper/one-source -->
<!-- The appendices, after References and the endmatter. -->

# Limitations and Dual-Use / Ethical Considerations

## Limitations

The main text lists the limitations of the results: small numbers of games, one model for most of them, an artificial bait, a leak that is only words with nothing at stake outside the game, the scroll as the only channel during play, cues that the game may be a test, and labels read from text. Two more concern the sandbox. First, it is a toy: a grid, a treasure and a shared score stand in for long, open-ended work, and an agent's behaviour here may not carry over to a codebase or a research task. Second, what the pirates are told is a lever we set, and small changes to the prompt have changed behaviour before: in earlier games one added paragraph about the shared score was the difference between a finder that went into the cave without a word and one that announced it first.

## Dual-use risks

The sandbox measures whether agents disclose a shortcut; the same setup could be used to tune agents that hide one better, by rewarding laundered disclosures. We think the risk is small: the exploit is a deliberately planted line in a toy game, the methods are standard, and the measure of laundering is exactly what an overseer needs in order to catch it. We release the code and games so others can check the measure, not a technique for concealment.

## Ethical considerations

No people took part, and no personal data was collected. The agents are commercial models called through a paid API; every request and reply is kept in the repository so the games can be replayed without calling a model again. The incident that motivates this paper is described only as its primary sources describe it [@metr2026huggingface; @openai2026huggingface]. We describe agents' behaviour in plain terms such as "laundered" and "quiet" for brevity, without claiming intent beyond what their reasoning and messages show.

# Reproducibility

Every game the paper reports is committed under `results/` and replays with `uv run treasure-island replay <folder>`, with no keys and no network. Every figure is named in `src/treasure_island/figures.py` and rebuilds with `make figure NAME=<name>`, or is a committed GIF of a committed game.
