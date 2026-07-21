"""Tests for manuscript figure generators."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_figure_registry_lists_nine_referenced_generators() -> None:
    from codomyrmex.manuscript.figures import FIGURES

    assert len(FIGURES) == 9
    names = {name for name, _ in FIGURES}
    assert "cover.png" in names
    assert "colony_pressure_loop.png" in names
    assert "formula_comparison.png" not in names


def test_all_configured_figure_generators_write_pngs(
    tmp_path: Path, monkeypatch
) -> None:
    """Exercise every configured generator against the current variable snapshot."""
    from codomyrmex.manuscript import figures
    from codomyrmex.manuscript.figures import _common

    monkeypatch.setattr(_common, "FIGDIR", tmp_path)

    for filename, generator in figures.FIGURES:
        generator()
        output = tmp_path / filename
        assert output.exists(), filename
        assert output.stat().st_size > 500, filename


def test_pheromone_decay_writes_png(tmp_path: Path, monkeypatch) -> None:
    from codomyrmex.manuscript import figures
    from codomyrmex.manuscript.figures import _common

    monkeypatch.setattr(_common, "FIGDIR", tmp_path)
    _common._VARIABLES.clear()
    _common._CONFIG.clear()

    figures.fig_pheromone_decay()

    output = tmp_path / "pheromone_decay.png"
    assert output.exists()
    assert output.stat().st_size > 500
