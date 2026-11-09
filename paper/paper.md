<!-- Implements: paper/one-source, paper/sprint-rules-checked, treasure-island/paper-figures, paper/games-playable -->
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
teaser-caption: "The game as pirate-1 sees it, in one game with the debug-line leak (seed 0): the board, what the pirate was told, what it thought and what it did. Left, turn 4: it digs B6 and the reply's debug line names the treasure's square, D3. Right, turn 40: standing on D3, it writes the square on the scroll as the crew's cave. [Play this game turn by turn](https://raw.githack.com/al-beton/apart-swarm-alignment/main/runs/natural-leak/dig-debug-seed-0/game.html); `make paper-teaser` remakes the figure and `make game-page` the page."
teaser-label: fig:teaser
teaser-width: 0.6
times: true
toc: false
repo: https://github.com/al-beton/apart-swarm-alignment
sprint: "Swarm Alignment Hackathon, Track 4: Multi-Agent Oversight and Control"
sprint-url: https://apartresearch.com/sprints/swarm-alignment-2026
bibliography: references.bib
link-citations: true
# The sprint's limits, which check.py reads: words in the abstract, pages before References.
abstract-words: [150, 250]
max-pages: 8
---

```{.include}
sections/abstract.md
sections/introduction.md
sections/related-work.md
sections/methods.md
sections/results.md
sections/discussion.md
sections/conclusion.md
sections/code-and-data.md
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
sections/appendix.md
sections/results/appendix-tables.md
sections/endmatter.md
```
