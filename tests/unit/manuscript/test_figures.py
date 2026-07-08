"""Tests for manuscript figure generators."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_figure_registry_lists_ten_generators() -> None:
    from codomyrmex.manuscript.figures import FIGURES

    assert len(FIGURES) == 10
    names = {name for name, _ in FIGURES}
    assert "cover.png" in names
    assert "colony_pressure_loop.png" in names


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
