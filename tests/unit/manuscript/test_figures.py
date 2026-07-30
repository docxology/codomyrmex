"""Tests for manuscript figure generators."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module", autouse=True)
def _ensure_generated_manuscript_snapshot() -> None:
    """Prepare and load the authoritative snapshot when running from a fresh clone."""
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
    # Another test module can import the figure package during collection, before
    # this fixture creates the ignored snapshot. Refresh that cached empty map.
    from codomyrmex.manuscript.figures import _common

    _common._VARIABLES.clear()
    _common._VARIABLES.update(_common._load_json(snapshot))


def test_figure_registry_lists_all_referenced_generators() -> None:
    import json

    import yaml

    from codomyrmex.manuscript.figures import FIGURES

    root = Path(__file__).resolve().parents[3]
    configured = yaml.safe_load(
        (root / "docs/manuscript/config.yaml").read_text(encoding="utf-8")
    )["figures"]
    variables = json.loads(
        (root / "output/data/manuscript_variables.json").read_text(encoding="utf-8")
    )
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
    assert int(variables["ARTIFACT_FIGURE_COUNT"]) == len(configured)
    accessibility_rows = variables["RESULT_FIGURE_ACCESSIBILITY_ROWS"]
    assert "<br" not in accessibility_rows
    assert accessibility_rows.count("**Short alternative:**") == len(configured)
    assert accessibility_rows.count("**Extended description:**") == len(configured)


def test_configured_figures_have_distinct_text_alternatives() -> None:
    import yaml

    configured = yaml.safe_load(
        (Path(__file__).resolve().parents[3] / "docs/manuscript/config.yaml").read_text(
            encoding="utf-8"
        )
    )["figures"]
    for name, spec in configured.items():
        caption = " ".join(spec["caption"].split())
        alt_text = " ".join(spec["alt_text"].split())
        long_description = " ".join(spec["long_description"].split())
        assert alt_text, name
        assert long_description, name
        assert alt_text != caption, name
        assert len(long_description.split()) > len(alt_text.split()), name


def test_shared_palette_and_in_fill_text_meet_contrast_floor() -> None:
    from codomyrmex.manuscript.figures._common import (
        _OI,
        _contrast_ratio,
        _text_color_on,
    )

    background = "#F7F9FC"
    for role, color in _OI.items():
        assert _contrast_ratio(color, background) >= 4.5, role
        assert _contrast_ratio(_text_color_on(color), color) >= 4.5, role


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
