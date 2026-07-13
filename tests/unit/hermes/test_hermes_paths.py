"""Unit tests for unified hermes-agent path discovery."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from codomyrmex.agents.hermes import hermes_paths

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_discover_prefers_hermes_agent_repo(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = tmp_path / "my-hermes"
    fake.mkdir()
    monkeypatch.setenv(hermes_paths.ENV_HERMES_AGENT_REPO, str(fake))
    monkeypatch.delenv("HOME", raising=False)
    assert hermes_paths.discover_hermes_agent_repo() == fake.resolve()


def test_discover_ignores_env_when_not_a_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    not_dir = tmp_path / "file.txt"
    not_dir.write_text("x")
    monkeypatch.setenv(hermes_paths.ENV_HERMES_AGENT_REPO, str(not_dir))
    got = hermes_paths.discover_hermes_agent_repo()
    assert got is None or got.is_dir()
    assert got != not_dir.resolve()


def test_discover_hermes_cli_path_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    exe = tmp_path / "hermes"
    exe.write_text("#!/bin/sh\necho ok\n")
    exe.chmod(0o755)
    monkeypatch.setenv(hermes_paths.ENV_HERMES_CLI_PATH, str(exe))
    assert hermes_paths.discover_hermes_cli_binary() == str(exe.resolve())


def test_session_db_env_prevents_home_database_writes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Default client persistence follows the injected DB and leaves HOME untouched."""
    fake_home = tmp_path / "home"
    injected_db = tmp_path / "worker" / "hermes-sessions.db"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv(hermes_paths.ENV_HERMES_SESSION_DB, str(injected_db))

    from codomyrmex.agents.hermes.hermes_client import HermesClient

    client = HermesClient(config={"hermes_backend": "none"})
    assert client._session_db_path == str(injected_db)
    client.set_system_prompt("isolated-session", "test")

    assert injected_db.exists()
    assert not (fake_home / ".codomyrmex" / "hermes_sessions.db").exists()


def test_explicit_session_db_overrides_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    explicit = tmp_path / "explicit.db"
    monkeypatch.setenv(hermes_paths.ENV_HERMES_SESSION_DB, str(tmp_path / "env.db"))
    assert hermes_paths.resolve_hermes_session_db(explicit) == explicit
