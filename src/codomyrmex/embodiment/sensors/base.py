from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass
class SensorData:
    sensor_id: str
    timestamp: float = field(default_factory=time)
    data: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


class SimulatedSensor:
    def __init__(self, sensor_id: str, default_value: Any = None) -> None:
        self.sensor_id = sensor_id
        self.default_value = default_value
        self.is_connected = False

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def disconnect(self) -> None:
        self.is_connected = False

    def read(self) -> SensorData:
        return SensorData(
            sensor_id=self.sensor_id,
            data={"value": self.default_value},
            metadata={"type": "simulated"},
        )


class MockSensor(SimulatedSensor):
    def read(self) -> SensorData:
        reading = super().read()
        reading.metadata["type"] = "mock"
        return reading
