from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SensorPayload:
    node_id: str
    timestamp: float
    sensor_type: str
    readings: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def parse_payload(cls, raw: str) -> SensorPayload:
        try:
            data = json.loads(raw)
            return cls(
                node_id=str(data["node_id"]),
                timestamp=float(data["timestamp"]),
                sensor_type=str(data["sensor_type"]),
                readings=dict(data["readings"]),
                metadata=dict(data.get("metadata", {})),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid sensor payload") from exc


class TelemetryStream:
    def __init__(self) -> None:
        self._payloads_by_node: dict[str, list[SensorPayload]] = {}

    def ingest(self, payload: SensorPayload) -> None:
        self._payloads_by_node.setdefault(payload.node_id, []).append(payload)

    def get_latest(self, node_id: str) -> SensorPayload | None:
        payloads = self._payloads_by_node.get(node_id, [])
        return payloads[-1] if payloads else None
