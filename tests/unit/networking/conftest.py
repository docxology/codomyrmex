"""Explicit trust stores and opt-in credentialed SSH test configuration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from codomyrmex.networking import SSHClient


@pytest.fixture
def known_hosts_file(tmp_path: Path) -> Path:
    """An actual empty trust store, independent of the operator's home."""
    path = tmp_path / "known_hosts"
    path.write_text("")
    return path


@pytest.fixture
def live_ssh_client() -> SSHClient:
    """Require an explicit live flag and caller-selected account/trust inputs."""
    from codomyrmex.networking import SSHClient

    if os.environ.get("CODOMYRMEX_RUN_LIVE_SSH_TESTS") != "1":
        pytest.fail(
            "Credentialed SSH tests require explicit live opt-in", pytrace=False
        )

    def required(name: str) -> str:
        value = os.environ.get(name)
        if not value:
            pytest.fail(f"Live SSH requires {name}", pytrace=False)
        return value

    key = required("CODOMYRMEX_TEST_SSH_KEY")
    known_hosts = required("CODOMYRMEX_TEST_SSH_KNOWN_HOSTS")
    username = required("CODOMYRMEX_TEST_SSH_USER")
    if not Path(key).is_file() or not Path(known_hosts).is_file():
        pytest.fail(
            "Live SSH key and trust store must be explicit files", pytrace=False
        )
    return SSHClient(
        hostname=os.environ.get("CODOMYRMEX_TEST_SSH_HOST", "localhost"),
        username=username,
        port=int(os.environ.get("CODOMYRMEX_TEST_SSH_PORT", "22")),
        key_filename=key,
        known_hosts_file=known_hosts,
    )
