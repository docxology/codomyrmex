"""Shared fixtures for the plugin_system tests."""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _run_in_tmp_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run each test with its own temporary directory as the CWD.

    A PluginLoader constructed without ``plugin_directories`` (directly or
    through PluginManager) creates ``./plugins`` in the current directory.
    """
    monkeypatch.chdir(tmp_path)
