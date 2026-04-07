"""Unit tests for scripts/documentation/enforce_quality_gate.py (fixture-based, no full-repo scan)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]


@pytest.fixture(scope="module")
def enforce_module():
    script = REPO_ROOT / "scripts" / "documentation" / "enforce_quality_gate.py"
    assert script.is_file(), f"missing {script}"
    spec = importlib.util.spec_from_file_location("enforce_quality_gate", script)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _write_gate_fixtures(
    out: Path,
    *,
    link_status: str = "ok",
    quality_scores: list[tuple[int, int]] | None = None,
    agents_valid: list[bool] | None = None,
) -> None:
    """Write minimal JSON inputs for enforce_quality_gate.

    quality_scores: list of (score, placeholder_count) per synthetic file row.
    agents_valid: list of valid flags per synthetic AGENTS row.
    """
    if quality_scores is None:
        quality_scores = [(100, 0)]
    if agents_valid is None:
        agents_valid = [True]

    out.mkdir(parents=True, exist_ok=True)
    (out / "link_validation.json").write_text(
        json.dumps([{"file": "x.md", "link": "y.md", "line": 1, "status": link_status, "message": ""}]),
        encoding="utf-8",
    )
    quality_rows = [
        {
            "file": f"doc{i}.md",
            "score": sc,
            "issues": [],
            "metrics": {"placeholder_count": ph},
        }
        for i, (sc, ph) in enumerate(quality_scores)
    ]
    (out / "content_quality.json").write_text(
        json.dumps(quality_rows),
        encoding="utf-8",
    )
    agents_rows = [
        {
            "file": f"AGENTS{i}.md",
            "valid": v,
            "missing_sections": [] if v else ["Purpose"],
            "warnings": [],
            "score": 100 if v else 60,
        }
        for i, v in enumerate(agents_valid)
    ]
    (out / "agents_validation.json").write_text(
        json.dumps(agents_rows),
        encoding="utf-8",
    )


@pytest.mark.unit
def test_enforce_quality_gate_passes_with_clean_fixtures(
    enforce_module, tmp_path: Path
) -> None:
    _write_gate_fixtures(tmp_path)
    rc = enforce_module.enforce_quality_gate(
        REPO_ROOT,
        tmp_path,
        min_quality_score=70,
        max_broken_links=10,
        max_placeholders=100,
        min_agents_valid_rate=80,
        allow_warnings=True,
    )
    assert rc == 0


@pytest.mark.unit
def test_enforce_quality_gate_fails_on_broken_links(
    enforce_module, tmp_path: Path
) -> None:
    _write_gate_fixtures(tmp_path, link_status="broken")
    # One broken link must exceed cap (CI uses 10; use 0 here to assert failure wiring).
    rc = enforce_module.enforce_quality_gate(
        REPO_ROOT,
        tmp_path,
        min_quality_score=70,
        max_broken_links=0,
        max_placeholders=100,
        min_agents_valid_rate=80,
        allow_warnings=True,
    )
    assert rc == 1


@pytest.mark.unit
def test_enforce_quality_gate_fails_on_placeholder_cap(
    enforce_module, tmp_path: Path
) -> None:
    _write_gate_fixtures(tmp_path, quality_scores=[(100, 50), (100, 51)])
    rc = enforce_module.enforce_quality_gate(
        REPO_ROOT,
        tmp_path,
        min_quality_score=70,
        max_broken_links=10,
        max_placeholders=100,
        min_agents_valid_rate=80,
        allow_warnings=True,
    )
    assert rc == 1


@pytest.mark.unit
def test_enforce_quality_gate_fails_on_low_avg_score(
    enforce_module, tmp_path: Path
) -> None:
    # Average must be strictly below min (100 + 39) / 2 = 69.5 < 70
    _write_gate_fixtures(tmp_path, quality_scores=[(100, 0), (39, 0)])
    rc = enforce_module.enforce_quality_gate(
        REPO_ROOT,
        tmp_path,
        min_quality_score=70,
        max_broken_links=10,
        max_placeholders=100,
        min_agents_valid_rate=80,
        allow_warnings=True,
    )
    assert rc == 1


@pytest.mark.unit
def test_enforce_quality_gate_fails_on_agents_valid_rate(
    enforce_module, tmp_path: Path
) -> None:
    _write_gate_fixtures(tmp_path, agents_valid=[True, False])
    rc = enforce_module.enforce_quality_gate(
        REPO_ROOT,
        tmp_path,
        min_quality_score=70,
        max_broken_links=10,
        max_placeholders=100,
        min_agents_valid_rate=80,
        allow_warnings=True,
    )
    assert rc == 1
