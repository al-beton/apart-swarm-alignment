# Implements: agents/adaption-cost
"""The measured Adaption rates, re-derived from the replies that measured them.

Adaption publishes a rate only for deepseek-v4-flash, but each reply's usage
carries the `cost` it charged. On 2026-11-09 each hosted model got two replies:
a long input ("pirate " * 3000, then "Say ok.") with a short cap, and a short
input ("Write a 150-word story about a pirate.") with a long cap. Below are each
reply's input tokens, output tokens and reported cost, as Adaption returned them;
solving the pair gives the two rates in credits per million tokens.
"""

import pytest

from treasure_island.adaption_backend import RATES

# model -> ((input tokens, output tokens, cost), (input tokens, output tokens, cost))
MEASURED = {
    "deepseek-v4-flash": ((3088, 42, 0.00014283016), (93, 257, 3.839616e-05)),
    "glm-5.2": ((3017, 61, 0.0044922), (22, 207, 0.0009416)),
    "glm-53-flash": ((3017, 64, 0.00048455), (22, 600, 0.0003033)),
    "qwen3.5-397b": ((3015, 64, 0.00188225), (22, 600, 0.0021121)),
    "qwen3.8-27b": ((3057, 54, 0.000186723), (64, 600, 0.000752496)),
    "gemma-4-31b-it": ((3019, 2, 0.00027239), (26, 179, 6.32e-05)),
    "gemma-4-26b-a4b-it": ((3019, 3, 0.0002317185), (26, 195, 5.1714e-05)),
}


def solved(first, second):
    """The (input, output) rates per million tokens that price both replies."""
    (i1, o1, c1), (i2, o2, c2) = first, second
    det = i1 * o2 - i2 * o1
    return (
        (c1 * o2 - c2 * o1) / det * 1_000_000,
        (i1 * c2 - i2 * c1) / det * 1_000_000,
    )


@pytest.mark.parametrize("model", sorted(MEASURED))
def test_adaption_cost_unpublished_rates_are_measured_from_reported_cost(model):
    per_input, per_output = solved(*MEASURED[model])
    assert RATES[model] == (
        pytest.approx(per_input, rel=0.01),
        pytest.approx(per_output, rel=0.01),
    )
