import subprocess
import sys

import pytest

def test_check_command():
    """Tests that the check command runs successfully."""
    result = subprocess.run(
        [sys.executable, "-m", "codomyrmex.cli", "check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert ("Codomyrmex Environment Check" in result.stdout or
            "Checking Codomyrmex environment..." in result.stdout)

def test_info_command():
    """Tests that the info command runs successfully."""
    result = subprocess.run(
        [sys.executable, "-m", "codomyrmex.cli", "info"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Codomyrmex - A Modular, Extensible Coding Workspace" in result.stdout

def test_doctor_command():
    """Tests that the doctor command runs successfully."""
    result = subprocess.run(
        [sys.executable, "-m", "codomyrmex.cli", "doctor", "--all_checks"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Codomyrmex Doctor" in result.stdout