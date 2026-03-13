"""Physical embodiment telemetry mechanisms.

Provides standard structures for parsing raw JSON hardware state
into rigorous agent-parsable telemetry streams.
"""

import json
from dataclasses import dataclass
from typing import Any


@dataclass
class SensorPayload:
    """Standardized representation of an incoming hardware sensor telemetry tick."""

    node_id: str
    timestamp: float
    sensor_type: str
    readings: dict[str, float]
    metadata: dict[str, Any]

    @classmethod
    def parse_payload(cls, raw_json: str) -> "SensorPayload":
        """Parse raw JSON into a validated SensorPayload.

        Args:
            raw_json: String payload from the hardware endpoint.

        Returns:
            A populated SensorPayload object.

        Raises:
            ValueError: If the JSON is malformed or missing required keys.
        """
        try:
            data = json.loads(raw_json)
            return cls(
                node_id=data["node_id"],
                timestamp=float(data["timestamp"]),
                sensor_type=data["sensor_type"],
                readings={str(k): float(v) for k, v in data["readings"].items()},
                metadata=data.get("metadata", {}),
            )
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
            raise ValueError(f"Invalid sensor payload: {exc}") from exc


class TelemetryStream:
    """Manages the history and aggregation of localized sensor data streams."""

    def __init__(self) -> None:
        """Initialize the empty telemetry buffer."""
        # Maps node_id -> list of payloads
        self._buffer: dict[str, list[SensorPayload]] = {}

    def ingest(self, payload: SensorPayload) -> None:
        """Route a validated payload into the stream buffer."""
        if payload.node_id not in self._buffer:
            self._buffer[payload.node_id] = []
        self._buffer[payload.node_id].append(payload)

    def get_latest(self, node_id: str) -> SensorPayload | None:
        """Retrieve the most recent reading for a given hardware node."""
        if self._buffer.get(node_id):
            return self._buffer[node_id][-1]
        return None
