"""Tests for manuscript figure generators."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module", autouse=True)
def _ensure_generated_manuscript_snapshot() -> None:
    """Prepare the authoritative variable snapshot when running from a fresh clone."""
    snapshot = (
        Path(__file__).resolve().parents[3] / "output/data/manuscript_variables.json"
    )
    if not snapshot.exists():
        root = snapshot.parents[2]
        subprocess.run(
            [sys.executable, str(root / "scripts/z_generate_manuscript_variables.py")],
            cwd=root,
            check=True,
        )


def test_figure_registry_lists_all_referenced_generators() -> None:
    import yaml

    from codomyrmex.manuscript.figures import FIGURES

    configured = yaml.safe_load(
        (Path(__file__).resolve().parents[3] / "docs/manuscript/config.yaml").read_text(
            encoding="utf-8"
        )
    )["figures"]
    assert len(FIGURES) == len(configured)
    names = {name for name, _ in FIGURES}
    assert "cover.png" in names
    assert "colony_pressure_loop.png" in names
    assert "research_roadmap.png" in names
    assert "replay_contract.png" in names
    assert "attestation_event_chain.png" in names
    assert "safety_utility_frontier.png" in names
    assert "calibration_reliability.png" in names
    assert "persistence_recovery.png" in names
    assert "formalism_coverage.png" in names
    assert "research_status_matrix.png" in names
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


def test_figure_generation_rejects_missing_snapshot(
    tmp_path: Path, monkeypatch
) -> None:
    from codomyrmex.manuscript import figures
    from codomyrmex.manuscript.figures import _common

    monkeypatch.setattr(_common, "FIGDIR", tmp_path)
    saved_variables = dict(_common._VARIABLES)
    saved_config = dict(_common._CONFIG)
    _common._VARIABLES.clear()
    try:
        with pytest.raises(_common.FigureConfigurationError, match="variables"):
            figures.fig_pheromone_decay()
    finally:
        _common._VARIABLES.update(saved_variables)
        _common._CONFIG.update(saved_config)


def test_figure_generation_rejects_stale_source_snapshot(
    tmp_path: Path, monkeypatch
) -> None:
    from codomyrmex.manuscript import figures
    from codomyrmex.manuscript.figures import _common

    monkeypatch.setattr(_common, "FIGDIR", tmp_path)
    saved_variables = dict(_common._VARIABLES)
    _common._VARIABLES["REPRO_KERNEL_SOURCE_HASH"] = "stale-source"
    try:
        with pytest.raises(_common.FigureConfigurationError, match="stale"):
            figures.fig_pheromone_decay()
    finally:
        _common._VARIABLES.clear()
        _common._VARIABLES.update(saved_variables)


def test_figure_generation_rejects_snapshot_without_source_provenance(
    tmp_path: Path, monkeypatch
) -> None:
    from codomyrmex.manuscript import figures
    from codomyrmex.manuscript.figures import _common

    monkeypatch.setattr(_common, "FIGDIR", tmp_path)
    saved_variables = dict(_common._VARIABLES)
    _common._VARIABLES.pop("REPRO_KERNEL_SOURCE_HASH", None)
    try:
        with pytest.raises(_common.FigureConfigurationError, match="missing"):
            figures.fig_pheromone_decay()
    finally:
        _common._VARIABLES.clear()
        _common._VARIABLES.update(saved_variables)
