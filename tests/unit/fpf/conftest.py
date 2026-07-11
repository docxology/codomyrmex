"""FPF tests import `codomyrmex.fpf`, which pulls `networkx` via the package `__init__`."""

import pytest

pytest.importorskip(
    "networkx",
    reason="fpf analyzer stack requires networkx (uv sync --extra scientific)",
)
