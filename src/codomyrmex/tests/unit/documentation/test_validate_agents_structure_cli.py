"""CLI integration for scripts/documentation/validate_agents_structure.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]


@pytest.mark.unit
def test_validate_agents_structure_fail_on_invalid_passes() -> None:
    """Repository AGENTS.md set must satisfy validator with --fail-on-invalid."""
    script = REPO_ROOT / "scripts" / "documentation" / "validate_agents_structure.py"
    assert script.is_file(), f"missing {script}"
    proc = subprocess.run(
        [sys.executable, str(script), "--fail-on-invalid"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert proc.returncode == 0, (
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    assert "All AGENTS.md files are valid" in proc.stdout
