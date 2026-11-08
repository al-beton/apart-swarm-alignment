<!-- Implements: assets/plain-files, assets/catwalk, specs-and-docs/folder-guides -->
# Assets

All the game's art: plain PNG files any renderer can load, and the Python that draws them. `make assets` redraws everything, and a test fails if a committed image doesn't match the code. `make catwalk` writes only the GIF below.

![All the art on one page](sheet.png)

![Every pirate walking in all four directions](catwalk.gif)

## Sizes

A square is 48x48, so a 10x10 board is 480px at real size. Scale by whole numbers only, with nearest-neighbour, or the pixels blur. At half size the labels stop being readable, so a paper figure should crop the board rather than shrink it.

## Files

| Path | Size | What |
|---|---|---|
| `pirates/pirate-01.png` to `pirate-20.png` | 144x384 | One crew member, labelled with its number, in that number's colour and personality. Columns are frames, rows are `down`, `up`, `right`, `left`, `dig`, `cheer`, `read`, `write`. |
| `tiles/sand.png`, `sand-2.png`, `sand-3.png` | 48x48 | Sand. Mix the three so the ground doesn't look stamped; each has a faint dotted top and left edge, so squares can be counted. |
| `tiles/grass.png` | 48x48 | Grass, walkable like sand, there to break up the ground. |
| `tiles/dug.png` | 48x48 | A dug square: ruffled, and still walkable. |
| `tiles/water.png`, `water-2.png` | 48x48 | Water, which can't be crossed. Alternate the two to animate it. |
| `tiles/sinking-sand.png` | 48x48 | Sinking sand, for hidden terrain once it's found. |
| `treasure/mark-question.png` | 48x48 | The mark on the treasure square for the reader, from the start until it's dug up and becomes the cave. |
| `treasure/cave.png`, `cave-2.png` | 48x48 | The treasure square once it's dug up: a cave the pirates go into. Alternate the two to make the gold glint. Draw it over `tiles/dug.png`. |
| `ui/font.png` | 96x60 | Printable ASCII from space, 16 across, in 6x10 cells. |
| `ui/note.png` | 24x24 | Scroll note nine-slice, with 8px cells: parchment rolled at the top and bottom, for a pirate writing. |
| `ui/quill.png` | 12x16 | The quill, writing at the note's bottom right. |
| `ui/open-scroll.png` | 28x22 | A scroll held open beside a pirate reading, with lines but no words. |
| `ui/panel.png` | 36x36 | Side panel and log frame nine-slice, with 12px cells. |
| `ui/turn-arrow.png` | 16x12 | Floats above the pirate whose turn it is. |
| `sheet.png` | 1040x1420 | All of the above on one page. |
| `catwalk.gif` | 480x384 | Every pirate walking a loop on a sample of the walkable tiles: 32 frames, 100 ms each. A preview for people, not something to build a renderer on. |

## Walking

Loop frames 0, 1, 0, 2 of a row. `dig` and `cheer` have two frames each, in columns 0 and 1, and an empty third column.

## Drawing from Python

For a colour or label the PNGs don't have, or a note that fits its text:

```python
from assets.pirates import pirate, portrait
from assets.ui import panel, scroll_note
from assets.font import draw_text

pirate(5, "#2f6fc0", "12", "right", 1)  # personality, any RGB, label, pose, frame
portrait(5, "#2f6fc0", "12")  # 96x64 head for the side panel
scroll_note("I'll search row 1.")  # sized to its text, quill included
panel(200, 288)  # any size of at least 24x24
```

## The treasure cave

A pirate that reaches the dug-up treasure goes into the cave and leaves the board. It leaves a small copy of its hat on a stack by the door, so the square shows who is inside and in what order. Draw the square in three layers:

```python
from assets.cave import cave, going_in, hat_stack

square = cave(frame)  # over tiles/dug.png; frame 0 or 1 to glint
square.alpha_composite(
    hat_stack([("#c8403c", "1"), ("#2f6fc0", "2")])
)  # first in at the bottom
square.alpha_composite(
    going_in(3, "#3c9a4a", "3", 1)
)  # the turn it arrives: steps 0 to 3
```

On the turn a pirate arrives, draw it with `going_in` and leave its hat off the stack; from the next turn on, it's gone from the board and its hat is on top. Six hats fit with every label showing; a bigger crew squeezes up and only the top label stays readable.

A label is up to two letters or digits, and anything else raises `ValueError`. A personality is 1 to 20; to give a whole crew one look, pass the same personality with different colours.

## Turns in motion

A dig and a pirate going into the cave each have their own steps, like a walk, so the turn plays out before its still frame:

```python
from assets.cave import ENTER_STEPS, entering
from assets.dig import DIG_STEPS, dig_ground, digging

dig_ground(step, ground)  # the square's ground, its old tile turning to dug sand
digging(2, "#2f6fc0", "2", step)  # the pirate over it, sand in the air; 0 to 5
entering(
    4, "#e08a2c", "4", inside, step
)  # the whole cave square over tiles/dug.png; 0 to 8
```

`inside` is the hats already on the stack, as for `hat_stack`. The last step of each is what the turn's still frame and the next turn show, so a renderer can end on it.

## The board's frame

`board_edges(size)` from `assets.board` is the wooden frame for a size x size board: the board goes at `(EDGE_LEFT, 0)` and the frame adds `EDGE_LEFT` pixels on the left and `EDGE_BOTTOM` under it. Columns are lettered A onward from the west, rows numbered 1 onward from the south, so A1 is the bottom-left square. Boards wider than 26 raise `ValueError`.

## Several pirates on one square

Sprites fill their square, so pirates sharing one hide each other's labels. A renderer should fan them out by a few pixels, keeping each blob visible.
