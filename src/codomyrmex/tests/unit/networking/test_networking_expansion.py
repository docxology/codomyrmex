"""Zero-Mock unit tests for networking module expansion.

Uses real networking clients and servers where possible, with skip markers
for tests requiring external services.
"""

import socket

import pytest

try:
    from codomyrmex.networking import PortScanner, SSHClient, TCPClient, UDPClient
    NETWORKING_AVAILABLE = True
except ImportError:
    NETWORKING_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not NETWORKING_AVAILABLE,
    reason="networking dependencies (paramiko, etc.) not installed",
)

# Check for real SSH
_HAS_SSH = False
try:
    s = socket.create_connection(("localhost", 22), timeout=0.5)
    s.close()
    _HAS_SSH = True
except Exception:
    pass

requires_ssh = pytest.mark.skipif(
    not _HAS_SSH,
    reason="SSH server not available on localhost:22",
)


@pytest.mark.unit
@requires_ssh
def test_ssh_client_logic():
    """Test SSHClient command execution with a real SSH connection."""
    # Skip if no proper credentials (this requires key-based auth)
    import os
    key_path = os.path.expanduser("~/.ssh/id_rsa")
    if not os.path.exists(key_path):
        pytest.skip("No SSH key found at ~/.ssh/id_rsa")

    username = os.environ.get("USER", os.environ.get("USERNAME", ""))
    if not username:
        pytest.skip("Cannot determine current username")

    client = SSHClient("localhost", username, key_filename=key_path)
    client.connect()
    status, out, err = client.execute_command("echo hello world")
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
        conn, addr = server_sock.accept()
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
    data, addr = client.receive(1024)
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
