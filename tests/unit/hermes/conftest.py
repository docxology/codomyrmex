"""Isolate Hermes operator data while preserving discovery of actual upstream code."""

from pathlib import Path

import pytest

from codomyrmex.agents.hermes.hermes_paths import discover_hermes_agent_repo

# Discovery checks directories only; it never reads the operator's config.
_UPSTREAM_AGENT_REPO = discover_hermes_agent_repo()


@pytest.fixture(autouse=True)
def hermes_test_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Use recognized Hermes configuration isolation without changing HOME."""
    home = tmp_path / "hermes-home"
    home.mkdir()
    (home / "config.yaml").write_text(
        "backend: none\n"
        "telegram:\n  require_mention: true\n"
        "approvals:\n  mode: manual\n"
        "security:\n  allow_private_urls: false\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("HERMES_HOME", str(home))
    if _UPSTREAM_AGENT_REPO is not None:
        monkeypatch.setenv("HERMES_AGENT_REPO", str(_UPSTREAM_AGENT_REPO))
    return home
