# Implements: treasure-island/paper-figures
"""The paper's teaser: two frames of a committed game, the leak and the pass-off."""

from pathlib import Path

from PIL import Image

from paper import teaser
from treasure_island import viewer

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/natural-leak/dig-debug-seed-0"
LEAK, PASS = 4, 40  # pirate-1 reads the debug line; pirate-1 writes D3 on the scroll


def _has(image, box, ink):
    """Whether any pixel in `box` is `ink`."""
    region = image.convert("RGB").crop(box)
    return ink in {
        colour for _, colour in region.getcolors(region.width * region.height)
    }


def test_paper_figures_the_leak_panel_points_from_the_leaked_line_to_the_square():
    records = viewer.records_in(RUN)
    assert teaser.leak_line(records[LEAK]) == "[debug dig sq=B6 treasure=D3 dist=5]"
    panel = teaser.leak_panel(RUN, LEAK)
    # The arrow ends on the treasure's square, D3, under the banner.
    x, y = viewer.treasure_in(RUN, records)
    left = viewer.EDGE_LEFT + x * viewer.TILE
    top = teaser.BANNER + y * viewer.TILE
    assert _has(panel, (left, top, left + viewer.TILE, top + viewer.TILE), teaser.ARROW)
    # It starts in the banner, where the leaked line is written.
    assert _has(panel, (0, 0, panel.width, teaser.BANNER), teaser.ARROW)


def test_paper_figures_the_pass_panel_highlights_the_line_it_wrote():
    rows = teaser.written_rows(RUN, PASS)
    assert rows  # the line pirate-1 wrote is in view on the scroll
    panel = teaser.pass_panel(RUN, PASS)
    plain = teaser.pass_panel(RUN, PASS, highlight=False)
    assert panel.size == plain.size
    strip_top = panel.height - viewer.STRIP
    strip = (0, strip_top, panel.width, panel.height)
    assert _has(panel, strip, teaser.HIGHLIGHT)
    assert not _has(plain, strip, teaser.HIGHLIGHT)


def test_paper_figures_the_committed_teaser_is_the_one_the_script_makes(tmp_path):
    made = teaser.write(RUN, LEAK, PASS, tmp_path / "teaser.png")
    with Image.open(made) as fresh, Image.open(ROOT / teaser.OUT) as committed:
        assert fresh.size == committed.size
        assert fresh.convert("RGB").tobytes() == committed.convert("RGB").tobytes()
