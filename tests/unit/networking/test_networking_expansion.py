"""Zero-Mock unit tests for networking module expansion.

Uses real networking clients and servers where possible, with skip markers
for tests requiring external services.
"""

from __future__ import annotations

import os
import socket
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from codomyrmex.networking.ssh_sftp import SSHClient as SSHClientType

try:
    from codomyrmex.networking import PortScanner, SSHClient, TCPClient, UDPClient

    NETWORKING_AVAILABLE = True
except ImportError:
    NETWORKING_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not NETWORKING_AVAILABLE,
    reason="networking dependencies (paramiko, etc.) not installed",
)

requires_ssh = pytest.mark.skipif(
    os.environ.get("CODOMYRMEX_RUN_LIVE_SSH_TESTS") != "1",
    reason="Credentialed SSH requires CODOMYRMEX_RUN_LIVE_SSH_TESTS=1",
)


@pytest.mark.unit
@requires_ssh
def test_ssh_client_logic(live_ssh_client: SSHClientType):
    """Use only the explicitly configured live account and trust store."""
    client = live_ssh_client
    try:
        client.connect()
        status, out, _err = client.execute_command("echo hello world")
    finally:
        client.close()
    assert status == 0
    assert "hello world" in out


@pytest.mark.unit
def test_tcp_client_real():
    """Test TCPClient with a real loopback TCP server."""
    import threading

    # Start a real TCP server on a random port
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("127.0.0.1", 0))
    port = server_sock.getsockname()[1]
    server_sock.listen(1)

    def handle_client():
        conn, _addr = server_sock.accept()
        data = conn.recv(1024)
        conn.sendall(data)  # Echo back
        conn.close()
        server_sock.close()

    t = threading.Thread(target=handle_client, daemon=True)
    t.start()

    client = TCPClient("127.0.0.1", port)
    client.connect()
    client.send(b"data")
    response = client.receive(1024)
    client.close()

    assert response == b"data"
    t.join(timeout=2)


@pytest.mark.unit
def test_udp_client_real():
    """Test UDPClient with a real loopback UDP echo."""
    import threading

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind(("127.0.0.1", 0))
    port = server_sock.getsockname()[1]

    received = []

    def handle_udp():
        data, addr = server_sock.recvfrom(1024)
        received.append(data)
        server_sock.sendto(data, addr)
        server_sock.close()

    t = threading.Thread(target=handle_udp, daemon=True)
    t.start()

    client = UDPClient("127.0.0.1", port)
    client.send(b"pulse")
    data, _addr = client.receive(1024)
    client.close()

    assert data == b"pulse"
    assert received == [b"pulse"]
    t.join(timeout=2)


@pytest.mark.unit
def test_port_scanner():
    """Test PortScanner logic with a real listening port."""
    # Start a real server
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("127.0.0.1", 0))
    port = server_sock.getsockname()[1]
    server_sock.listen(1)

    try:
        assert PortScanner.is_port_open("127.0.0.1", port) is True
        # Test a port that's very unlikely to be open
        assert PortScanner.is_port_open("127.0.0.1", 1) is False
    finally:
        server_sock.close()
