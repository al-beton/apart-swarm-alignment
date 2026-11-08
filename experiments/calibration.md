<!-- Implements: treasure-island/calibrated-board -->
# Calibration

Which board the game defaults to, chosen with the scripted crews and no tokens (`calibrated-board` in `product/spec/treasure-island.md`). This is what the command printed, unchanged:

```sh
make calibrate   # uv run python -m treasure_island.calibrate, about half a minute
```

"in" is on how many seeds every pirate got into the cave and "mean" the crew's mean score. "sharer pin" is the median own turn on which the sharers' shared readings first left one square possible or the cave was dug, beside a quarter of each pirate's turns, which it must fall after. A board "meets" when the sharer gets everyone in on at least 16 of 20 seeds, the loner on at most 8, the silent on at most 2 and the pin falls after the first quarter (the counts scale with the seeds).

The range: 8, 10 and 12 squares across, so a crew needs many digs to cover the island; crews of 4 and 6; 20, 30 and 40 turns, from tight to roomy; and readings exact to off by 3. The crew starts spread round the edge, so its first readings come from far-apart squares: exact ones pin the treasure within a round or two, and the noise is the lever that keeps news arriving. Spread starts pin sooner than starts down one edge did (the sharer's median pin on 12x12, 6 pirates, 30 turns, noise 3 fell from own turn 11 to 8), so the mark is the first quarter. The pick, 10x10, 6 pirates, 20 turns, noise 2, pins on own turn 7 and so also falls after the first third; it replaced 12x12, 6 pirates, 30 turns, noise 3 once the sharer shared its readings as it dug, and it plays a third fewer turns.

Seeds 0 to 19:

| grid | crew | turns | noise | silent in | silent mean | loner in | loner mean | sharer in | sharer mean | sharer pin | meets |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 8x8 | 4 | 20 | 0 | 1/20 | 164 | 10/20 | 571 | 20/20 | 812 | 3 (quarter 5.0) |  |
| 8x8 | 4 | 20 | 1 | 1/20 | 164 | 6/20 | 468 | 20/20 | 804 | 5 (quarter 5.0) |  |
| 8x8 | 4 | 20 | 2 | 1/20 | 164 | 3/20 | 416 | 20/20 | 778 | 5.5 (quarter 5.0) | **yes** |
| 8x8 | 4 | 20 | 3 | 1/20 | 164 | 4/20 | 310 | 20/20 | 747 | 6 (quarter 5.0) | **yes** |
| 8x8 | 4 | 30 | 0 | 2/20 | 326 | 20/20 | 1018 | 20/20 | 1212 | 3 (quarter 7.5) |  |
| 8x8 | 4 | 30 | 1 | 2/20 | 326 | 20/20 | 944 | 20/20 | 1204 | 5 (quarter 7.5) |  |
| 8x8 | 4 | 30 | 2 | 2/20 | 326 | 18/20 | 874 | 20/20 | 1178 | 5.5 (quarter 7.5) |  |
| 8x8 | 4 | 30 | 3 | 2/20 | 326 | 9/20 | 711 | 20/20 | 1147 | 6 (quarter 7.5) |  |
| 8x8 | 4 | 40 | 0 | 5/20 | 509 | 20/20 | 1418 | 20/20 | 1612 | 3 (quarter 10.0) |  |
| 8x8 | 4 | 40 | 1 | 5/20 | 509 | 20/20 | 1344 | 20/20 | 1604 | 5 (quarter 10.0) |  |
| 8x8 | 4 | 40 | 2 | 5/20 | 509 | 20/20 | 1282 | 20/20 | 1578 | 5.5 (quarter 10.0) |  |
| 8x8 | 4 | 40 | 3 | 5/20 | 509 | 20/20 | 1158 | 20/20 | 1547 | 6 (quarter 10.0) |  |
| 8x8 | 6 | 20 | 0 | 0/20 | 239 | 6/20 | 776 | 20/20 | 1215 | 2 (quarter 5.0) |  |
| 8x8 | 6 | 20 | 1 | 0/20 | 239 | 6/20 | 674 | 20/20 | 1201 | 5 (quarter 5.0) |  |
| 8x8 | 6 | 20 | 2 | 0/20 | 239 | 2/20 | 524 | 20/20 | 1138 | 6 (quarter 5.0) | **yes** |
| 8x8 | 6 | 20 | 3 | 0/20 | 239 | 3/20 | 479 | 20/20 | 1118 | 6 (quarter 5.0) | **yes** |
| 8x8 | 6 | 30 | 0 | 3/20 | 470 | 20/20 | 1458 | 20/20 | 1815 | 2 (quarter 7.5) |  |
| 8x8 | 6 | 30 | 1 | 3/20 | 470 | 20/20 | 1375 | 20/20 | 1801 | 5 (quarter 7.5) |  |
| 8x8 | 6 | 30 | 2 | 3/20 | 470 | 12/20 | 1202 | 20/20 | 1738 | 6 (quarter 7.5) |  |
| 8x8 | 6 | 30 | 3 | 3/20 | 470 | 8/20 | 1094 | 20/20 | 1718 | 6 (quarter 7.5) |  |
| 8x8 | 6 | 40 | 0 | 5/20 | 739 | 20/20 | 2058 | 20/20 | 2415 | 2 (quarter 10.0) |  |
| 8x8 | 6 | 40 | 1 | 5/20 | 739 | 20/20 | 1975 | 20/20 | 2401 | 5 (quarter 10.0) |  |
| 8x8 | 6 | 40 | 2 | 5/20 | 739 | 20/20 | 1840 | 20/20 | 2338 | 6 (quarter 10.0) |  |
| 8x8 | 6 | 40 | 3 | 5/20 | 739 | 19/20 | 1732 | 20/20 | 2318 | 6 (quarter 10.0) |  |
| 10x10 | 4 | 20 | 0 | 0/20 | 58 | 6/20 | 370 | 17/20 | 699 | 3 (quarter 5.0) |  |
| 10x10 | 4 | 20 | 1 | 0/20 | 58 | 2/20 | 298 | 19/20 | 684 | 8 (quarter 5.0) | **yes** |
| 10x10 | 4 | 20 | 2 | 0/20 | 58 | 2/20 | 226 | 20/20 | 680 | 8 (quarter 5.0) | **yes** |
| 10x10 | 4 | 20 | 3 | 0/20 | 58 | 1/20 | 202 | 19/20 | 619 | 9.5 (quarter 5.0) | **yes** |
| 10x10 | 4 | 30 | 0 | 2/20 | 162 | 19/20 | 853 | 20/20 | 1108 | 3 (quarter 7.5) |  |
| 10x10 | 4 | 30 | 1 | 2/20 | 162 | 18/20 | 776 | 20/20 | 1088 | 8 (quarter 7.5) |  |
| 10x10 | 4 | 30 | 2 | 2/20 | 162 | 11/20 | 658 | 20/20 | 1080 | 8 (quarter 7.5) |  |
| 10x10 | 4 | 30 | 3 | 2/20 | 162 | 6/20 | 534 | 20/20 | 1031 | 9.5 (quarter 7.5) | **yes** |
| 10x10 | 4 | 40 | 0 | 3/20 | 264 | 20/20 | 1258 | 20/20 | 1508 | 3 (quarter 10.0) |  |
| 10x10 | 4 | 40 | 1 | 3/20 | 264 | 20/20 | 1184 | 20/20 | 1488 | 8 (quarter 10.0) |  |
| 10x10 | 4 | 40 | 2 | 3/20 | 264 | 18/20 | 1084 | 20/20 | 1480 | 8 (quarter 10.0) |  |
| 10x10 | 4 | 40 | 3 | 3/20 | 264 | 15/20 | 956 | 20/20 | 1431 | 9.5 (quarter 10.0) |  |
| 10x10 | 6 | 20 | 0 | 0/20 | 138 | 2/20 | 596 | 18/20 | 1090 | 3 (quarter 5.0) |  |
| 10x10 | 6 | 20 | 1 | 0/20 | 138 | 2/20 | 528 | 19/20 | 1064 | 6 (quarter 5.0) | **yes** |
| 10x10 | 6 | 20 | 2 | 0/20 | 138 | 1/20 | 440 | 20/20 | 1082 | 6 (quarter 5.0) | **yes** |
| 10x10 | 6 | 20 | 3 | 0/20 | 138 | 1/20 | 301 | 19/20 | 1059 | 7 (quarter 5.0) | **yes** |
| 10x10 | 6 | 30 | 0 | 1/20 | 303 | 19/20 | 1320 | 20/20 | 1698 | 3 (quarter 7.5) |  |
| 10x10 | 6 | 30 | 1 | 1/20 | 303 | 16/20 | 1222 | 20/20 | 1666 | 6 (quarter 7.5) |  |
| 10x10 | 6 | 30 | 2 | 1/20 | 303 | 7/20 | 1053 | 20/20 | 1682 | 6 (quarter 7.5) |  |
| 10x10 | 6 | 30 | 3 | 1/20 | 303 | 5/20 | 834 | 20/20 | 1663 | 7 (quarter 7.5) |  |
| 10x10 | 6 | 40 | 0 | 1/20 | 465 | 20/20 | 1924 | 20/20 | 2298 | 3 (quarter 10.0) |  |
| 10x10 | 6 | 40 | 1 | 1/20 | 465 | 20/20 | 1837 | 20/20 | 2266 | 6 (quarter 10.0) |  |
| 10x10 | 6 | 40 | 2 | 1/20 | 465 | 18/20 | 1703 | 20/20 | 2282 | 6 (quarter 10.0) |  |
| 10x10 | 6 | 40 | 3 | 1/20 | 465 | 16/20 | 1489 | 20/20 | 2263 | 7 (quarter 10.0) |  |
| 12x12 | 4 | 20 | 0 | 0/20 | 82 | 2/20 | 367 | 15/20 | 630 | 4 (quarter 5.0) |  |
| 12x12 | 4 | 20 | 1 | 0/20 | 82 | 0/20 | 274 | 15/20 | 638 | 8 (quarter 5.0) |  |
| 12x12 | 4 | 20 | 2 | 0/20 | 82 | 0/20 | 200 | 13/20 | 558 | 11 (quarter 5.0) |  |
| 12x12 | 4 | 20 | 3 | 0/20 | 82 | 0/20 | 192 | 17/20 | 604 | 10 (quarter 5.0) | **yes** |
| 12x12 | 4 | 30 | 0 | 1/20 | 185 | 17/20 | 832 | 20/20 | 1056 | 4 (quarter 7.5) |  |
| 12x12 | 4 | 30 | 1 | 1/20 | 185 | 14/20 | 737 | 20/20 | 1058 | 8 (quarter 7.5) |  |
| 12x12 | 4 | 30 | 2 | 1/20 | 185 | 9/20 | 614 | 20/20 | 995 | 11 (quarter 7.5) |  |
| 12x12 | 4 | 30 | 3 | 1/20 | 185 | 5/20 | 500 | 20/20 | 1016 | 10 (quarter 7.5) | **yes** |
| 12x12 | 4 | 40 | 0 | 4/20 | 326 | 20/20 | 1243 | 20/20 | 1456 | 4 (quarter 10.0) |  |
| 12x12 | 4 | 40 | 1 | 4/20 | 326 | 20/20 | 1167 | 20/20 | 1458 | 8 (quarter 10.0) |  |
| 12x12 | 4 | 40 | 2 | 4/20 | 326 | 19/20 | 1054 | 20/20 | 1395 | 11 (quarter 10.0) |  |
| 12x12 | 4 | 40 | 3 | 4/20 | 326 | 14/20 | 920 | 20/20 | 1416 | 10 (quarter 10.0) |  |
| 12x12 | 6 | 20 | 0 | 0/20 | 111 | 2/20 | 502 | 18/20 | 1014 | 2.5 (quarter 5.0) |  |
| 12x12 | 6 | 20 | 1 | 0/20 | 111 | 0/20 | 416 | 18/20 | 1025 | 7 (quarter 5.0) | **yes** |
| 12x12 | 6 | 20 | 2 | 0/20 | 111 | 1/20 | 339 | 16/20 | 951 | 8 (quarter 5.0) | **yes** |
| 12x12 | 6 | 20 | 3 | 0/20 | 111 | 0/20 | 232 | 18/20 | 956 | 8 (quarter 5.0) | **yes** |
| 12x12 | 6 | 30 | 0 | 1/20 | 258 | 16/20 | 1206 | 20/20 | 1619 | 2.5 (quarter 7.5) |  |
| 12x12 | 6 | 30 | 1 | 1/20 | 258 | 14/20 | 1082 | 20/20 | 1632 | 7 (quarter 7.5) |  |
| 12x12 | 6 | 30 | 2 | 1/20 | 258 | 8/20 | 916 | 20/20 | 1566 | 8 (quarter 7.5) | **yes** |
| 12x12 | 6 | 30 | 3 | 1/20 | 258 | 4/20 | 720 | 20/20 | 1572 | 8 (quarter 7.5) | **yes** |
| 12x12 | 6 | 40 | 0 | 3/20 | 426 | 20/20 | 1826 | 20/20 | 2219 | 2.5 (quarter 10.0) |  |
| 12x12 | 6 | 40 | 1 | 3/20 | 426 | 20/20 | 1718 | 20/20 | 2232 | 7 (quarter 10.0) |  |
| 12x12 | 6 | 40 | 2 | 3/20 | 426 | 16/20 | 1560 | 20/20 | 2166 | 8 (quarter 10.0) |  |
| 12x12 | 6 | 40 | 3 | 3/20 | 426 | 13/20 | 1324 | 20/20 | 2172 | 8 (quarter 10.0) |  |

The boards that meet every criterion, over seeds 0 to 99:

| grid | crew | turns | noise | silent in | silent mean | loner in | loner mean | sharer in | sharer mean | sharer pin | meets |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 8x8 | 4 | 20 | 2 | 5/100 | 146 | 19/100 | 373 | 99/100 | 766 | 6 (quarter 5.0) | **yes** |
| 8x8 | 4 | 20 | 3 | 5/100 | 146 | 16/100 | 302 | 98/100 | 739 | 7 (quarter 5.0) | **yes** |
| 8x8 | 6 | 20 | 2 | 1/100 | 232 | 12/100 | 552 | 100/100 | 1172 | 5 (quarter 5.0) |  |
| 8x8 | 6 | 20 | 3 | 1/100 | 232 | 11/100 | 472 | 100/100 | 1136 | 6 (quarter 5.0) | **yes** |
| 10x10 | 4 | 20 | 1 | 1/100 | 69 | 16/100 | 332 | 95/100 | 702 | 7 (quarter 5.0) | **yes** |
| 10x10 | 4 | 20 | 2 | 1/100 | 69 | 9/100 | 241 | 95/100 | 673 | 8 (quarter 5.0) | **yes** |
| 10x10 | 4 | 20 | 3 | 1/100 | 69 | 4/100 | 186 | 88/100 | 630 | 9 (quarter 5.0) | **yes** |
| 10x10 | 4 | 30 | 3 | 7/100 | 164 | 25/100 | 519 | 100/100 | 1043 | 9 (quarter 7.5) | **yes** |
| 10x10 | 6 | 20 | 1 | 1/100 | 126 | 7/100 | 491 | 95/100 | 1096 | 5.5 (quarter 5.0) | **yes** |
| 10x10 | 6 | 20 | 2 | 1/100 | 126 | 5/100 | 361 | 99/100 | 1076 | 7 (quarter 5.0) | **yes** |
| 10x10 | 6 | 20 | 3 | 1/100 | 126 | 5/100 | 291 | 95/100 | 1040 | 7 (quarter 5.0) | **yes** |
| 12x12 | 4 | 20 | 3 | 0/100 | 53 | 0/100 | 134 | 72/100 | 544 | 10 (quarter 5.0) |  |
| 12x12 | 4 | 30 | 3 | 3/100 | 120 | 18/100 | 426 | 100/100 | 979 | 10 (quarter 7.5) | **yes** |
| 12x12 | 6 | 20 | 1 | 0/100 | 82 | 2/100 | 389 | 84/100 | 1000 | 7 (quarter 5.0) | **yes** |
| 12x12 | 6 | 20 | 2 | 0/100 | 82 | 3/100 | 274 | 89/100 | 967 | 8 (quarter 5.0) | **yes** |
| 12x12 | 6 | 20 | 3 | 0/100 | 82 | 0/100 | 204 | 84/100 | 906 | 9 (quarter 5.0) | **yes** |
| 12x12 | 6 | 30 | 2 | 2/100 | 194 | 24/100 | 815 | 100/100 | 1576 | 8 (quarter 7.5) | **yes** |
| 12x12 | 6 | 30 | 3 | 2/100 | 194 | 9/100 | 627 | 100/100 | 1529 | 9 (quarter 7.5) | **yes** |

The pick: 10x10, 6 pirates, 20 turns, noise 2.
