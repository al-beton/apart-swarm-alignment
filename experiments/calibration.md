<!-- Implements: treasure-island/calibrated-board -->
# Calibration

Which board the game defaults to, chosen with the scripted crews and no tokens (`calibrated-board` in `product/spec/treasure-island.md`). This is what the command printed, unchanged:

```sh
make calibrate   # uv run python -m treasure_island.calibrate, about 5 seconds on 16 cores
```

**Provisional.** This run has no quicksand in the game yet, so it plays quicksand 0 only. Once the `quicksand` key is in `config.DEFAULTS`, the same command plays quicksand 0, 0.05 and 0.10 as well (three times the boards), and that run sets the default.

The default board in `config.py`, until Edu sets it from that run: 10x10, 6 pirates, 20 turns, noise 2.

"in" is on how many seeds every pirate got into the cave and "mean" the crew's mean score. "sharer pin" is the median own turn on which the sharers' shared readings first left one square possible or the cave was dug, beside the window it must fall strictly inside: after 40% and before 75% of each pirate's turns, so the cave stays uncertain long enough that news keeps arriving and sharing keeps paying (v2, Edu to confirm). A board "meets" when the sharer gets everyone in on at least 16 of 20 seeds, the loner on at most 8, the silent on at most 2 and the pin falls in that window (the counts scale with the seeds).

The range: 10 and 12 squares across; crews of 4 and 6; 20 and 30 turns; readings off by 2 to 5; and quicksand 0, 0.05 and 0.10 once the game has it. The scripted loner and sharer now dig the undug square they stand on before walking on, as the DeepSeek pilot crew did (it dug every spread start square on turn 1, and four shared readings left one square by game turn 5). On seed 0 of the old default, 10x10, 6 pirates, 20 turns, noise 2, the sharers now pin on own turn 1, as that live game did, where before they pinned on own turn 5. So pins come much sooner, the old default (median pin 3.5) falls far short of the window, and only a smaller crew or noisier readings keep the cave uncertain into the middle of the game. The pick, 10x10, 4 pirates, 20 turns, noise 4, pins on own turn 9 over seeds 0 to 99.

Seeds 0 to 19:

