"""Unit tests for unified hermes-agent path discovery."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from codomyrmex.agents.hermes import hermes_paths


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
