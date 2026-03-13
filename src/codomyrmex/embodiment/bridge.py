"""Physical Embodiment WebSocket Bridge.

Relays hardware telemetry streams (sensors) and operational
commands (actuators) between physical robotics/IoT nodes and the
Codomyrmex agent networks.
"""

import json
import logging
from collections.abc import Callable
from typing import Any

# Use external optional if available, else gracefully fallback for pure mockless IO
try:
    import websockets
except ImportError:
    websockets = None  # type: ignore

from .telemetry import SensorPayload, TelemetryStream

logger = logging.getLogger(__name__)


class EmbodimentBridge:
    """Async WebSocket server wrapping agent-to-hardware communication endpoints."""

    def __init__(self) -> None:
        """Initialize telemetry state management and websocket client connections."""
        self.stream = TelemetryStream()
        # Maps node_id -> websockets.WebSocketServerProtocol
        self._connected_nodes: dict[str, Any] = {}
        # Allows registering listeners on specific events
        self._subscribers: list[Callable[[SensorPayload], None]] = []

    def subscribe(self, callback: Callable[[SensorPayload], None]) -> None:
        """Subscribe a callback function to all freshly ingested sensor payloads."""
        self._subscribers.append(callback)

    async def _handler(self, websocket: Any, *args: Any, **kwargs: Any) -> None:
        """Handle individual websocket stream connections."""
        node_id = None
        try:
            # Wait for specific init/handshake packet identifying the node
            init_msg = await websocket.recv()
            init_data = json.loads(init_msg)
            node_id = init_data.get("node_id")

            if not node_id:
                await websocket.close(1008, "Missing node_id in handshake")
                return

            self._connected_nodes[node_id] = websocket
            logger.info(f"Hardware node connected: {node_id}")

            async for message in websocket:
                try:
                    payload = SensorPayload.parse_payload(message)
                    self.stream.ingest(payload)
                    for sub in self._subscribers:
                        sub(payload)
                except ValueError as e:
                    logger.warning(f"Failed to parse payload from {node_id}: {e}")

        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            if node_id and node_id in self._connected_nodes:
                del self._connected_nodes[node_id]
                logger.info(f"Hardware node disconnected: {node_id}")

    async def start_server(self, host: str = "127.0.0.1", port: int = 8765) -> Any:
        """Bind and start the async WebSocket ingress server."""
        if websockets is None:
            raise ImportError(
                "websockets package is required for EmbodimentBridge. "
                "Install with `pip install websockets` or `uv sync --all-extras`."
            )

        # Start the websockets server
        server = await websockets.serve(self._handler, host, port)
        logger.info(f"Embodiment bridge listening on ws://{host}:{port}")
        return server

    async def send_command(self, node_id: str, command: dict[str, Any]) -> bool:
        """Send structural JSON actuation instructions to a specific node."""
        if node_id not in self._connected_nodes:
            logger.error(f"Cannot send command: Node {node_id} is not connected.")
            return False

        try:
            websocket = self._connected_nodes[node_id]
            cmd_json = json.dumps(command)
            await websocket.send(cmd_json)
            return True
        except Exception as e:
            logger.error(f"Failed to send command to {node_id}: {e}")
            return False
