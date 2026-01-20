"""Unit tests for networking module expansion."""

import pytest
from unittest.mock import MagicMock, patch
from codomyrmex.networking import SSHClient, TCPClient, UDPClient, PortScanner

def test_ssh_client_logic():
    """Test SSHClient command execution logic."""
    with patch('paramiko.SSHClient') as mock_ssh_cls:
        mock_ssh = MagicMock()
        mock_ssh_cls.return_value = mock_ssh
        
        # Mock exec_command return values
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b"hello world"
        mock_stderr.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        client = SSHClient("localhost", "user", "pass")
        client.connect()
        status, out, err = client.execute_command("echo hello world")
        
        assert status == 0
        assert out == "hello world"
        assert err == ""
        mock_ssh.connect.assert_called_once()
        mock_ssh.exec_command.assert_called_once_with("echo hello world")

def test_tcp_client_mock():
    """Test TCPClient interactions with socket."""
    with patch('socket.socket') as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        
        client = TCPClient("127.0.0.1", 8080)
        client.connect()
        mock_sock.connect.assert_called_once_with(("127.0.0.1", 8080))
        
        client.send(b"data")
        mock_sock.sendall.assert_called_once_with(b"data")
        
        client.close()
        mock_sock.close.assert_called_once()

def test_udp_client_mock():
    """Test UDPClient interactions with socket."""
    with patch('socket.socket') as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        
        client = UDPClient("127.0.0.1", 9090)
        client.send(b"pulse")
        mock_sock.sendto.assert_called_once_with(b"pulse", ("127.0.0.1", 9090))

def test_port_scanner():
    """Test PortScanner logic with socket mocks."""
    with patch('socket.socket') as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value.__enter__.return_value = mock_sock
        
        # Test success
        mock_sock.connect.return_value = None
        assert PortScanner.is_port_open("localhost", 80) is True
        
        # Test failure
        mock_sock.connect.side_effect = ConnectionRefusedError()
        assert PortScanner.is_port_open("localhost", 81) is False
