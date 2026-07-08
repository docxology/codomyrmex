#!/usr/bin/env python3
"""Tests for apply_curated_markers."""

from pathlib import Path

import pytest

from codomyrmex.documentation.scripts.apply_curated_markers import _prepend_marker
from codomyrmex.documentation.scripts.bootstrap_agents_readmes import (
    AGENTS_CURATED_MARKER,
    README_CURATED_MARKER,
)


@pytest.mark.unit
def test_prepend_marker_prepends_once(tmp_path: Path) -> None:
    p = tmp_path / "AGENTS.md"
    p.write_text("# Body\n", encoding="utf-8")
    assert _prepend_marker(p, AGENTS_CURATED_MARKER, dry_run=False) is True
    text = p.read_text(encoding="utf-8")
    assert text.startswith(AGENTS_CURATED_MARKER)
    assert "# Body" in text
    assert _prepend_marker(p, AGENTS_CURATED_MARKER, dry_run=False) is False


@pytest.mark.unit
def test_prepend_marker_dry_run_no_write(tmp_path: Path) -> None:
    p = tmp_path / "README.md"
    p.write_text("x", encoding="utf-8")
    assert _prepend_marker(p, README_CURATED_MARKER, dry_run=True) is True
    assert p.read_text(encoding="utf-8") == "x"
