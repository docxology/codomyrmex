"""Shared fixtures for the ci_cd_automation tests."""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _run_in_tmp_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run each test with its own temporary directory as the CWD.

    PipelineManager, PipelineMonitor, PipelineOptimizer and RollbackManager
    keep their data under the current directory when no ``workspace_dir`` is
    given (``.pipelines/``, ``pipeline_reports/``, ``rollback_plans/``, ...),
    and many tests construct them without one.
    """
    monkeypatch.chdir(tmp_path)
