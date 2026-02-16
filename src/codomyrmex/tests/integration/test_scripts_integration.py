
import pytest
import sys
import subprocess
from pathlib import Path
from unittest.mock import patch

# Verify we can import the scripts
# Since scripts are not a package, we might need to assume details about their location
ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"

sys.path.append(str(SCRIPTS_DIR))

# Import scripts dynamically or just run them as subprocesses
# Running as subprocesses is a better "true" integration test for scripts

def test_audit_documentation_help():
    """Verify audit_documentation.py help command."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "audit_documentation.py"), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Audit documentation completeness" in result.stdout

def test_fix_missing_docstrings_help():
    """Verify fix_missing_docstrings.py help command."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "fix_missing_docstrings.py"), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Fix missing docstrings" in result.stdout

def test_run_all_scripts_help():
    """Verify run_all_scripts.py help command."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "run_all_scripts.py"), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Run and log all scripts" in result.stdout

def test_launch_dashboard_help():
    """Verify launch_dashboard.py help command."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "launch_dashboard.py"), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Launch Codomyrmex Dashboard" in result.stdout

def test_demo_defense_import():
    """Verify demo_defense.py can be imported (syntax check)."""
    # Just running it might trigger interactive mode or long outputs
    # Let's try to run it and capture output, hoping it exits cleanly or we can dry-run
    # demo_defense.py runs main() on execution.
    # We can rely on it running quickly in testing.
    # It has no arguments, so it just runs.
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "demo_defense.py")],
        capture_output=True,
        text=True,
        timeout=10 # Should be very fast
    )
    assert result.returncode == 0
    assert "Defense Demo Complete" in result.stdout

def test_verify_phase1_execution():
    """Verify verify_phase1.py runs successfully."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "verify_phase1.py")],
        capture_output=True,
        text=True,
         timeout=10
    )
    assert result.returncode == 0
    assert "Phase 1 Verification Complete" in result.stdout


def test_finalize_root_docs_help():
    """Test that scripts/finalize_root_docs.py runs and shows help."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "finalize_root_docs.py"), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Finalize root documentation" in result.stdout

def test_remediate_documentation_help():
    """Test that scripts/remediate_documentation.py runs and shows help."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "remediate_documentation.py"), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Remediate documentation gaps" in result.stdout

def test_restore_descriptions_help():
    """Test that scripts/restore_descriptions.py runs and shows help."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "restore_descriptions.py"), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Restore module descriptions" in result.stdout

def test_update_pai_docs_help():
    """Test that scripts/update_pai_docs.py runs and shows help."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "update_pai_docs.py"), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Batch update stub PAI.md files" in result.stdout

def test_update_root_docs_help():
    """Test that scripts/update_root_docs.py runs and shows help."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "update_root_docs.py"), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Update root documentation files" in result.stdout

def test_update_spec_md_help():
    """Test that scripts/update_spec_md.py runs and shows help."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "update_spec_md.py"), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Update SPEC.md with missing modules" in result.stdout

