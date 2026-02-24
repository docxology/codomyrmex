"""Integration tests for top-level scripts.

Each test verifies that a script either responds to ``--help`` or
runs successfully (for scripts that have no help flag and just execute).
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"


def _run_script(*args: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a script relative to SCRIPTS_DIR."""
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ── Help-flag tests ──────────────────────────────────────────────
# Each script should exit 0 and print its description when called
# with --help.

_HELP_SCRIPTS = {
    "audit_documentation": (
        "documentation/audit_documentation.py",
        "Audits repository documentation coverage",
    ),
    "fix_missing_docstrings": (
        "docs/fix_missing_docstrings.py",
        "Fix missing docstrings",
    ),
    "run_all_scripts": (
        "run_all_scripts.py",
        "Run and log all scripts",
    ),
    "launch_dashboard": (
        "website/launch_dashboard.py",
        "Launch Codomyrmex Dashboard",
    ),
    "remediate_documentation": (
        "docs/remediate_documentation.py",
        "Remediate documentation gaps",
    ),
    "update_pai_docs": (
        "pai/update_pai_docs.py",
        "Batch update stub PAI.md files",
    ),
    "update_root_docs": (
        "docs/update_root_docs.py",
        "Update root documentation files",
    ),
    "update_spec_md": (
        "docs/update_spec_md.py",
        "Update SPEC.md with missing modules",
    ),
}


@pytest.mark.parametrize(
    "script_path, expected_text",
    [
        pytest.param(v[0], v[1], id=k)
        for k, v in _HELP_SCRIPTS.items()
    ],
)
def test_script_help(script_path: str, expected_text: str) -> None:
    """Verify script responds to --help with expected description."""
    full_path = SCRIPTS_DIR / script_path
    if not full_path.exists():
        pytest.skip(f"Script not found: {full_path}")

    result = _run_script(str(full_path), "--help")
    assert result.returncode == 0, f"Script exited {result.returncode}: {result.stderr}"
    assert expected_text in result.stdout, (
        f"Expected '{expected_text}' in stdout, got:\n{result.stdout[:500]}"
    )


# ── Execution tests ──────────────────────────────────────────────

def test_demo_defense_runs() -> None:
    """Verify demo_defense.py runs to completion."""
    script = SCRIPTS_DIR / "demos" / "demo_defense.py"
    if not script.exists():
        pytest.skip(f"Script not found: {script}")

    result = _run_script(str(script), timeout=10)
    assert result.returncode == 0
    assert "Defense Demo Complete" in result.stdout


def test_verify_phase1_runs() -> None:
    """Verify verify_phase1.py runs to completion."""
    script = SCRIPTS_DIR / "verification" / "verify_phase1.py"
    if not script.exists():
        pytest.skip(f"Script not found: {script}")

    result = _run_script(str(script), timeout=10)
    assert result.returncode == 0
    assert "Phase 1 Verification Complete" in result.stdout
