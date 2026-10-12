"""Real temporary SSH trust stores; no operator credentials or SSH daemon."""

import socket
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_ssh_client_loads_only_explicit_temporary_trust_store(tmp_path: Path) -> None:
    paramiko = pytest.importorskip("paramiko")
    from codomyrmex.networking import SSHClient

    key = paramiko.RSAKey.generate(1024)
    trust = paramiko.HostKeys()
    trust.add("isolated-test-host", key.get_name(), key)
    path = tmp_path / "known_hosts"
    trust.save(str(path))
    client = SSHClient("isolated-test-host", "test-user", known_hosts_file=str(path))
    try:
        assert len(client.client._system_host_keys) == 0
        actual = client.client.get_host_keys()
        assert list(actual) == ["isolated-test-host"]
        assert actual["isolated-test-host"][key.get_name()] == key
        assert isinstance(client.client._policy, paramiko.RejectPolicy)
    finally:
        client.close()


def test_default_policy_rejects_unknown_key_with_real_transport(
    known_hosts_file: Path,
) -> None:
    paramiko = pytest.importorskip("paramiko")
    from codomyrmex.networking import SSHClient

    client = SSHClient(
        "untrusted-test-host", "test-user", known_hosts_file=str(known_hosts_file)
    )
    left, right = socket.socketpair()
    # Paramiko's real policy logs through a real Transport even before a
    # handshake. No daemon, private key file, account, or fake client is used.
    client.client._transport = paramiko.Transport(left)
    try:
        key = paramiko.RSAKey.generate(1024)
        with pytest.raises(paramiko.SSHException, match="not found in known_hosts"):
            client.client._policy.missing_host_key(
                client.client, "untrusted-test-host", key
            )
        assert "untrusted-test-host" not in client.client.get_host_keys()
    finally:
        client.close()
        left.close()
        right.close()
