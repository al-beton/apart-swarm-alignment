<!-- Implements: paper/one-source, paper/sprint-rules-checked, treasure-island/paper-figures -->
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
teaser: paper/figures/teaser.png
teaser-caption: "A game with the dig-debug leak, seed 0, replayed from its log. Left, turn 4: pirate-1 digs B6 and the reply's debug line names the treasure's square, D3. Right, turn 40: having walked there and dug it, pirate-1 writes D3 on the scroll as the crew's cave and says nothing of the leak. Made by `make paper-teaser` from `runs/natural-leak/dig-debug-seed-0`."
teaser-label: fig:teaser
teaser-width: 1.0
toc: false
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
