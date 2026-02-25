"""Tests for orchestrator.core module."""

from pathlib import Path

import pytest

from codomyrmex.orchestrator.core import main


@pytest.fixture
def test_env(tmp_path):
    """Set up a real directory structure with scripts for core.main()."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    
    subdir1 = scripts_dir / "subdir1"
    subdir1.mkdir()
    
    # Create a passing script
    (subdir1 / "pass.py").write_text("print('pass')\n")
    
    # Create a failing script
    (subdir1 / "fail.py").write_text("import sys\nsys.exit(1)\n")
    
    # Create a config to skip one script
    (scripts_dir / "config.yaml").write_text(
        "scripts:\n  subdir1/fail.py:\n    skip: true\n    skip_reason: 'Testing skip'\n"
    )
    
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    return scripts_dir, logs_dir


def test_main_help(capsys):
    """Test --help argument."""
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "Run and log all scripts" in captured.out


def test_main_dry_run(test_env, capsys):
    """Test --dry-run argument."""
    scripts_dir, _ = test_env
    exit_code = main(["--dry-run", "--scripts-dir", str(scripts_dir)])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert "DRY RUN MODE" in captured.out
    assert "pass.py" in captured.out
    assert "WOULD SKIP: fail.py" in captured.out


def test_main_generate_docs(test_env, tmp_path):
    """Test --generate-docs argument."""
    scripts_dir, _ = test_env
    docs_out = tmp_path / "docs.md"
    exit_code = main([
        "--generate-docs", str(docs_out), 
        "--scripts-dir", str(scripts_dir)
    ])
    assert exit_code == 0
    assert docs_out.exists()


def test_main_success_run(test_env, capsys):
    """Test a successful full run (fail.py is skipped via config)."""
    scripts_dir, logs_dir = test_env
    exit_code = main([
        "--scripts-dir", str(scripts_dir),
        "--output-dir", str(logs_dir),
        "--verbose"
    ])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert "SCRIPT ORCHESTRATOR" in captured.out
    assert "Total Scripts: 2" in captured.out
    assert "Passed:  1" in captured.out
    assert "Skipped by config: 1" in captured.out or "WOULD SKIP" not in captured.out


def test_main_no_scripts_found(tmp_path, capsys):
    """Test behavior when no scripts are discovered."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    exit_code = main(["--scripts-dir", str(empty_dir)])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert "No scripts found matching criteria" in captured.out


def test_main_failure_run(test_env, capsys):
    """Test behavior when a script fails."""
    scripts_dir, logs_dir = test_env
    # Remove config so fail.py is not skipped and runs, causing a failure
    (scripts_dir / "config.yaml").unlink()
    
    exit_code = main([
        "--scripts-dir", str(scripts_dir),
        "--output-dir", str(logs_dir)
    ])
    assert exit_code == 1
    
    captured = capsys.readouterr()
    assert "Passed:  1" in captured.out
    assert "Failed:  1" in captured.out

