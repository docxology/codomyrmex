import json
import os
import sys
from pathlib import Path

import pytest
import yaml

from manuscript_variables import compute_variables, inject_via_infrastructure


def test_compute_variables_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test compute_variables successfully generates variables."""
    project_root = tmp_path / "project_root"
    project_root.mkdir()

    # We must ensure that colony_kernel_dir exists so it won't fallback
    colony_kernel_dir = project_root / "src" / "codomyrmex" / "colony_kernel"
    colony_kernel_dir.mkdir(parents=True)

    config_path = project_root / "config.yaml"
    config_data = {
        "paper": {
            "title": "Test Paper Title",
            "version": "1.2.3",
            "date": "2023-10-01",
        },
        "experiment": {
            "colony_kernel_subsystems": 42,
            "trust_sandbox_score": 0.2,
            "agent_roles": ["TEST_ROLE_1", "TEST_ROLE_2"],
        },
        "publication": {"doi": "10.1234/test.doi"},
    }
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

    monkeypatch.setattr(
        "manuscript_variables._run_colony_kernel_coverage",
        lambda p, t: {"collected": 150, "coverage_pct": "98.5"},
    )

    # Create dummy executables for ruff and ty to avoid subprocess failures
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    ruff_sh = bin_dir / "ruff"
    ruff_bat = bin_dir / "ruff.bat"
    ruff_sh.write_text(
        f'#!/bin/sh\necho \'[{"{"}"error": "some finding"{"}"}]\'\nexit 0\n'
    )
    ruff_bat.write_text(
        f'@echo off\necho [{"{"}"error": "some finding"{"}"}]\nexit /b 0\n'
    )
    ruff_sh.chmod(0o755)

    ty_sh = bin_dir / "ty"
    ty_bat = bin_dir / "ty.bat"
    ty_sh.write_text(
        '#!/bin/sh\necho "some output\\nfile.py:10: error: bad types\\n"\nexit 0\n'
    )
    ty_bat.write_text(
        "@echo off\necho some output\necho file.py:10: error: bad types\nexit /b 0\n"
    )
    ty_sh.chmod(0o755)

    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")

    # Also we should mock counts if they take too long, but authentic files are better
    # Let's create actual dummy files so real functions return expected values, or patch them.
    monkeypatch.setattr("manuscript_variables._count_top_level_modules", lambda p: 12)
    monkeypatch.setattr(
        "manuscript_variables._count_colony_kernel_test_suites", lambda p: 5
    )
    monkeypatch.setattr(
        "manuscript_variables._count_colony_kernel_config_files", lambda p: 2
    )
    monkeypatch.setattr(
        "manuscript_variables._count_colony_kernel_mcp_tools", lambda d, c: 15
    )
    monkeypatch.setattr("manuscript_variables._count_loc", lambda p: 5000)
    monkeypatch.setattr("manuscript_variables._count_python_files", lambda p: 45)
    monkeypatch.setattr("manuscript_variables._count_colony_kernel_docs", lambda p: 10)

    variables = compute_variables(config_path, project_root)

    assert variables["CONFIG_TITLE"] == "Test Paper Title"
    assert variables["CONFIG_VERSION"] == "1.2.3"
    assert variables["CONFIG_COLONY_KERNEL_SUBSYSTEMS"] == "42"
    assert variables["CONFIG_DOI"] == "10.1234/test.doi"
    assert variables["CONFIG_TRUST_SANDBOX_SCORE"] == "0.2"
    assert variables["CONFIG_ROLE_COUNT"] == "2"

    assert variables["RESULT_TEST_COUNT"] == "150"
    assert variables["RESULT_COVERAGE_PCT"] == "98.5"
    assert variables["RESULT_RUFF_ERRORS"] == "1"
    assert variables["RESULT_TY_ERRORS"] == "1"
    assert variables["RESULT_COLONY_KERNEL_LOC"] == "5000"
    assert variables["RESULT_COLONY_KERNEL_FILES"] == "45"

    assert variables["ARTIFACT_TEST_SUITES"] == "5"
    assert variables["ARTIFACT_CONFIG_FILES"] == "2"
    assert variables["ARTIFACT_MCP_TOOLS"] == "15"


def test_compute_variables_no_tests(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test compute_variables raises error if no tests collected."""
    project_root = tmp_path / "project_root"
    project_root.mkdir()

    config_path = project_root / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump({}, f)

    monkeypatch.setattr(
        "manuscript_variables._run_colony_kernel_coverage",
        lambda p, t: {"collected": 0, "coverage_pct": "0.0"},
    )

    with pytest.raises(
        RuntimeError, match="pytest collection returned zero colony-kernel tests"
    ):
        compute_variables(config_path, project_root)


def test_compute_variables_ruff_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test compute_variables raises error if ruff check fails horribly."""
    project_root = tmp_path / "project_root"
    project_root.mkdir()

    config_path = project_root / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump({}, f)

    monkeypatch.setattr(
        "manuscript_variables._run_colony_kernel_coverage",
        lambda p, t: {"collected": 10, "coverage_pct": "100.0"},
    )

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    ruff_sh = bin_dir / "ruff"
    ruff_bat = bin_dir / "ruff.bat"
    ruff_sh.write_text('#!/bin/sh\necho "Fatal error" >&2\nexit 2\n')
    ruff_bat.write_text("@echo off\necho Fatal error 1>&2\nexit /b 2\n")
    ruff_sh.chmod(0o755)

    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")

    with pytest.raises(RuntimeError, match="ruff check failed"):
        compute_variables(config_path, project_root)


def test_inject_via_infrastructure_not_implemented(monkeypatch: pytest.MonkeyPatch):
    """Test inject_via_infrastructure raises NotImplementedError when no infra."""
    monkeypatch.setitem(sys.modules, "infrastructure.rendering", None)
    with pytest.raises(
        NotImplementedError, match="infrastructure rendering not available"
    ):
        inject_via_infrastructure(
            Path("manuscript_dir"), Path("output_dir"), {"VAR": "value"}
        )


class DummyPdfRenderer:
    def inject_manuscript_variables(self, manuscript_dir, output_dir, variables):
        self.called_with = (manuscript_dir, output_dir, variables)


def test_inject_via_infrastructure_success(monkeypatch: pytest.MonkeyPatch):
    """Test inject_via_infrastructure delegates to infrastructure module when present."""
    import types

    mock_pdf_renderer = DummyPdfRenderer()

    mock_rendering = types.ModuleType("infrastructure.rendering")
    mock_rendering.pdf_combined_renderer = mock_pdf_renderer

    mock_infrastructure = types.ModuleType("infrastructure")
    mock_infrastructure.rendering = mock_rendering

    monkeypatch.setitem(sys.modules, "infrastructure", mock_infrastructure)
    monkeypatch.setitem(sys.modules, "infrastructure.rendering", mock_rendering)

    inject_via_infrastructure(Path("m_dir"), Path("o_dir"), {"VAR": "VAL"})

    assert mock_pdf_renderer.called_with == (
        Path("m_dir"),
        Path("o_dir"),
        {"VAR": "VAL"},
    )
