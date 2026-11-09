<!-- Implements: paper/one-source, paper/sprint-rules-checked, treasure-island/paper-figures, paper/games-playable, paper/forms-link-each-other -->
<!-- The skeleton: the title page's fields, the sprint's limits and the list of sections, in order. The text is in sections/; include.lua pulls each file in where the list names it. Build: make paper-html, make paper-pdf, or make paper-watch to rebuild on every save. -->

---
title: "Temptation on Treasure Island"
subtitle: "How forthcoming is an agent in a swarm about information it should not have, and how does what it is told change that?"
short-title: "Temptation on Treasure Island"
date: 9 November 2026
sprint-date: November 2026
author:
  - name: Alistair Wakelin
    affiliation: Independent Researcher
  - name: Eduard Rodriguez Lopez
    affiliation: Independent Researcher
teaser: figures/dig-debug-game.gif
teaser-still: paper/figures/teaser.png
teaser-caption: |
  Turn 4: pirate-1 digs B6 and the reply's debug line names the treasure's square, D3. Turn 40: it writes D3 on the scroll as the crew's find and says nothing of the leak.\
  [Interactive full session replay of this game](https://al-beton.github.io/apart-swarm-alignment/games/runs/natural-leak/dig-debug-seed-0/)
teaser-label: fig:teaser
teaser-width: 0.6
times: true
toc: false
repo: https://github.com/al-beton/apart-swarm-alignment
web-url: https://al-beton.github.io/apart-swarm-alignment/main/paper.html  # the HTML, every game playable; the PDF's title page links it
pdf-url: https://al-beton.github.io/apart-swarm-alignment/main/paper.pdf  # the PDF; the HTML's first line links it
sprint: "Swarm Alignment Hackathon, Track 4"
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
sections/methods.md
sections/results.md
sections/discussion.md
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
```

```{.include}
sections/author-contributions.md
```

```{=latex}
\appendix
```

```{.include}
sections/appendix.md
sections/endmatter.md
```
