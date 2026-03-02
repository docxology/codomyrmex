"""Base classes for sensor interfaces."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SensorData:
    """Base class for sensor data samples."""

    sensor_id: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)
    data: Any = None


class SensorInterface(ABC):
    """Abstract base class for all sensors."""

    def __init__(self, sensor_id: str) -> None:
        self.sensor_id = sensor_id
        self._is_connected = False

    @property
    def is_connected(self) -> bool:
        """Return True if the sensor is connected and ready."""
        return self._is_connected

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the physical or simulated sensor."""

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the sensor."""

    @abstractmethod
    def read(self) -> SensorData:
        """Read a single sample from the sensor."""


class MockSensor(SensorInterface):
    """A generic mock sensor for testing without hardware."""

    def __init__(self, sensor_id: str, default_value: float = 0.0) -> None:
        super().__init__(sensor_id)
        self.value = default_value

    def connect(self) -> bool:
        self._is_connected = True
        return True

    def disconnect(self) -> None:
        self._is_connected = False

    def read(self) -> SensorData:
        if not self.is_connected:
            raise RuntimeError(f"Sensor {self.sensor_id} is not connected.")
        return SensorData(
            sensor_id=self.sensor_id,
            data={"value": self.value},
            metadata={"type": "mock"},
        )
