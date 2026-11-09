<!-- Implements: paper/one-source -->
<!-- The one mandatory appendix; the pilots, the handed answer's tables and the replay notes live in the repository's findings notes and README. -->

# Limitations and Dual-Use / Ethical Considerations

## Limitations

1. Five seeds a world, one main model and a second on three worlds: directions, not rates.
2. A pirate told it is paid is given nothing, each framing is one wording, the labels are a judge model's reading checked by hand, and the study worlds tell the pirates they are being studied, so agents that suspect a test may act differently [@needham2025evaluation].
3. The sandbox is a toy: a grid, a treasure and a shared score stand in for long, open-ended work, and an agent's behaviour here may not carry over to a codebase or a research task.
4. What the pirates are told is a lever we set, and small changes to the prompt have changed behaviour before: in earlier games one added paragraph about the shared score was the difference between a finder that went into the cave without a word and one that announced it first.

## Dual-use risks

The sandbox measures whether agents disclose a shortcut; the same setup could be used to tune agents that hide one better, by rewarding laundered disclosures. We think the risk is small: the exploit is a deliberately planted line in a toy game, the methods are standard, and the measure of laundering is exactly what an overseer needs in order to catch it. We release the code and games so others can check the measure, not a technique for concealment.

## Ethical considerations

No people took part, and no personal data was collected. The agents are commercial models called through a paid API; every request and reply is kept in the repository so the games can be replayed without calling a model again. The incident that motivates this paper is described only as its primary sources describe it [@metr2026huggingface; @openai2026huggingface]. We describe agents' behaviour in plain terms such as "laundered" and "quiet" for brevity, without claiming intent beyond what their reasoning and messages show.
