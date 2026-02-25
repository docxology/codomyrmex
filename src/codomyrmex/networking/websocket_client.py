"""WebSocket client implementation.

This module provides a robust WebSocket client wrapper with reconnection logic,
message handling, and error recovery.
"""

import asyncio
import json
from collections.abc import Callable
from typing import Any

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class WebSocketError(CodomyrmexError):
    """Raised when WebSocket operations fail."""
    pass


class WebSocketClient:
    """WebSocket client with automatic reconnection."""

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        reconnect_interval: float = 1.0,
        max_reconnect_delay: float = 30.0,
    ):
        """Initialize WebSocket client.

        Args:
            url: WebSocket URL
            headers: Headers for handshake
            reconnect_interval: Initial reconnection delay
            max_reconnect_delay: Maximum reconnection delay
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets package not available. Install with: pip install websockets")

        self.url = url
        self.headers = headers or {}
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_delay = max_reconnect_delay
        self.connection = None
        self._running = False
        self._handlers = []

    async def connect(self):
        """Connect to WebSocket server with retry loop."""
        self._running = True
        delay = self.reconnect_interval

        while self._running:
            try:
                logger.info(f"Connecting to {self.url}...")
                async with websockets.connect(self.url, extra_headers=self.headers) as websocket:
                    self.connection = websocket
                    logger.info("WebSocket connected")
                    delay = self.reconnect_interval  # Reset delay on success

                    # Process messages
                    async for message in websocket:
                        await self._handle_message(message)

            except (OSError, websockets.exceptions.WebSocketException) as e:
                logger.warning(f"WebSocket connection failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected WebSocket error: {e}")
            finally:
                self.connection = None

            if self._running:
                logger.info(f"Reconnecting in {delay}s...")
                await asyncio.sleep(delay)
                delay = min(delay * 1.5, self.max_reconnect_delay)

    async def send(self, message: str | bytes | dict):
        """Send a message."""
        if not self.connection or self.connection.closed:
            raise WebSocketError("Not connected")

        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            await self.connection.send(message)
        except Exception as e:
            raise WebSocketError(f"Failed to send message: {e}") from e

    async def close(self):
        """Close connection."""
        self._running = False
        if self.connection:
            await self.connection.close()

    def on(self, handler: Callable[[Any], Any]):
        """Add a message handler. Alias for event system consistency."""
        self._handlers.append(handler)

    async def _handle_message(self, message: str | bytes):
        """Dispatch message to handlers."""
        # Try to parse JSON
        data = message
        if isinstance(message, str):
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                pass

        for handler in self._handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
