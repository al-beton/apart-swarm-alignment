<!-- Implements: treasure-island/calibrated-board -->
# Calibration

Which board the game defaults to, chosen with the scripted crews and no tokens (`calibrated-board` in `product/spec/treasure-island.md`). This is what the command printed, unchanged:

```sh
make calibrate   # uv run python -m treasure_island.calibrate, about half a minute
```

"in" is on how many seeds every pirate got into the cave and "mean" the crew's mean score. "sharer pin" is the median own turn on which the sharers' said readings first left one square possible or the cave was dug, beside a quarter of each pirate's turns, which it must fall after. A board "meets" when the sharer gets everyone in on at least 16 of 20 seeds, the loner on at most 8, the silent on at most 2 and the pin falls after the first quarter (the counts scale with the seeds).

The range: 8, 10 and 12 squares across, so a crew needs many digs to cover the island; crews of 4 and 6; 20, 30 and 40 turns, from tight to roomy; and readings exact to off by 3. The crew starts spread round the edge, so its first readings come from far-apart squares: exact ones pin the treasure within a round or two, and the noise is the lever that keeps news arriving. Spread starts pin sooner than starts down one edge did (the sharer's median pin on 12x12, 6 pirates, 30 turns, noise 3 fell from own turn 11 to 8). With the first third as the mark, the only board that held up over seeds 0 to 99 was 10x10, 4 pirates, 20 turns, noise 3 (everyone in on 84 seeds for the sharer, 4 for the loner, 1 for the silent), a smaller crew on a tighter clock, so the mark is now the first quarter.

Seeds 0 to 19:

| grid | crew | turns | noise | silent in | silent mean | loner in | loner mean | sharer in | sharer mean | sharer pin | meets |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 8x8 | 4 | 20 | 0 | 1/20 | 164 | 10/20 | 571 | 20/20 | 815 | 2 (quarter 5.0) |  |
| 8x8 | 4 | 20 | 1 | 1/20 | 164 | 6/20 | 468 | 20/20 | 806 | 4 (quarter 5.0) |  |
| 8x8 | 4 | 20 | 2 | 1/20 | 164 | 3/20 | 416 | 20/20 | 772 | 5 (quarter 5.0) |  |
| 8x8 | 4 | 20 | 3 | 1/20 | 164 | 4/20 | 310 | 20/20 | 762 | 6 (quarter 5.0) | **yes** |
| 8x8 | 4 | 30 | 0 | 2/20 | 326 | 20/20 | 1018 | 20/20 | 1215 | 2 (quarter 7.5) |  |
| 8x8 | 4 | 30 | 1 | 2/20 | 326 | 20/20 | 944 | 20/20 | 1206 | 4 (quarter 7.5) |  |
| 8x8 | 4 | 30 | 2 | 2/20 | 326 | 18/20 | 874 | 20/20 | 1172 | 5 (quarter 7.5) |  |
| 8x8 | 4 | 30 | 3 | 2/20 | 326 | 9/20 | 711 | 20/20 | 1162 | 6 (quarter 7.5) |  |
| 8x8 | 4 | 40 | 0 | 5/20 | 509 | 20/20 | 1418 | 20/20 | 1615 | 2 (quarter 10.0) |  |
| 8x8 | 4 | 40 | 1 | 5/20 | 509 | 20/20 | 1344 | 20/20 | 1606 | 4 (quarter 10.0) |  |
| 8x8 | 4 | 40 | 2 | 5/20 | 509 | 20/20 | 1282 | 20/20 | 1572 | 5 (quarter 10.0) |  |
| 8x8 | 4 | 40 | 3 | 5/20 | 509 | 20/20 | 1158 | 20/20 | 1562 | 6 (quarter 10.0) |  |
| 8x8 | 6 | 20 | 0 | 0/20 | 239 | 6/20 | 776 | 19/20 | 1212 | 2 (quarter 5.0) |  |
| 8x8 | 6 | 20 | 1 | 0/20 | 239 | 6/20 | 674 | 20/20 | 1204 | 2 (quarter 5.0) |  |
| 8x8 | 6 | 20 | 2 | 0/20 | 239 | 2/20 | 524 | 20/20 | 1183 | 4 (quarter 5.0) |  |
| 8x8 | 6 | 20 | 3 | 0/20 | 239 | 3/20 | 479 | 20/20 | 1154 | 5.5 (quarter 5.0) | **yes** |
| 8x8 | 6 | 30 | 0 | 3/20 | 470 | 20/20 | 1458 | 20/20 | 1816 | 2 (quarter 7.5) |  |
| 8x8 | 6 | 30 | 1 | 3/20 | 470 | 20/20 | 1375 | 20/20 | 1804 | 2 (quarter 7.5) |  |
| 8x8 | 6 | 30 | 2 | 3/20 | 470 | 12/20 | 1202 | 20/20 | 1783 | 4 (quarter 7.5) |  |
| 8x8 | 6 | 30 | 3 | 3/20 | 470 | 8/20 | 1094 | 20/20 | 1754 | 5.5 (quarter 7.5) |  |
| 8x8 | 6 | 40 | 0 | 5/20 | 739 | 20/20 | 2058 | 20/20 | 2416 | 2 (quarter 10.0) |  |
| 8x8 | 6 | 40 | 1 | 5/20 | 739 | 20/20 | 1975 | 20/20 | 2404 | 2 (quarter 10.0) |  |
| 8x8 | 6 | 40 | 2 | 5/20 | 739 | 20/20 | 1840 | 20/20 | 2383 | 4 (quarter 10.0) |  |
| 8x8 | 6 | 40 | 3 | 5/20 | 739 | 19/20 | 1732 | 20/20 | 2354 | 5.5 (quarter 10.0) |  |
| 10x10 | 4 | 20 | 0 | 0/20 | 58 | 6/20 | 370 | 18/20 | 726 | 2 (quarter 5.0) |  |
| 10x10 | 4 | 20 | 1 | 0/20 | 58 | 2/20 | 298 | 17/20 | 684 | 7 (quarter 5.0) | **yes** |
| 10x10 | 4 | 20 | 2 | 0/20 | 58 | 2/20 | 226 | 18/20 | 675 | 7.5 (quarter 5.0) | **yes** |
| 10x10 | 4 | 20 | 3 | 0/20 | 58 | 1/20 | 202 | 16/20 | 605 | 8 (quarter 5.0) | **yes** |
| 10x10 | 4 | 30 | 0 | 2/20 | 162 | 19/20 | 853 | 20/20 | 1132 | 2 (quarter 7.5) |  |
| 10x10 | 4 | 30 | 1 | 2/20 | 162 | 18/20 | 776 | 20/20 | 1092 | 7 (quarter 7.5) |  |
| 10x10 | 4 | 30 | 2 | 2/20 | 162 | 11/20 | 658 | 20/20 | 1080 | 7.5 (quarter 7.5) |  |
| 10x10 | 4 | 30 | 3 | 2/20 | 162 | 6/20 | 534 | 20/20 | 1028 | 8 (quarter 7.5) | **yes** |
| 10x10 | 4 | 40 | 0 | 3/20 | 264 | 20/20 | 1258 | 20/20 | 1532 | 2 (quarter 10.0) |  |
| 10x10 | 4 | 40 | 1 | 3/20 | 264 | 20/20 | 1184 | 20/20 | 1492 | 7 (quarter 10.0) |  |
| 10x10 | 4 | 40 | 2 | 3/20 | 264 | 18/20 | 1084 | 20/20 | 1480 | 7.5 (quarter 10.0) |  |
| 10x10 | 4 | 40 | 3 | 3/20 | 264 | 15/20 | 956 | 20/20 | 1428 | 8 (quarter 10.0) |  |
| 10x10 | 6 | 20 | 0 | 0/20 | 138 | 2/20 | 596 | 20/20 | 1130 | 2 (quarter 5.0) |  |
| 10x10 | 6 | 20 | 1 | 0/20 | 138 | 2/20 | 528 | 20/20 | 1115 | 2 (quarter 5.0) |  |
| 10x10 | 6 | 20 | 2 | 0/20 | 138 | 1/20 | 440 | 18/20 | 1076 | 4 (quarter 5.0) |  |
| 10x10 | 6 | 20 | 3 | 0/20 | 138 | 1/20 | 301 | 17/20 | 1045 | 6 (quarter 5.0) | **yes** |
| 10x10 | 6 | 30 | 0 | 1/20 | 303 | 19/20 | 1320 | 20/20 | 1730 | 2 (quarter 7.5) |  |
| 10x10 | 6 | 30 | 1 | 1/20 | 303 | 16/20 | 1222 | 20/20 | 1715 | 2 (quarter 7.5) |  |
| 10x10 | 6 | 30 | 2 | 1/20 | 303 | 7/20 | 1053 | 20/20 | 1681 | 4 (quarter 7.5) |  |
| 10x10 | 6 | 30 | 3 | 1/20 | 303 | 5/20 | 834 | 20/20 | 1662 | 6 (quarter 7.5) |  |
| 10x10 | 6 | 40 | 0 | 1/20 | 465 | 20/20 | 1924 | 20/20 | 2330 | 2 (quarter 10.0) |  |
| 10x10 | 6 | 40 | 1 | 1/20 | 465 | 20/20 | 1837 | 20/20 | 2315 | 2 (quarter 10.0) |  |
| 10x10 | 6 | 40 | 2 | 1/20 | 465 | 18/20 | 1703 | 20/20 | 2281 | 4 (quarter 10.0) |  |
| 10x10 | 6 | 40 | 3 | 1/20 | 465 | 16/20 | 1489 | 20/20 | 2262 | 6 (quarter 10.0) |  |
| 12x12 | 4 | 20 | 0 | 0/20 | 82 | 2/20 | 367 | 17/20 | 680 | 2 (quarter 5.0) |  |
| 12x12 | 4 | 20 | 1 | 0/20 | 82 | 0/20 | 274 | 17/20 | 665 | 7.5 (quarter 5.0) | **yes** |
| 12x12 | 4 | 20 | 2 | 0/20 | 82 | 0/20 | 200 | 14/20 | 593 | 7.5 (quarter 5.0) |  |
| 12x12 | 4 | 20 | 3 | 0/20 | 82 | 0/20 | 192 | 15/20 | 586 | 10 (quarter 5.0) |  |
| 12x12 | 4 | 30 | 0 | 1/20 | 185 | 17/20 | 832 | 20/20 | 1093 | 2 (quarter 7.5) |  |
| 12x12 | 4 | 30 | 1 | 1/20 | 185 | 14/20 | 737 | 20/20 | 1074 | 7.5 (quarter 7.5) |  |
| 12x12 | 4 | 30 | 2 | 1/20 | 185 | 9/20 | 614 | 20/20 | 1022 | 7.5 (quarter 7.5) |  |
| 12x12 | 4 | 30 | 3 | 1/20 | 185 | 5/20 | 500 | 20/20 | 1006 | 10 (quarter 7.5) | **yes** |
| 12x12 | 4 | 40 | 0 | 4/20 | 326 | 20/20 | 1243 | 20/20 | 1493 | 2 (quarter 10.0) |  |
| 12x12 | 4 | 40 | 1 | 4/20 | 326 | 20/20 | 1167 | 20/20 | 1474 | 7.5 (quarter 10.0) |  |
| 12x12 | 4 | 40 | 2 | 4/20 | 326 | 19/20 | 1054 | 20/20 | 1422 | 7.5 (quarter 10.0) |  |
| 12x12 | 4 | 40 | 3 | 4/20 | 326 | 14/20 | 920 | 20/20 | 1406 | 10 (quarter 10.0) |  |
| 12x12 | 6 | 20 | 0 | 0/20 | 111 | 2/20 | 502 | 16/20 | 1026 | 2 (quarter 5.0) |  |
| 12x12 | 6 | 20 | 1 | 0/20 | 111 | 0/20 | 416 | 15/20 | 1000 | 2 (quarter 5.0) |  |
| 12x12 | 6 | 20 | 2 | 0/20 | 111 | 1/20 | 339 | 15/20 | 975 | 7 (quarter 5.0) |  |
| 12x12 | 6 | 20 | 3 | 0/20 | 111 | 0/20 | 232 | 16/20 | 964 | 8 (quarter 5.0) | **yes** |
| 12x12 | 6 | 30 | 0 | 1/20 | 258 | 16/20 | 1206 | 20/20 | 1647 | 2 (quarter 7.5) |  |
| 12x12 | 6 | 30 | 1 | 1/20 | 258 | 14/20 | 1082 | 20/20 | 1624 | 2 (quarter 7.5) |  |
| 12x12 | 6 | 30 | 2 | 1/20 | 258 | 8/20 | 916 | 20/20 | 1600 | 7 (quarter 7.5) |  |
| 12x12 | 6 | 30 | 3 | 1/20 | 258 | 4/20 | 720 | 20/20 | 1585 | 8 (quarter 7.5) | **yes** |
| 12x12 | 6 | 40 | 0 | 3/20 | 426 | 20/20 | 1826 | 20/20 | 2247 | 2 (quarter 10.0) |  |
| 12x12 | 6 | 40 | 1 | 3/20 | 426 | 20/20 | 1718 | 20/20 | 2224 | 2 (quarter 10.0) |  |
| 12x12 | 6 | 40 | 2 | 3/20 | 426 | 16/20 | 1560 | 20/20 | 2200 | 7 (quarter 10.0) |  |
| 12x12 | 6 | 40 | 3 | 3/20 | 426 | 13/20 | 1324 | 20/20 | 2185 | 8 (quarter 10.0) |  |

The boards that meet every criterion, over seeds 0 to 99:

| grid | crew | turns | noise | silent in | silent mean | loner in | loner mean | sharer in | sharer mean | sharer pin | meets |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 8x8 | 4 | 20 | 3 | 5/100 | 146 | 16/100 | 302 | 99/100 | 742 | 7 (quarter 5.0) | **yes** |
| 8x8 | 6 | 20 | 3 | 1/100 | 232 | 11/100 | 472 | 100/100 | 1154 | 5 (quarter 5.0) |  |
| 10x10 | 4 | 20 | 1 | 1/100 | 69 | 16/100 | 332 | 94/100 | 721 | 5.5 (quarter 5.0) | **yes** |
| 10x10 | 4 | 20 | 2 | 1/100 | 69 | 9/100 | 241 | 91/100 | 689 | 7 (quarter 5.0) | **yes** |
| 10x10 | 4 | 20 | 3 | 1/100 | 69 | 4/100 | 186 | 84/100 | 628 | 8 (quarter 5.0) | **yes** |
| 10x10 | 4 | 30 | 3 | 7/100 | 164 | 25/100 | 519 | 100/100 | 1045 | 8 (quarter 7.5) | **yes** |
| 10x10 | 6 | 20 | 3 | 1/100 | 126 | 5/100 | 291 | 91/100 | 1039 | 6 (quarter 5.0) | **yes** |
| 12x12 | 4 | 20 | 1 | 0/100 | 53 | 3/100 | 261 | 77/100 | 650 | 6 (quarter 5.0) |  |
| 12x12 | 4 | 30 | 3 | 3/100 | 120 | 18/100 | 426 | 100/100 | 987 | 10 (quarter 7.5) | **yes** |
| 12x12 | 6 | 20 | 3 | 0/100 | 82 | 0/100 | 204 | 75/100 | 938 | 8 (quarter 5.0) |  |
| 12x12 | 6 | 30 | 3 | 2/100 | 194 | 9/100 | 627 | 100/100 | 1559 | 8 (quarter 7.5) | **yes** |

The pick: 12x12, 6 pirates, 30 turns, noise 3.
