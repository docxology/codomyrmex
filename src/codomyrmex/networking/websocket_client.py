from typing import Optional, Union

import websocket

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger






"""
WebSocket client implementation.
"""



logger = get_logger(__name__)

try:
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


class NetworkingError(CodomyrmexError):
    """Raised when networking operations fail."""

    pass


class WebSocketClient:
    """WebSocket client for real-time communication."""

    def __init__(self, url: str):
        """Initialize WebSocket client.

        Args:
            url: WebSocket URL
        """
        if not WEBSOCKET_AVAILABLE:
            raise ImportError("websocket-client package not available. Install with: pip install websocket-client")

        self.url = url
        self.ws: Optional[websocket.WebSocket] = None
        self.connected = False

    def connect(self) -> bool:
        """Connect to WebSocket server.

        Returns:
            True if connection successful
        """
        try:
            self.ws = websocket.create_connection(self.url)
            self.connected = True
            logger.info(f"Connected to WebSocket: {self.url}")
            return True
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            self.connected = False
            return False

    def send(self, message: Union[str, bytes]) -> bool:
        """Send a message over WebSocket.

        Args:
            message: Message to send

        Returns:
            True if send successful
        """
        if not self.connected or self.ws is None:
            raise NetworkingError("WebSocket not connected")

        try:
            if isinstance(message, str):
                self.ws.send(message)
            else:
                self.ws.send_binary(message)
            return True
        except Exception as e:
            logger.error(f"WebSocket send failed: {e}")
            raise NetworkingError(f"Failed to send message: {str(e)}") from e

    def receive(self) -> Optional[Union[str, bytes]]:
        """Receive a message from WebSocket.

        Returns:
            Received message, None if connection closed
        """
        if not self.connected or self.ws is None:
            raise NetworkingError("WebSocket not connected")

        try:
            message = self.ws.recv()
            return message
        except Exception as e:
            logger.error(f"WebSocket receive failed: {e}")
            self.connected = False
            return None

    def close(self) -> None:
        """Close WebSocket connection."""
        if self.ws is not None:
            try:
                self.ws.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
            finally:
                self.ws = None
                self.connected = False


