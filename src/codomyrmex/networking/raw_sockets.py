"""TCP and UDP socket implementation."""

import socket
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class TCPClient:
    """Simple TCP client."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self) -> "TCPClient":
        """Support use as a context manager."""
        return self

    def __exit__(self, *args) -> None:
        """Close socket on context manager exit (prevents fd leaks)."""
        self.close()

    def connect(self) -> None:
        """Establish a connection to the target service."""
        self.sock.connect((self.host, self.port))

    def send(self, data: bytes) -> None:
        """Send the message or request."""
        self.sock.sendall(data)

    def receive(self, buffer_size: int = 1024) -> bytes:
        """Receive and return the response."""
        return self.sock.recv(buffer_size)

    def close(self) -> None:
        """Close the resource and release associated handles."""
        self.sock.close()

class TCPServer:
    """Simple TCP server."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self) -> None:
        """Start the operation or service."""
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        logger.info(f"TCP server listening on {self.host}:{self.port}")

    def accept(self):
        """Accept."""
        conn, addr = self.sock.accept()
        return conn, addr

    def close(self) -> None:
        """Close the resource and release associated handles."""
        self.sock.close()

class UDPClient:
    """Simple UDP client."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data: bytes) -> None:
        """Send the message or request."""
        self.sock.sendto(data, (self.host, self.port))

    def receive(self, buffer_size: int = 1024) -> tuple[bytes, Any]:
        """Receive and return the response."""
        return self.sock.recvfrom(buffer_size)

    def close(self) -> None:
        """Close the resource and release associated handles."""
        self.sock.close()

class PortScanner:
    """Utility for scanning open ports on a host."""

    @staticmethod
    def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if a single port is open."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            try:
                sock.connect((host, port))
                return True
            except (TimeoutError, OSError, ConnectionRefusedError) as e:
                logger.warning("Port %d on %s is not open: %s", port, host, e)
                return False

    @staticmethod
    def scan_range(host: str, start_port: int, end_port: int, timeout: float = 0.5) -> list[int]:
        """Scan a range of ports (synchronous)."""
        open_ports = []
        for port in range(start_port, end_port + 1):
            if PortScanner.is_port_open(host, port, timeout):
                open_ports.append(port)
        return open_ports
