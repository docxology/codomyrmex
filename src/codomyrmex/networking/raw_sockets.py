"""TCP and UDP socket implementation."""

import logging
import socket

logger = logging.getLogger(__name__)

class TCPClient:
    """Simple TCP client."""

    def __init__(self, host: str, port: int):
        """Execute   Init   operations natively."""
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self) -> None:
        """Execute Connect operations natively."""
        self.sock.connect((self.host, self.port))

    def send(self, data: bytes) -> None:
        """Execute Send operations natively."""
        self.sock.sendall(data)

    def receive(self, buffer_size: int = 1024) -> bytes:
        """Execute Receive operations natively."""
        return self.sock.recv(buffer_size)

    def close(self) -> None:
        """Execute Close operations natively."""
        self.sock.close()

class TCPServer:
    """Simple TCP server."""

    def __init__(self, host: str, port: int):
        """Execute   Init   operations natively."""
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self) -> None:
        """Execute Start operations natively."""
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        logger.info(f"TCP server listening on {self.host}:{self.port}")

    def accept(self):
        """Execute Accept operations natively."""
        conn, addr = self.sock.accept()
        return conn, addr

    def close(self) -> None:
        """Execute Close operations natively."""
        self.sock.close()

class UDPClient:
    """Simple UDP client."""

    def __init__(self, host: str, port: int):
        """Execute   Init   operations natively."""
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data: bytes) -> None:
        """Execute Send operations natively."""
        self.sock.sendto(data, (self.host, self.port))

    def receive(self, buffer_size: int = 1024) -> tuple[bytes, any]:
        """Execute Receive operations natively."""
        return self.sock.recvfrom(buffer_size)

    def close(self) -> None:
        """Execute Close operations natively."""
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
            except (socket.timeout, ConnectionRefusedError, socket.error):
                return False

    @staticmethod
    def scan_range(host: str, start_port: int, end_port: int, timeout: float = 0.5) -> list[int]:
        """Scan a range of ports (synchronous)."""
        open_ports = []
        for port in range(start_port, end_port + 1):
            if PortScanner.is_port_open(host, port, timeout):
                open_ports.append(port)
        return open_ports
