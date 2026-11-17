"""Regression tests for the root pyplot figure-isolation fixture."""

from __future__ import annotations

import subprocess
import sys
import textwrap

import pytest
from tests.support.figures import close_loaded_figures
from tests.support.repo_paths import REPO_ROOT

plt = pytest.importorskip("matplotlib.pyplot")

# One more than matplotlib's figure.max_open_warning default.
_LEAKED_FIGURES = 21


@pytest.mark.unit
def test_close_loaded_figures_closes_and_counts() -> None:
    for _ in range(3):
        plt.figure()
    assert close_loaded_figures() == 3
    assert plt.get_fignums() == []
    assert close_loaded_figures() == 0


@pytest.mark.unit
def test_close_loaded_figures_does_not_import_pyplot() -> None:
    probe = textwrap.dedent(
        """
        import sys

        from tests.support.figures import close_loaded_figures

        assert close_loaded_figures() == 0
        assert "matplotlib.pyplot" not in sys.modules
        print("ok")
        """
    )
    result = subprocess.run(
        [sys.executable, "-W", "error", "-c", probe],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        stdin=subprocess.DEVNULL,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"


@pytest.mark.unit
class TestLeakedFiguresDoNotReachLaterTests:
    """A leaking test must not make a later test on the same worker fail.

    Under ``filterwarnings = error``, the 21st open figure raises matplotlib's
    "More than 20 figures" RuntimeWarning from ``plt.figure()``.
    """

    def test_leaks_figures_without_closing(self) -> None:
        for _ in range(_LEAKED_FIGURES - 1):
            plt.figure()
        assert len(plt.get_fignums()) == _LEAKED_FIGURES - 1

    def test_starts_with_an_empty_figure_registry(self) -> None:
        assert plt.get_fignums() == []
        plt.close(plt.figure())
