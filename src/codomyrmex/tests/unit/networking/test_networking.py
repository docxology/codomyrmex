"""Zero-Mock comprehensive tests for the networking module.

Uses real HTTP requests (via httpbin.org or local echo), real loopback
TCP/UDP sockets, and skip markers for external services (SSH, WebSocket).
"""

import socket
import threading

import pytest
import requests as requests_lib

try:
    from codomyrmex import networking
    # Try importing EphemeralServer, might fail if path issues, handled in tests
    try:
        from codomyrmex.tests.utils.ephemeral_server import EphemeralServer
    except ImportError:
        EphemeralServer = None
    
    from codomyrmex.networking import (
        HTTPClient,
        PortScanner,
        Response,
        SSHClient,
        TCPClient,
        TCPServer,
        UDPClient,
        WebSocketClient,
        get_http_client,
    )
    from codomyrmex.networking.http_client import NetworkingError
    NETWORKING_AVAILABLE = True
except ImportError:
    NETWORKING_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not NETWORKING_AVAILABLE,
    reason="networking dependencies (paramiko, etc.) not installed",
)

# Check network availability
try:
    requests_lib.head("https://httpbin.org", timeout=3)
    _HAS_NETWORK = True
except Exception:
    _HAS_NETWORK = False

requires_network = pytest.mark.skipif(
    not _HAS_NETWORK,
    reason="Network unavailable (cannot reach httpbin.org)",
)


# ==============================================================================
# Module Import Tests
# ==============================================================================

class TestNetworkingModuleImport:
    """Test networking module import and structure."""

    def test_networking_module_import(self):
        """Test functionality: networking module import."""
        assert networking is not None
        assert hasattr(networking, "__path__")

    def test_networking_module_structure(self):
        """Test functionality: networking module structure."""
        assert hasattr(networking, "__file__")

    def test_networking_module_exports(self):
        """Test functionality: networking module exports."""
        assert hasattr(networking, "HTTPClient")
        assert hasattr(networking, "WebSocketClient")
        assert hasattr(networking, "SSHClient")
        assert hasattr(networking, "TCPClient")
        assert hasattr(networking, "UDPClient")
        assert hasattr(networking, "PortScanner")

    def test_get_http_client_factory(self):
        """Test functionality: get http client factory."""
        client = get_http_client()
        assert isinstance(client, HTTPClient)


# ==============================================================================
# Response Object Tests
# ==============================================================================

