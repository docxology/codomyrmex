"""Resource-isolation fixtures for data-visualization tests."""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType

import pytest


def _close_loaded_figures() -> None:
    """Close figures only when pyplot was loaded by the test process."""
    pyplot: ModuleType | None = sys.modules.get("matplotlib.pyplot")
    close = getattr(pyplot, "close", None)
    if callable(close):
        close("all")


@pytest.fixture(autouse=True)
def isolate_matplotlib_figures() -> Iterator[None]:
    """Prevent figure-registry state from leaking between visualization tests."""
    _close_loaded_figures()
    yield
    _close_loaded_figures()
