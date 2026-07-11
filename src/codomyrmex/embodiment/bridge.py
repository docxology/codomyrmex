from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from .telemetry import SensorPayload, TelemetryStream


class EmbodimentBridge:
    def __init__(self) -> None:
        self.stream = TelemetryStream()
        self._subscribers: list[Callable[[SensorPayload], None]] = []
        self._connected_nodes: dict[str, Any] = {}

    def subscribe(self, callback: Callable[[SensorPayload], None]) -> None:
        self._subscribers.append(callback)

    async def start_server(self, host: str = "127.0.0.1", port: int = 8765) -> Any:
        import websockets

        return await websockets.serve(self._handle_connection, host, port)

    async def send_command(self, node_id: str, command: dict[str, Any]) -> bool:
        websocket = self._connected_nodes.get(node_id)
        if websocket is None:
            return False
        await websocket.send(json.dumps(command))
        return True

    async def _handle_connection(self, websocket: Any, path: str | None = None) -> None:
        handshake = json.loads(await websocket.recv())
        node_id = str(handshake["node_id"])
        self._connected_nodes[node_id] = websocket
        try:
            async for message in websocket:
                payload = SensorPayload.parse_payload(message)
                self.stream.ingest(payload)
                for callback in list(self._subscribers):
                    callback(payload)
        finally:
            self._connected_nodes.pop(node_id, None)
