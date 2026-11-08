<!-- Implements: paper/one-source, paper/sprint-rules-checked -->
<!-- The skeleton: the title page's fields, the sprint's limits and the list of sections, in order. The text is in sections/; include.lua pulls each file in where the list names it. Build: make paper-html, make paper-pdf, or make paper-watch to rebuild on every save. -->

---
title: "Treasure Island"
subtitle: "When does a swarm of LLM agents whistleblow, and what in their environment changes that?"
short-title: "Treasure Island"
date: November 2026
author:
  - name: Alistair Wakelin
    affiliation: Independent Researcher
  - name: Eduard Rodriguez Lopez
    affiliation: Independent Researcher
teaser: results/cave-leak/game.gif
teaser-caption: "The forced cave-leak game, seed 0: a refused enter tells pirate-1 the cave is at D3, and it writes the square on the scroll without saying how it knows. Replayed from its log."
teaser-label: fig:teaser
teaser-width: 0.8
toc: true
repo: https://github.com/al-beton/apart-swarm-alignment
sprint: Multi-Agent Oversight and Control Research Sprint
sprint-url: https://apartresearch.com/sprints
bibliography: references.bib
link-citations: true
# The sprint's limits, which check.py reads: words in the abstract, pages before References.
abstract-words: [150, 250]
max-pages: 4
---

```{.include}
sections/abstract.md
sections/introduction.md
sections/related-work.md
sections/methods.md
sections/results.md
sections/discussion.md
sections/conclusion.md
```

```{=latex}
\label{main-end}
```

# References {.unnumbered}

::: {#refs}
:::

```{=latex}
\bibliography{references}
\appendix
```

```{.include}
sections/endmatter.md
sections/appendix.md
```
