"""Generator content."""

def generate_sensor_integration_content() -> str:
    """Generate sensor integration module."""
    return '''"""Sensor integration and device management."""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import time
import json


class SensorType(Enum):
    """Types of sensors supported."""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    MOTION = "motion"
    LIGHT = "light"
    PROXIMITY = "proximity"
    GPS = "gps"
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    MAGNETOMETER = "magnetometer"


class DeviceStatus(Enum):
    """Device connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class SensorReading:
    """Represents a sensor reading."""
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type.value,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class DeviceInterface:
    """Interface for connected devices."""
    device_id: str
    device_type: str
    sensors: List[SensorType]
    status: DeviceStatus = DeviceStatus.UNKNOWN
    last_seen: float = field(default_factory=time.time)
    capabilities: Dict[str, Any] = field(default_factory=dict)


class SensorManager:
    """Manages sensor data collection and device integration."""

    def __init__(self):
        self.devices: Dict[str, DeviceInterface] = {}
        self.readings: List[SensorReading] = []
        self._callbacks: Dict[str, List[Callable]] = {}
        self.max_readings = 10000  # Keep last N readings

    def register_device(self, device: DeviceInterface) -> None:
        """Register a new device."""
        self.devices[device.device_id] = device
        logger.info(f"Registered device: {device.device_id}")

    def unregister_device(self, device_id: str) -> Optional[DeviceInterface]:
        """Unregister a device."""
        return self.devices.pop(device_id, None)

    def add_reading(self, reading: SensorReading) -> None:
        """Add a sensor reading."""
        self.readings.append(reading)

        # Keep only recent readings
        if len(self.readings) > self.max_readings:
            self.readings = self.readings[-self.max_readings:]

        # Trigger callbacks
        sensor_type_key = reading.sensor_type.value
        if sensor_type_key in self._callbacks:
            for callback in self._callbacks[sensor_type_key]:
                try:
                    callback(reading)
                except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                    logger.error(f"Callback error: {e}")

    def get_latest_reading(self, sensor_type: SensorType) -> Optional[SensorReading]:
        """Get the latest reading for a sensor type."""
        for reading in reversed(self.readings):
            if reading.sensor_type == sensor_type:
                return reading
        return None

    def get_readings_by_type(self, sensor_type: SensorType,
                           start_time: Optional[float] = None,
                           end_time: Optional[float] = None) -> List[SensorReading]:
                               pass
        """Get readings for a sensor type within time range."""
        filtered_readings = []

        for reading in self.readings:
            if reading.sensor_type == sensor_type:
                if start_time is None or reading.timestamp >= start_time:
                    if end_time is None or reading.timestamp <= end_time:
                        filtered_readings.append(reading)

        return filtered_readings

    def subscribe_to_sensor(self, sensor_type: SensorType, callback: Callable[[SensorReading], None]) -> None:
        """Subscribe to sensor readings."""
        sensor_key = sensor_type.value
        if sensor_key not in self._callbacks:
            self._callbacks[sensor_key] = []
        self._callbacks[sensor_key].append(callback)

    def unsubscribe_from_sensor(self, sensor_type: SensorType, callback: Callable[[SensorReading], None]) -> None:
        """Unsubscribe from sensor readings."""
        sensor_key = sensor_type.value
        if sensor_key in self._callbacks:
            try:
                self._callbacks[sensor_key].remove(callback)
            except ValueError:
                pass

    def get_device_status(self, device_id: str) -> Optional[DeviceStatus]:
        """Get device connection status."""
        device = self.devices.get(device_id)
        return device.status if device else None

    def update_device_status(self, device_id: str, status: DeviceStatus) -> bool:
        """Update device status."""
        if device_id in self.devices:
            self.devices[device_id].status = status
            self.devices[device_id].last_seen = time.time()
            return True
        return False

    def export_readings(self, file_path: str, sensor_type: Optional[SensorType] = None) -> None:
        """Export sensor readings to file."""
        readings_to_export = self.readings

        if sensor_type:
            readings_to_export = [r for r in readings_to_export if r.sensor_type == sensor_type]

        data = {
            "readings": [r.to_dict() for r in readings_to_export],
            "exported_at": time.time(),
            "total_readings": len(readings_to_export)
        }

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_statistics(self) -> Dict[str, Any]:
        """Get sensor system statistics."""
        sensor_counts = {}
        for reading in self.readings:
            sensor_type = reading.sensor_type.value
            sensor_counts[sensor_type] = sensor_counts.get(sensor_type, 0) + 1

        device_counts = {}
        for device in self.devices.values():
            status = device.status.value
            device_counts[status] = device_counts.get(status, 0) + 1

        return {
            "total_devices": len(self.devices),
            "total_readings": len(self.readings),
            "readings_by_sensor": sensor_counts,
            "devices_by_status": device_counts,
            "last_reading": self.readings[-1].timestamp if self.readings else None
        }


# Utility classes
class PhysicalConstants:
    """Physical constants for calculations."""

    GRAVITY = 9.81  # m/s²
    EARTH_RADIUS = 6371000  # meters
    SPEED_OF_LIGHT = 299792458  # m/s


class UnitConverter:
    """Utility for unit conversions."""

    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9/5) + 32

    @staticmethod
    def meters_to_feet(meters: float) -> float:
        """Convert meters to feet."""
        return meters * 3.28084

    @staticmethod
    def pascals_to_psi(pascals: float) -> float:
        """Convert Pascals to PSI."""
        return pascals * 0.000145038


class CoordinateSystem:
    """Coordinate system utilities."""

    @staticmethod
    def cartesian_to_spherical(x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Convert Cartesian to spherical coordinates."""
        r = math.sqrt(x**2 + y**2 + z**2)
        theta = math.acos(z / r) if r != 0 else 0
        phi = math.atan2(y, x)
        return r, theta, phi

    @staticmethod
    def spherical_to_cartesian(r: float, theta: float, phi: float) -> Tuple[float, float, float]:
        """Convert spherical to Cartesian coordinates."""
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        return x, y, z


__all__ = [
    "SensorType", "DeviceStatus", "SensorReading", "DeviceInterface",
    "SensorManager", "PhysicalConstants", "UnitConverter", "CoordinateSystem"
]
'''

