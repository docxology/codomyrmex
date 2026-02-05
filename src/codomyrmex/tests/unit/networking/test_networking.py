"""Comprehensive tests for the networking module.

Tests cover:
- HTTPClient requests (GET, POST, PUT, DELETE)
- Response handling
- Headers and authentication
- Timeout handling
- Error responses
- WebSocket connection patterns
- TCP/UDP client basics
- SSH client operations
- Port scanning utilities
"""

import asyncio
import json
import socket
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock

import pytest

try:
    from codomyrmex import networking
    from codomyrmex.networking import (
        HTTPClient,
        Response,
        WebSocketClient,
        SSHClient,
        TCPClient,
        TCPServer,
        UDPClient,
        PortScanner,
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


# ==============================================================================
# Module Import Tests
# ==============================================================================

class TestNetworkingModuleImport:
    """Test networking module import and structure."""

    def test_networking_module_import(self):
        """Verify that the networking module can be imported successfully."""
        assert networking is not None
        assert hasattr(networking, "__path__")

    def test_networking_module_structure(self):
        """Verify basic structure of networking module."""
        assert hasattr(networking, "__file__")

    def test_networking_module_exports(self):
        """Verify expected exports from networking module."""
        assert hasattr(networking, "HTTPClient")
        assert hasattr(networking, "WebSocketClient")
        assert hasattr(networking, "SSHClient")
        assert hasattr(networking, "TCPClient")
        assert hasattr(networking, "UDPClient")
        assert hasattr(networking, "PortScanner")

    def test_get_http_client_factory(self):
        """Test get_http_client factory function."""
        client = get_http_client()
        assert isinstance(client, HTTPClient)


# ==============================================================================
# Response Object Tests
# ==============================================================================

class TestResponse:
    """Tests for Response dataclass."""

    def test_response_creation(self):
        """Test basic response creation."""
        response = Response(
            status_code=200,
            headers={"Content-Type": "application/json"},
            content=b'{"key": "value"}',
            text='{"key": "value"}'
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.content == b'{"key": "value"}'
        assert response.text == '{"key": "value"}'

    def test_response_json_parsing(self):
        """Test response JSON parsing."""
        response = Response(
            status_code=200,
            headers={},
            content=b'{"name": "test", "value": 123}',
            text='{"name": "test", "value": 123}'
        )
        data = response.json()
        assert data["name"] == "test"
        assert data["value"] == 123

    def test_response_json_caching(self):
        """Test that JSON parsing result is cached."""
        response = Response(
            status_code=200,
            headers={},
            content=b'{"cached": true}',
            text='{"cached": true}'
        )
        # First call parses JSON
        data1 = response.json()
        # Second call should return cached result
        data2 = response.json()
        assert data1 is data2

    def test_response_with_predefined_json(self):
        """Test response with pre-parsed JSON data."""
        json_data = {"preloaded": "data"}
        response = Response(
            status_code=200,
            headers={},
            content=b'{"preloaded": "data"}',
            text='{"preloaded": "data"}',
            json_data=json_data
        )
        assert response.json() is json_data


# ==============================================================================
# HTTPClient Tests
# ==============================================================================

class TestHTTPClient:
    """Tests for HTTPClient."""

    @pytest.fixture
    def mock_session(self):
        """Create mock requests session."""
        with patch('codomyrmex.networking.http_client.requests') as mock_requests:
            mock_session = MagicMock()
            mock_requests.Session.return_value = mock_session
            yield mock_session

    @pytest.fixture
    def client(self, mock_session):
        """Create HTTPClient with mocked session."""
        return HTTPClient()

    def test_client_initialization_defaults(self, client):
        """Test client initialization with defaults."""
        assert client.timeout == 30
        assert client.max_retries == 3
        assert client.retry_backoff == 1.0
        assert client.default_headers == {}

    def test_client_initialization_custom(self, mock_session):
        """Test client initialization with custom values."""
        client = HTTPClient(
            timeout=60,
            max_retries=5,
            retry_backoff=2.0,
            headers={"Authorization": "Bearer token"}
        )
        assert client.timeout == 60
        assert client.max_retries == 5
        assert client.retry_backoff == 2.0
        assert client.default_headers["Authorization"] == "Bearer token"

    def test_get_request(self, client, mock_session):
        """Test GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = b'{"result": "success"}'
        mock_response.text = '{"result": "success"}'
        mock_response.json.return_value = {"result": "success"}
        mock_session.request.return_value = mock_response

        response = client.get("https://api.example.com/data")

        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == "https://api.example.com/data"
        assert response.status_code == 200

    def test_post_request(self, client, mock_session):
        """Test POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.headers = {}
        mock_response.content = b'{"id": 123}'
        mock_response.text = '{"id": 123}'
        mock_response.json.return_value = {"id": 123}
        mock_session.request.return_value = mock_response

        response = client.post(
            "https://api.example.com/items",
            data={"name": "test"}
        )

        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "POST"
        assert response.status_code == 201

    def test_put_request(self, client, mock_session):
        """Test PUT request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b'{"updated": true}'
        mock_response.text = '{"updated": true}'
        mock_response.json.return_value = {"updated": True}
        mock_session.request.return_value = mock_response

        response = client.put(
            "https://api.example.com/items/123",
            data={"name": "updated"}
        )

        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "PUT"
        assert response.status_code == 200

    def test_delete_request(self, client, mock_session):
        """Test DELETE request."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.headers = {}
        mock_response.content = b''
        mock_response.text = ''
        mock_response.json.side_effect = ValueError("No JSON")
        mock_session.request.return_value = mock_response

        response = client.delete("https://api.example.com/items/123")

        call_args = mock_session.request.call_args
        assert call_args[1]["method"] == "DELETE"
        assert response.status_code == 204

    def test_request_with_custom_headers(self, client, mock_session):
        """Test request with custom headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b'{}'
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_session.request.return_value = mock_response

        client.get(
            "https://api.example.com/data",
            headers={"X-Custom-Header": "custom-value"}
        )

        call_args = mock_session.request.call_args
        assert call_args[1]["headers"]["X-Custom-Header"] == "custom-value"

    def test_request_with_custom_timeout(self, client, mock_session):
        """Test request with custom timeout."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b'{}'
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_session.request.return_value = mock_response

        client.get("https://api.example.com/data", timeout=60)

        call_args = mock_session.request.call_args
        assert call_args[1]["timeout"] == 60

    def test_request_error_handling(self):
        """Test that request errors are wrapped in NetworkingError."""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        with patch.object(requests.Session, 'request') as mock_request:
            mock_request.side_effect = requests.exceptions.RequestException("Connection failed")

            client = HTTPClient()
            with pytest.raises(NetworkingError) as exc_info:
                client.get("https://api.example.com/data")

            assert "Connection failed" in str(exc_info.value)

    def test_request_timeout_error(self):
        """Test timeout error handling."""
        import requests

        with patch.object(requests.Session, 'request') as mock_request:
            mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

            client = HTTPClient()
            with pytest.raises(NetworkingError):
                client.get("https://api.example.com/data")

    def test_request_connection_error(self):
        """Test connection error handling."""
        import requests

        with patch.object(requests.Session, 'request') as mock_request:
            mock_request.side_effect = requests.exceptions.ConnectionError("Failed to connect")

            client = HTTPClient()
            with pytest.raises(NetworkingError):
                client.get("https://api.example.com/data")

    def test_response_with_empty_content(self, client, mock_session):
        """Test handling response with empty content."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.headers = {}
        mock_response.content = b''
        mock_response.text = ''
        mock_response.json.side_effect = ValueError("No content")
        mock_session.request.return_value = mock_response

        response = client.get("https://api.example.com/empty")
        assert response.status_code == 204
        assert response.content == b''

    def test_response_4xx_error(self, client, mock_session):
        """Test handling 4xx error responses."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {}
        mock_response.content = b'{"error": "Not found"}'
        mock_response.text = '{"error": "Not found"}'
        mock_response.json.return_value = {"error": "Not found"}
        mock_session.request.return_value = mock_response

        response = client.get("https://api.example.com/missing")
        assert response.status_code == 404
        assert response.json()["error"] == "Not found"

    def test_response_5xx_error(self, client, mock_session):
        """Test handling 5xx error responses."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.headers = {}
        mock_response.content = b'{"error": "Internal server error"}'
        mock_response.text = '{"error": "Internal server error"}'
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_session.request.return_value = mock_response

        response = client.get("https://api.example.com/error")
        assert response.status_code == 500


# ==============================================================================
# WebSocketClient Tests
# ==============================================================================

class TestWebSocketClient:
    """Tests for WebSocketClient."""

    def test_websocket_client_initialization(self):
        """Test WebSocketClient initialization."""
        client = WebSocketClient("ws://localhost:8080")
        assert client.url == "ws://localhost:8080"
        assert client.headers == {}
        assert client.reconnect_interval == 1.0
        assert client.max_reconnect_delay == 30.0

    def test_websocket_client_custom_initialization(self):
        """Test WebSocketClient initialization with custom values."""
        client = WebSocketClient(
            "wss://example.com/ws",
            headers={"Authorization": "Bearer token"},
            reconnect_interval=2.0,
            max_reconnect_delay=60.0
        )
        assert client.url == "wss://example.com/ws"
        assert client.headers["Authorization"] == "Bearer token"
        assert client.reconnect_interval == 2.0
        assert client.max_reconnect_delay == 60.0

    @pytest.mark.asyncio
    async def test_websocket_on_handler_registration(self):
        """Test handler registration with .on() method."""
        client = WebSocketClient("ws://localhost:8080")
        handler = MagicMock()
        client.on(handler)
        assert handler in client._handlers

    @pytest.mark.asyncio
    async def test_websocket_multiple_handlers(self):
        """Test registering multiple handlers."""
        client = WebSocketClient("ws://localhost:8080")
        handler1 = MagicMock()
        handler2 = MagicMock()
        client.on(handler1)
        client.on(handler2)
        assert len(client._handlers) == 2

    @pytest.mark.asyncio
    async def test_websocket_message_handling_json(self):
        """Test message handling parses JSON."""
        client = WebSocketClient("ws://localhost:8080")
        received = []

        async def handler(data):
            received.append(data)

        client.on(handler)
        await client._handle_message('{"type": "test", "value": 42}')

        assert len(received) == 1
        assert received[0] == {"type": "test", "value": 42}

    @pytest.mark.asyncio
    async def test_websocket_message_handling_string(self):
        """Test message handling with non-JSON string."""
        client = WebSocketClient("ws://localhost:8080")
        received = []

        async def handler(data):
            received.append(data)

        client.on(handler)
        await client._handle_message("plain text message")

        assert len(received) == 1
        assert received[0] == "plain text message"

    @pytest.mark.asyncio
    async def test_websocket_message_handling_bytes(self):
        """Test message handling with bytes."""
        client = WebSocketClient("ws://localhost:8080")
        received = []

        async def handler(data):
            received.append(data)

        client.on(handler)
        await client._handle_message(b"binary data")

        assert len(received) == 1
        assert received[0] == b"binary data"

    @pytest.mark.asyncio
    async def test_websocket_sync_handler(self):
        """Test synchronous handler execution."""
        client = WebSocketClient("ws://localhost:8080")
        handler = MagicMock()
        client.on(handler)

        await client._handle_message('{"test": true}')

        handler.assert_called_once_with({"test": True})

    @pytest.mark.asyncio
    async def test_websocket_handler_exception_isolation(self):
        """Test that handler exceptions don't break other handlers."""
        client = WebSocketClient("ws://localhost:8080")
        called = []

        async def failing_handler(data):
            raise ValueError("Handler error")

        async def working_handler(data):
            called.append(data)

        client.on(failing_handler)
        client.on(working_handler)

        # Should not raise
        await client._handle_message('{"test": 1}')

        # Working handler should have been called
        assert len(called) == 1

    @pytest.mark.asyncio
    async def test_websocket_send_not_connected(self):
        """Test send raises error when not connected."""
        client = WebSocketClient("ws://localhost:8080")
        from codomyrmex.networking.websocket_client import WebSocketError

        with pytest.raises(WebSocketError):
            await client.send({"message": "test"})

    @pytest.mark.asyncio
    async def test_websocket_close_without_connection(self):
        """Test close without active connection."""
        client = WebSocketClient("ws://localhost:8080")
        # Should not raise
        await client.close()
        assert client._running is False


# ==============================================================================
# SSHClient Tests
# ==============================================================================

class TestSSHClient:
    """Tests for SSHClient."""

    @pytest.fixture
    def mock_paramiko(self):
        """Create mock paramiko."""
        with patch('codomyrmex.networking.ssh_sftp.paramiko') as mock:
            yield mock

    def test_ssh_client_initialization(self, mock_paramiko):
        """Test SSHClient initialization."""
        client = SSHClient(
            hostname="example.com",
            username="user",
            password="pass"
        )
        assert client.hostname == "example.com"
        assert client.username == "user"
        assert client.password == "pass"
        assert client.port == 22

    def test_ssh_client_key_based_auth(self, mock_paramiko):
        """Test SSHClient with key-based authentication."""
        client = SSHClient(
            hostname="example.com",
            username="user",
            key_filename="/path/to/key"
        )
        assert client.key_filename == "/path/to/key"
        assert client.password is None

    def test_ssh_client_custom_port(self, mock_paramiko):
        """Test SSHClient with custom port."""
        client = SSHClient(
            hostname="example.com",
            username="user",
            port=2222
        )
        assert client.port == 2222

    def test_ssh_client_connect(self, mock_paramiko):
        """Test SSH connection."""
        mock_ssh = MagicMock()
        mock_paramiko.SSHClient.return_value = mock_ssh

        client = SSHClient("localhost", "user", "pass")
        client.connect()

        mock_ssh.connect.assert_called_once_with(
            hostname="localhost",
            port=22,
            username="user",
            password="pass",
            key_filename=None
        )

    def test_ssh_client_execute_command(self, mock_paramiko):
        """Test SSH command execution."""
        mock_ssh = MagicMock()
        mock_paramiko.SSHClient.return_value = mock_ssh

        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b"command output"
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

        client = SSHClient("localhost", "user", "pass")
        client.connect()
        status, stdout, stderr = client.execute_command("ls -la")

        assert status == 0
        assert stdout == "command output"
        assert stderr == ""
        mock_ssh.exec_command.assert_called_once_with("ls -la")

    def test_ssh_client_get_sftp(self, mock_paramiko):
        """Test getting SFTP client."""
        mock_ssh = MagicMock()
        mock_sftp = MagicMock()
        mock_paramiko.SSHClient.return_value = mock_ssh
        mock_ssh.open_sftp.return_value = mock_sftp

        client = SSHClient("localhost", "user", "pass")
        sftp = client.get_sftp()

        mock_ssh.open_sftp.assert_called_once()
        assert sftp is mock_sftp

    def test_ssh_client_close(self, mock_paramiko):
        """Test SSH connection close."""
        mock_ssh = MagicMock()
        mock_paramiko.SSHClient.return_value = mock_ssh

        client = SSHClient("localhost", "user", "pass")
        client.close()

        mock_ssh.close.assert_called_once()

    def test_ssh_client_context_manager(self, mock_paramiko):
        """Test SSHClient as context manager."""
        mock_ssh = MagicMock()
        mock_paramiko.SSHClient.return_value = mock_ssh

        with SSHClient("localhost", "user", "pass") as client:
            mock_ssh.connect.assert_called_once()

        mock_ssh.close.assert_called_once()


# ==============================================================================
# TCPClient Tests
# ==============================================================================

class TestTCPClient:
    """Tests for TCPClient."""

    @pytest.fixture
    def mock_socket(self):
        """Create mock socket."""
        with patch('codomyrmex.networking.raw_sockets.socket.socket') as mock:
            yield mock

    def test_tcp_client_initialization(self, mock_socket):
        """Test TCPClient initialization."""
        client = TCPClient("localhost", 8080)
        assert client.host == "localhost"
        assert client.port == 8080

    def test_tcp_client_connect(self, mock_socket):
        """Test TCP connection."""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        client = TCPClient("localhost", 8080)
        client.connect()

        mock_sock.connect.assert_called_once_with(("localhost", 8080))

    def test_tcp_client_send(self, mock_socket):
        """Test TCP send."""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        client = TCPClient("localhost", 8080)
        client.send(b"test data")

        mock_sock.sendall.assert_called_once_with(b"test data")

    def test_tcp_client_receive(self, mock_socket):
        """Test TCP receive."""
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b"response data"
        mock_socket.return_value = mock_sock

        client = TCPClient("localhost", 8080)
        data = client.receive(1024)

        mock_sock.recv.assert_called_once_with(1024)
        assert data == b"response data"

    def test_tcp_client_close(self, mock_socket):
        """Test TCP close."""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        client = TCPClient("localhost", 8080)
        client.close()

        mock_sock.close.assert_called_once()

    def test_tcp_client_default_buffer_size(self, mock_socket):
        """Test TCP receive with default buffer size."""
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b"data"
        mock_socket.return_value = mock_sock

        client = TCPClient("localhost", 8080)
        client.receive()

        mock_sock.recv.assert_called_once_with(1024)


# ==============================================================================
# TCPServer Tests
# ==============================================================================

class TestTCPServer:
    """Tests for TCPServer."""

    @pytest.fixture
    def mock_socket(self):
        """Create mock socket."""
        with patch('codomyrmex.networking.raw_sockets.socket.socket') as mock:
            yield mock

    def test_tcp_server_initialization(self, mock_socket):
        """Test TCPServer initialization."""
        server = TCPServer("0.0.0.0", 9000)
        assert server.host == "0.0.0.0"
        assert server.port == 9000

    def test_tcp_server_start(self, mock_socket):
        """Test TCP server start."""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        server = TCPServer("0.0.0.0", 9000)
        server.start()

        mock_sock.bind.assert_called_once_with(("0.0.0.0", 9000))
        mock_sock.listen.assert_called_once_with(1)

    def test_tcp_server_accept(self, mock_socket):
        """Test TCP server accept."""
        mock_sock = MagicMock()
        mock_conn = MagicMock()
        mock_addr = ("127.0.0.1", 12345)
        mock_sock.accept.return_value = (mock_conn, mock_addr)
        mock_socket.return_value = mock_sock

        server = TCPServer("0.0.0.0", 9000)
        conn, addr = server.accept()

        assert conn is mock_conn
        assert addr == mock_addr

    def test_tcp_server_close(self, mock_socket):
        """Test TCP server close."""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        server = TCPServer("0.0.0.0", 9000)
        server.close()

        mock_sock.close.assert_called_once()


# ==============================================================================
# UDPClient Tests
# ==============================================================================

class TestUDPClient:
    """Tests for UDPClient."""

    @pytest.fixture
    def mock_socket(self):
        """Create mock socket."""
        with patch('codomyrmex.networking.raw_sockets.socket.socket') as mock:
            yield mock

    def test_udp_client_initialization(self, mock_socket):
        """Test UDPClient initialization."""
        client = UDPClient("localhost", 5000)
        assert client.host == "localhost"
        assert client.port == 5000

    def test_udp_client_send(self, mock_socket):
        """Test UDP send."""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        client = UDPClient("localhost", 5000)
        client.send(b"udp data")

        mock_sock.sendto.assert_called_once_with(b"udp data", ("localhost", 5000))

    def test_udp_client_receive(self, mock_socket):
        """Test UDP receive."""
        mock_sock = MagicMock()
        mock_sock.recvfrom.return_value = (b"response", ("127.0.0.1", 5000))
        mock_socket.return_value = mock_sock

        client = UDPClient("localhost", 5000)
        data, addr = client.receive(1024)

        mock_sock.recvfrom.assert_called_once_with(1024)
        assert data == b"response"
        assert addr == ("127.0.0.1", 5000)

    def test_udp_client_close(self, mock_socket):
        """Test UDP close."""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        client = UDPClient("localhost", 5000)
        client.close()

        mock_sock.close.assert_called_once()

    def test_udp_client_default_buffer_size(self, mock_socket):
        """Test UDP receive with default buffer size."""
        mock_sock = MagicMock()
        mock_sock.recvfrom.return_value = (b"data", ("127.0.0.1", 5000))
        mock_socket.return_value = mock_sock

        client = UDPClient("localhost", 5000)
        client.receive()

        mock_sock.recvfrom.assert_called_once_with(1024)


# ==============================================================================
# PortScanner Tests
# ==============================================================================

class TestPortScanner:
    """Tests for PortScanner."""

    @pytest.fixture
    def mock_socket(self):
        """Create mock socket."""
        with patch('codomyrmex.networking.raw_sockets.socket.socket') as mock:
            yield mock

    def test_is_port_open_success(self, mock_socket):
        """Test port is open when connection succeeds."""
        mock_sock = MagicMock()
        mock_sock.connect.return_value = None
        mock_socket.return_value.__enter__.return_value = mock_sock

        result = PortScanner.is_port_open("localhost", 80)

        assert result is True

    def test_is_port_open_connection_refused(self, mock_socket):
        """Test port is closed when connection is refused."""
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = ConnectionRefusedError()
        mock_socket.return_value.__enter__.return_value = mock_sock

        result = PortScanner.is_port_open("localhost", 80)

        assert result is False

    def test_is_port_open_timeout(self, mock_socket):
        """Test port is closed on timeout."""
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = socket.timeout()
        mock_socket.return_value.__enter__.return_value = mock_sock

        result = PortScanner.is_port_open("localhost", 80)

        assert result is False

    def test_is_port_open_socket_error(self, mock_socket):
        """Test port is closed on socket error."""
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = socket.error()
        mock_socket.return_value.__enter__.return_value = mock_sock

        result = PortScanner.is_port_open("localhost", 80)

        assert result is False

    def test_is_port_open_custom_timeout(self, mock_socket):
        """Test port scan with custom timeout."""
        mock_sock = MagicMock()
        mock_sock.connect.return_value = None
        mock_socket.return_value.__enter__.return_value = mock_sock

        PortScanner.is_port_open("localhost", 80, timeout=5.0)

        mock_sock.settimeout.assert_called_once_with(5.0)

    def test_scan_range_all_open(self, mock_socket):
        """Test scanning range with all ports open."""
        mock_sock = MagicMock()
        mock_sock.connect.return_value = None
        mock_socket.return_value.__enter__.return_value = mock_sock

        result = PortScanner.scan_range("localhost", 80, 82)

        assert result == [80, 81, 82]

    def test_scan_range_none_open(self, mock_socket):
        """Test scanning range with no ports open."""
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = ConnectionRefusedError()
        mock_socket.return_value.__enter__.return_value = mock_sock

        result = PortScanner.scan_range("localhost", 80, 82)

        assert result == []

    def test_scan_range_some_open(self, mock_socket):
        """Test scanning range with some ports open."""
        mock_sock = MagicMock()

        def connect_side_effect(addr):
            host, port = addr
            if port == 80 or port == 443:
                return None
            raise ConnectionRefusedError()

        mock_sock.connect.side_effect = connect_side_effect
        mock_socket.return_value.__enter__.return_value = mock_sock

        result = PortScanner.scan_range("localhost", 79, 444)

        assert 80 in result
        assert 443 in result


# ==============================================================================
# Integration-style Tests
# ==============================================================================

class TestNetworkingIntegration:
    """Integration-style tests for networking module."""

    def test_http_client_json_workflow(self):
        """Test complete HTTP client JSON workflow."""
        with patch('codomyrmex.networking.http_client.requests') as mock_requests:
            mock_session = MagicMock()
            mock_requests.Session.return_value = mock_session

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.content = b'{"users": [{"id": 1, "name": "Alice"}]}'
            mock_response.text = '{"users": [{"id": 1, "name": "Alice"}]}'
            mock_response.json.return_value = {"users": [{"id": 1, "name": "Alice"}]}
            mock_session.request.return_value = mock_response

            client = HTTPClient(headers={"Accept": "application/json"})
            response = client.get("https://api.example.com/users")

            assert response.status_code == 200
            data = response.json()
            assert "users" in data
            assert data["users"][0]["name"] == "Alice"

    def test_http_client_post_json_workflow(self):
        """Test HTTP POST with JSON body."""
        with patch('codomyrmex.networking.http_client.requests') as mock_requests:
            mock_session = MagicMock()
            mock_requests.Session.return_value = mock_session

            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.headers = {}
            mock_response.content = b'{"id": 123, "created": true}'
            mock_response.text = '{"id": 123, "created": true}'
            mock_response.json.return_value = {"id": 123, "created": True}
            mock_session.request.return_value = mock_response

            client = HTTPClient()
            response = client.post(
                "https://api.example.com/users",
                json={"name": "Bob", "email": "bob@example.com"}
            )

            assert response.status_code == 201
            assert response.json()["created"] is True

    @pytest.mark.asyncio
    async def test_websocket_message_flow(self):
        """Test WebSocket message handling flow."""
        client = WebSocketClient("ws://localhost:8080")
        messages = []

        async def collector(data):
            messages.append(data)

        client.on(collector)

        # Simulate receiving messages
        await client._handle_message('{"event": "connect", "status": "ok"}')
        await client._handle_message('{"event": "data", "payload": {"value": 42}}')

        assert len(messages) == 2
        assert messages[0]["event"] == "connect"
        assert messages[1]["payload"]["value"] == 42


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestNetworkingErrorHandling:
    """Tests for error handling in networking module."""

    def test_networking_error_creation(self):
        """Test NetworkingError creation."""
        error = NetworkingError("Connection failed")
        assert "Connection failed" in str(error)

    def test_networking_error_inheritance(self):
        """Test NetworkingError inherits from CodomyrmexError."""
        from codomyrmex.exceptions import CodomyrmexError
        error = NetworkingError("Test error")
        assert isinstance(error, CodomyrmexError)

    def test_http_client_wraps_request_exceptions(self):
        """Test HTTP client wraps request exceptions in NetworkingError."""
        import requests

        with patch.object(requests.Session, 'request') as mock_request:
            mock_request.side_effect = requests.exceptions.RequestException("Failed")

            client = HTTPClient()
            with pytest.raises(NetworkingError):
                client.get("https://example.com")