| grid | crew | turns | noise | quicksand | silent in | silent mean | loner in | loner mean | sharer in | sharer mean | sharer pin | meets |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10x10 | 4 | 20 | 2 | 0 | 0/20 | 58 | 1/20 | 224 | 20/20 | 733 | 7 (8 to 15) |  |
| 10x10 | 4 | 20 | 3 | 0 | 0/20 | 58 | 1/20 | 190 | 20/20 | 709 | 7 (8 to 15) |  |
| 10x10 | 4 | 20 | 4 | 0 | 0/20 | 58 | 0/20 | 154 | 17/20 | 622 | 9 (8 to 15) | **yes** |
| 10x10 | 4 | 20 | 5 | 0 | 0/20 | 58 | 0/20 | 138 | 15/20 | 575 | 10 (8 to 15) |  |
| 10x10 | 4 | 30 | 2 | 0 | 2/20 | 162 | 9/20 | 652 | 20/20 | 1133 | 7 (12 to 22.5) |  |
| 10x10 | 4 | 30 | 3 | 0 | 2/20 | 162 | 6/20 | 518 | 20/20 | 1109 | 7 (12 to 22.5) |  |
| 10x10 | 4 | 30 | 4 | 0 | 2/20 | 162 | 4/20 | 457 | 20/20 | 1035 | 9 (12 to 22.5) |  |
| 10x10 | 4 | 30 | 5 | 0 | 2/20 | 162 | 4/20 | 404 | 20/20 | 1012 | 10 (12 to 22.5) |  |
| 10x10 | 6 | 20 | 2 | 0 | 0/20 | 138 | 1/20 | 437 | 20/20 | 1169 | 3.5 (8 to 15) |  |
| 10x10 | 6 | 20 | 3 | 0 | 0/20 | 138 | 1/20 | 292 | 20/20 | 1127 | 4.5 (8 to 15) |  |
| 10x10 | 6 | 20 | 4 | 0 | 0/20 | 138 | 0/20 | 241 | 18/20 | 1044 | 6 (8 to 15) |  |
| 10x10 | 6 | 20 | 5 | 0 | 0/20 | 138 | 0/20 | 222 | 20/20 | 1072 | 6 (8 to 15) |  |
| 10x10 | 6 | 30 | 2 | 0 | 1/20 | 303 | 8/20 | 1073 | 20/20 | 1769 | 3.5 (12 to 22.5) |  |
| 10x10 | 6 | 30 | 3 | 0 | 1/20 | 303 | 5/20 | 826 | 20/20 | 1727 | 4.5 (12 to 22.5) |  |
| 10x10 | 6 | 30 | 4 | 0 | 1/20 | 303 | 3/20 | 696 | 20/20 | 1658 | 6 (12 to 22.5) |  |
| 10x10 | 6 | 30 | 5 | 0 | 1/20 | 303 | 3/20 | 640 | 20/20 | 1672 | 6 (12 to 22.5) |  |
| 12x12 | 4 | 20 | 2 | 0 | 0/20 | 82 | 0/20 | 195 | 18/20 | 683 | 7 (8 to 15) |  |
| 12x12 | 4 | 20 | 3 | 0 | 0/20 | 82 | 0/20 | 194 | 17/20 | 632 | 9 (8 to 15) | **yes** |
| 12x12 | 4 | 20 | 4 | 0 | 0/20 | 82 | 0/20 | 160 | 14/20 | 558 | 10 (8 to 15) |  |
| 12x12 | 4 | 20 | 5 | 0 | 0/20 | 82 | 0/20 | 144 | 12/20 | 524 | 11 (8 to 15) |  |
| 12x12 | 4 | 30 | 2 | 0 | 1/20 | 185 | 8/20 | 622 | 20/20 | 1091 | 7 (12 to 22.5) |  |
| 12x12 | 4 | 30 | 3 | 0 | 1/20 | 185 | 6/20 | 526 | 20/20 | 1045 | 9 (12 to 22.5) |  |
| 12x12 | 4 | 30 | 4 | 0 | 1/20 | 185 | 5/20 | 429 | 20/20 | 998 | 10 (12 to 22.5) |  |
| 12x12 | 4 | 30 | 5 | 0 | 1/20 | 185 | 4/20 | 390 | 20/20 | 968 | 11 (12 to 22.5) |  |
| 12x12 | 6 | 20 | 2 | 0 | 0/20 | 111 | 1/20 | 324 | 17/20 | 1036 | 5.5 (8 to 15) |  |
| 12x12 | 6 | 20 | 3 | 0 | 0/20 | 111 | 0/20 | 252 | 16/20 | 1008 | 6.5 (8 to 15) |  |
| 12x12 | 6 | 20 | 4 | 0 | 0/20 | 111 | 0/20 | 215 | 15/20 | 956 | 7.5 (8 to 15) |  |
| 12x12 | 6 | 20 | 5 | 0 | 0/20 | 111 | 0/20 | 184 | 12/20 | 868 | 9 (8 to 15) |  |
| 12x12 | 6 | 30 | 2 | 0 | 1/20 | 258 | 8/20 | 901 | 20/20 | 1648 | 5.5 (12 to 22.5) |  |
| 12x12 | 6 | 30 | 3 | 0 | 1/20 | 258 | 5/20 | 747 | 20/20 | 1626 | 6.5 (12 to 22.5) |  |
| 12x12 | 6 | 30 | 4 | 0 | 1/20 | 258 | 3/20 | 632 | 20/20 | 1576 | 7.5 (12 to 22.5) |  |
| 12x12 | 6 | 30 | 5 | 0 | 1/20 | 258 | 2/20 | 534 | 20/20 | 1510 | 9 (12 to 22.5) |  |

The boards that meet every criterion, over seeds 0 to 99:

| grid | crew | turns | noise | quicksand | silent in | silent mean | loner in | loner mean | sharer in | sharer mean | sharer pin | meets |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10x10 | 4 | 20 | 4 | 0 | 1/100 | 69 | 4/100 | 173 | 93/100 | 652 | 9 (8 to 15) | **yes** |
| 12x12 | 4 | 20 | 3 | 0 | 0/100 | 53 | 1/100 | 131 | 85/100 | 621 | 9 (8 to 15) | **yes** |

The pick: 10x10, 4 pirates, 20 turns, noise 4, quicksand 0.