class TestResponse:
    """Tests for Response dataclass."""

    def test_response_creation(self):
        """Test functionality: response creation."""
        response = Response(
            status_code=200,
            headers={"Content-Type": "application/json"},
            content=b'{"key": "value"}',
            text='{"key": "value"}'
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

    def test_response_json_parsing(self):
        """Test functionality: response json parsing."""
        response = Response(
            status_code=200, headers={},
            content=b'{"name": "test", "value": 123}',
            text='{"name": "test", "value": 123}'
        )
        data = response.json()
        assert data["name"] == "test"
        assert data["value"] == 123

    def test_response_json_caching(self):
        """Test functionality: response json caching."""
        response = Response(
            status_code=200, headers={},
            content=b'{"cached": true}', text='{"cached": true}'
        )
        data1 = response.json()
        data2 = response.json()
        assert data1 is data2

    def test_response_with_predefined_json(self):
        """Test functionality: response with predefined json."""
        json_data = {"preloaded": "data"}
        response = Response(
            status_code=200, headers={},
            content=b'{"preloaded": "data"}',
            text='{"preloaded": "data"}',
            json_data=json_data
        )
        assert response.json() is json_data


# ==============================================================================
# HTTPClient Tests — Real HTTP
# ==============================================================================

class TestHTTPClient:
    """Tests for HTTPClient using real HTTP requests."""

    def test_client_initialization_defaults(self):
        """Test functionality: client initialization defaults."""
        client = HTTPClient()
        assert client.timeout == 30
        assert client.max_retries == 3
        assert client.retry_backoff == 1.0
        assert client.default_headers == {}

    def test_client_initialization_custom(self):
        """Test functionality: client initialization custom."""
        client = HTTPClient(
            timeout=60, max_retries=5, retry_backoff=2.0,
            headers={"Authorization": "Bearer token"}
        )
        assert client.timeout == 60
        assert client.max_retries == 5
        assert client.default_headers["Authorization"] == "Bearer token"

    def test_get_request(self):
        """Test functionality: get request."""
        if not EphemeralServer:
            pytest.skip("EphemeralServer not available")
            
        with EphemeralServer() as server:
            client = HTTPClient()
            response = client.get(f"{server.url}/get")
            assert response.status_code == 200
            data = response.json()
            assert "url" in data
            assert f"{server.url}/get" == data["url"]

    def test_post_request(self):
        """Test functionality: post request."""
        if not EphemeralServer:
             pytest.skip("EphemeralServer not available")

        with EphemeralServer() as server:
            client = HTTPClient()
            response = client.post(
                f"{server.url}/post",
                json={"name": "test"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["json"]["name"] == "test"

    def test_put_request(self):
        """Test functionality: put request."""
        if not EphemeralServer:
             pytest.skip("EphemeralServer not available")

        with EphemeralServer() as server:
            client = HTTPClient()
            response = client.put(
                f"{server.url}/put",
                json={"name": "updated"}
            )
            assert response.status_code == 200

    def test_delete_request(self):
        """Test functionality: delete request."""
        if not EphemeralServer:
             pytest.skip("EphemeralServer not available")

        with EphemeralServer() as server:
            client = HTTPClient()
            response = client.delete(f"{server.url}/delete")
            assert response.status_code == 200

    def test_request_with_custom_headers(self):
        """Test functionality: request with custom headers."""
        if not EphemeralServer:
             pytest.skip("EphemeralServer not available")

        with EphemeralServer() as server:
            client = HTTPClient()
            response = client.get(
                f"{server.url}/headers",
                headers={"X-Custom-Header": "custom-value"}
            )
            data = response.json()
            # headers keys are often lowercased or titlecased depending on server
            # EphemeralServer echoes exactly what it gets
            # requests might canonicalize?
            # Let's check generally
            assert data["headers"].get("X-Custom-Header") == "custom-value"

    def test_request_with_custom_timeout(self):
        """Test functionality: request with custom timeout."""
        if not EphemeralServer:
             pytest.skip("EphemeralServer not available")

        with EphemeralServer() as server:
            client = HTTPClient()
            response = client.get(f"{server.url}/get", timeout=60)
            assert response.status_code == 200

    def test_request_error_handling(self):
        """Test that request errors are wrapped in NetworkingError."""
        client = HTTPClient()
        with pytest.raises(NetworkingError):
            client.get("http://nonexistent-host-xyz-12345.invalid/data")

    def test_request_connection_error(self):
        """Test connection error handling."""
        client = HTTPClient()
        with pytest.raises(NetworkingError):
            client.get("http://127.0.0.1:1/impossible")

    def test_response_4xx_error(self):
        """Test functionality: response 4xx error."""
        if not EphemeralServer:
             pytest.skip("EphemeralServer not available")

        with EphemeralServer() as server:
            client = HTTPClient()
            response = client.get(f"{server.url}/status/404")
            assert response.status_code == 404

    @requires_network
    def test_response_5xx_error(self):
        """Test functionality: response 5xx error."""
        if not EphemeralServer:
             pytest.skip("EphemeralServer not available")
        
        with EphemeralServer() as server:
            client = HTTPClient(max_retries=0)
            with pytest.raises(NetworkingError):
                client.get(f"{server.url}/status/500")


# ==============================================================================
# WebSocketClient Tests
# ==============================================================================

class TestWebSocketClient:
    """Tests for WebSocketClient."""

    def test_websocket_client_initialization(self):
        """Test functionality: websocket client initialization."""
        client = WebSocketClient("ws://localhost:8080")
        assert client.url == "ws://localhost:8080"
        assert client.headers == {}
        assert client.reconnect_interval == 1.0
        assert client.max_reconnect_delay == 30.0

    def test_websocket_client_custom_initialization(self):
        """Test functionality: websocket client custom initialization."""
        client = WebSocketClient(
            "wss://example.com/ws",
            headers={"Authorization": "Bearer token"},
            reconnect_interval=2.0,
            max_reconnect_delay=60.0
        )
        assert client.url == "wss://example.com/ws"
        assert client.headers["Authorization"] == "Bearer token"

    @pytest.mark.asyncio
    async def test_websocket_on_handler_registration(self):
        client = WebSocketClient("ws://localhost:8080")
        handler = lambda data: None  # noqa: E731
        client.on(handler)
        assert handler in client._handlers

    @pytest.mark.asyncio
    async def test_websocket_message_handling_json(self):
        client = WebSocketClient("ws://localhost:8080")
        received = []
        async def handler(data):
            received.append(data)
        client.on(handler)
        await client._handle_message('{"type": "test", "value": 42}')
        assert received == [{"type": "test", "value": 42}]

    @pytest.mark.asyncio
    async def test_websocket_message_handling_string(self):
        client = WebSocketClient("ws://localhost:8080")
        received = []
        async def handler(data):
            received.append(data)
        client.on(handler)
        await client._handle_message("plain text message")
        assert received == ["plain text message"]

    @pytest.mark.asyncio
    async def test_websocket_message_handling_bytes(self):
        client = WebSocketClient("ws://localhost:8080")
        received = []
        async def handler(data):
            received.append(data)
        client.on(handler)
        await client._handle_message(b"binary data")
        assert received == [b"binary data"]

    @pytest.mark.asyncio
    async def test_websocket_sync_handler(self):
        client = WebSocketClient("ws://localhost:8080")
        received = []
        def handler(data):
            received.append(data)
        client.on(handler)
        await client._handle_message('{"test": true}')
        assert received == [{"test": True}]

    @pytest.mark.asyncio
    async def test_websocket_handler_exception_isolation(self):
        client = WebSocketClient("ws://localhost:8080")
        called = []
        async def failing_handler(data):
            raise ValueError("Handler error")
        async def working_handler(data):
            called.append(data)
        client.on(failing_handler)
        client.on(working_handler)
        await client._handle_message('{"test": 1}')
        assert len(called) == 1

    @pytest.mark.asyncio
    async def test_websocket_send_not_connected(self):
        client = WebSocketClient("ws://localhost:8080")
        from codomyrmex.networking.websocket_client import WebSocketError
        with pytest.raises(WebSocketError):
            await client.send({"message": "test"})

    @pytest.mark.asyncio
    async def test_websocket_close_without_connection(self):
        client = WebSocketClient("ws://localhost:8080")
        await client.close()
        assert client._running is False


# ==============================================================================
# SSHClient Tests — Skip if no local SSH
# ==============================================================================

_HAS_SSH = False
try:
    s = socket.create_connection(("localhost", 22), timeout=0.5)
    s.close()
    _HAS_SSH = True
except Exception:
    pass

requires_ssh = pytest.mark.skipif(not _HAS_SSH, reason="No local SSH server")


class TestSSHClient:
    """Tests for SSHClient — uses real paramiko if SSH available."""

    def test_ssh_client_initialization(self):
        """Test functionality: ssh client initialization."""
        client = SSHClient(hostname="example.com", username="user", password="pass")
        assert client.hostname == "example.com"
        assert client.username == "user"
        assert client.port == 22

    def test_ssh_client_key_based_auth(self):
        """Test functionality: ssh client key based auth."""
        client = SSHClient(hostname="example.com", username="user", key_filename="/path/to/key")
        assert client.key_filename == "/path/to/key"

    def test_ssh_client_custom_port(self):
        """Test functionality: ssh client custom port."""
        client = SSHClient(hostname="example.com", username="user", port=2222)
        assert client.port == 2222

    @requires_ssh
    def test_ssh_client_connect_and_execute(self):
        """Test functionality: ssh client connect and execute."""
        import os
        key_path = os.path.expanduser("~/.ssh/id_rsa")
        if not os.path.exists(key_path):
            pytest.skip("No SSH key at ~/.ssh/id_rsa")
        username = os.environ.get("USER", "")
        if not username:
            pytest.skip("Cannot determine current user")

        client = SSHClient("localhost", username, key_filename=key_path)
        client.connect()
        status, out, err = client.execute_command("echo hello")
        client.close()
        assert status == 0
        assert "hello" in out


# ==============================================================================
# TCPClient/Server Tests — Real Loopback
# ==============================================================================

class TestTCPClient:
    """Tests for TCPClient using real loopback sockets."""

    def test_tcp_client_initialization(self):
        """Test functionality: tcp client initialization."""
        client = TCPClient("localhost", 8080)
        assert client.host == "localhost"
        assert client.port == 8080

    def test_tcp_client_connect_send_receive(self):
        """Test functionality: tcp client connect send receive."""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        port = server_sock.getsockname()[1]
        server_sock.listen(1)

        def echo():
            conn, _ = server_sock.accept()
            data = conn.recv(1024)
            conn.sendall(data)
            conn.close()
            server_sock.close()

        t = threading.Thread(target=echo, daemon=True)
        t.start()

        client = TCPClient("127.0.0.1", port)
        client.connect()
        client.send(b"test data")
        data = client.receive(1024)
        client.close()

        assert data == b"test data"
        t.join(timeout=2)


class TestTCPServer:
    """Tests for TCPServer using real sockets."""

    def test_tcp_server_initialization(self):
        """Test functionality: tcp server initialization."""
        server = TCPServer("0.0.0.0", 0)
        assert server.host == "0.0.0.0"

    def test_tcp_server_start_and_accept(self):
        """Test functionality: tcp server start and accept."""
        server = TCPServer("127.0.0.1", 0)
        server.start()
        port = server.sock.getsockname()[1]

        def connect():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", port))
            s.close()

        t = threading.Thread(target=connect, daemon=True)
        t.start()

        conn, addr = server.accept()
        conn.close()
        server.close()
        t.join(timeout=2)
        assert addr[0] == "127.0.0.1"


# ==============================================================================
# UDPClient Tests — Real Loopback
# ==============================================================================

class TestUDPClient:
    """Tests for UDPClient using real loopback sockets."""

    def test_udp_client_initialization(self):
        """Test functionality: udp client initialization."""
        client = UDPClient("localhost", 5000)
        assert client.host == "localhost"
        assert client.port == 5000

    def test_udp_client_send_receive(self):
        """Test functionality: udp client send receive."""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_sock.bind(("127.0.0.1", 0))
        port = server_sock.getsockname()[1]

        def echo():
            data, addr = server_sock.recvfrom(1024)
            server_sock.sendto(data, addr)
            server_sock.close()

        t = threading.Thread(target=echo, daemon=True)
        t.start()

        client = UDPClient("127.0.0.1", port)
        client.send(b"udp data")
        data, addr = client.receive(1024)
        client.close()

        assert data == b"udp data"
        t.join(timeout=2)


# ==============================================================================
# PortScanner Tests — Real Ports
# ==============================================================================

class TestPortScanner:
    """Tests for PortScanner using real ports."""

    def test_is_port_open_success(self):
        """Test functionality: is port open success."""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        port = server_sock.getsockname()[1]
        server_sock.listen(1)
        try:
            assert PortScanner.is_port_open("127.0.0.1", port) is True
        finally:
            server_sock.close()

    def test_is_port_open_connection_refused(self):
        """Test functionality: is port open connection refused."""
        # Port 1 is almost never open
        assert PortScanner.is_port_open("127.0.0.1", 1) is False

    def test_scan_range(self):
        """Test functionality: scan range."""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        port = server_sock.getsockname()[1]
        server_sock.listen(1)
        try:
            result = PortScanner.scan_range("127.0.0.1", port, port)
            assert port in result
        finally:
            server_sock.close()


# ==============================================================================
# Integration-style Tests — Real HTTP
# ==============================================================================

class TestNetworkingIntegration:
    """Integration tests using real services."""

    def test_http_client_json_workflow(self):
        """Test functionality: http client json workflow."""
        if not EphemeralServer:
             pytest.skip("EphemeralServer not available")

        with EphemeralServer() as server:
            client = HTTPClient(headers={"Accept": "application/json"})
            response = client.get(f"{server.url}/get")
            assert response.status_code == 200
            data = response.json()
            assert "url" in data

    def test_http_client_post_json_workflow(self):
        """Test functionality: http client post json workflow."""
        if not EphemeralServer:
             pytest.skip("EphemeralServer not available")

        with EphemeralServer() as server:
            client = HTTPClient()
            response = client.post(
                f"{server.url}/post",
                json={"name": "Bob", "email": "bob@example.com"}
            )
            assert response.status_code == 200
            assert response.json()["json"]["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_websocket_message_flow(self):
        client = WebSocketClient("ws://localhost:8080")
        messages = []
        async def collector(data):
            messages.append(data)
        client.on(collector)
        await client._handle_message('{"event": "connect", "status": "ok"}')
        await client._handle_message('{"event": "data", "payload": {"value": 42}}')
        assert len(messages) == 2
        assert messages[0]["event"] == "connect"


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestNetworkingErrorHandling:
    """Tests for error handling in networking module."""

    def test_networking_error_creation(self):
        """Test functionality: networking error creation."""
        error = NetworkingError("Connection failed")
        assert "Connection failed" in str(error)

    def test_networking_error_inheritance(self):
        """Test functionality: networking error inheritance."""
        from codomyrmex.exceptions import CodomyrmexError
        assert isinstance(NetworkingError("Test"), CodomyrmexError)

    def test_http_client_wraps_request_exceptions(self):
        """Test functionality: http client wraps request exceptions."""
        client = HTTPClient()
        with pytest.raises(NetworkingError):
            client.get("http://nonexistent-host-xyz-12345.invalid")
