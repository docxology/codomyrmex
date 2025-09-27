"""Sensor integration and device management."""

from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import json
import math
import logging

logger = logging.getLogger(__name__)


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
            "metadata": self.metadata,
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
            self.readings = self.readings[-self.max_readings :]

        # Trigger callbacks
        sensor_type_key = reading.sensor_type.value
        if sensor_type_key in self._callbacks:
            for callback in self._callbacks[sensor_type_key]:
                try:
                    callback(reading)
                except Exception as e:
                    logger.error(f"Callback error: {e}")

    def get_latest_reading(self, sensor_type: SensorType) -> Optional[SensorReading]:
        """Get the latest reading for a sensor type."""
        for reading in reversed(self.readings):
            if reading.sensor_type == sensor_type:
                return reading
        return None

    def get_readings_by_type(
        self,
        sensor_type: SensorType,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> List[SensorReading]:
        """Get readings for a sensor type within time range."""
        filtered_readings = []

        for reading in self.readings:
            if reading.sensor_type == sensor_type:
                if start_time is None or reading.timestamp >= start_time:
                    if end_time is None or reading.timestamp <= end_time:
                        filtered_readings.append(reading)

        return filtered_readings

    def subscribe_to_sensor(
        self, sensor_type: SensorType, callback: Callable[[SensorReading], None]
    ) -> None:
        """Subscribe to sensor readings."""
        sensor_key = sensor_type.value
        if sensor_key not in self._callbacks:
            self._callbacks[sensor_key] = []
        self._callbacks[sensor_key].append(callback)

    def unsubscribe_from_sensor(
        self, sensor_type: SensorType, callback: Callable[[SensorReading], None]
    ) -> None:
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

    def export_readings(
        self, file_path: str, sensor_type: Optional[SensorType] = None
    ) -> None:
        """Export sensor readings to file."""
        readings_to_export = self.readings

        if sensor_type:
            readings_to_export = [
                r for r in readings_to_export if r.sensor_type == sensor_type
            ]

        data = {
            "readings": [r.to_dict() for r in readings_to_export],
            "exported_at": time.time(),
            "total_readings": len(readings_to_export),
        }

        with open(file_path, "w") as f:
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
            "last_reading": self.readings[-1].timestamp if self.readings else None,
        }

    def calibrate_sensor(
        self,
        sensor_id: str,
        reference_values: List[Tuple[float, float]],
        sensor_type: SensorType,
    ) -> Dict[str, float]:
        """
        Calibrate a sensor using reference values.
        reference_values: List of (sensor_reading, actual_value) tuples
        Returns calibration coefficients: {'slope': float, 'offset': float}
        """
        if len(reference_values) < 2:
            raise ValueError("At least 2 reference points needed for calibration")

        # Linear regression for calibration
        x_values = [point[0] for point in reference_values]  # sensor readings
        y_values = [point[1] for point in reference_values]  # actual values

        n = len(reference_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in reference_values)
        sum_xx = sum(x * x for x in x_values)

        # Calculate slope and intercept
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        offset = (sum_y - slope * sum_x) / n

        calibration = {"slope": slope, "offset": offset}

        # Store calibration for this sensor
        if not hasattr(self, "_calibrations"):
            self._calibrations = {}
        self._calibrations[sensor_id] = calibration

        logger.info(
            f"Calibrated sensor {sensor_id}: slope={slope:.4f}, offset={offset:.4f}"
        )
        return calibration

    def apply_calibration(self, reading: SensorReading) -> SensorReading:
        """Apply calibration to a sensor reading if available."""
        if hasattr(self, "_calibrations") and reading.sensor_id in self._calibrations:
            cal = self._calibrations[reading.sensor_id]
            calibrated_value = reading.value * cal["slope"] + cal["offset"]

            # Create new reading with calibrated value
            return SensorReading(
                sensor_id=reading.sensor_id,
                sensor_type=reading.sensor_type,
                value=calibrated_value,
                unit=reading.unit,
                timestamp=reading.timestamp,
                metadata={
                    **reading.metadata,
                    "calibrated": True,
                    "raw_value": reading.value,
                },
            )
        return reading

    def get_sensor_health(
        self, sensor_id: str, time_window: float = 3600
    ) -> Dict[str, Any]:
        """Analyze sensor health based on recent readings."""
        current_time = time.time()
        cutoff_time = current_time - time_window

        # Get recent readings for this sensor
        recent_readings = [
            r
            for r in self.readings
            if r.sensor_id == sensor_id and r.timestamp >= cutoff_time
        ]

        if not recent_readings:
            return {"status": "no_data", "readings_count": 0}

        values = [r.value for r in recent_readings]

        # Calculate statistics
        mean_value = sum(values) / len(values)
        variance = sum((v - mean_value) ** 2 for v in values) / len(values)
        std_dev = math.sqrt(variance)

        # Check for anomalies (values beyond 3 standard deviations)
        anomalies = [v for v in values if abs(v - mean_value) > 3 * std_dev]

        # Check reading frequency
        time_diffs = []
        for i in range(1, len(recent_readings)):
            time_diffs.append(
                recent_readings[i].timestamp - recent_readings[i - 1].timestamp
            )

        avg_interval = sum(time_diffs) / len(time_diffs) if time_diffs else 0

        return {
            "status": "healthy" if len(anomalies) < len(values) * 0.1 else "degraded",
            "readings_count": len(recent_readings),
            "mean_value": mean_value,
            "std_deviation": std_dev,
            "anomalies_count": len(anomalies),
            "average_interval": avg_interval,
            "last_reading": recent_readings[-1].timestamp,
        }

    def detect_sensor_drift(
        self,
        sensor_id: str,
        baseline_period: float = 86400,
        comparison_period: float = 3600,
    ) -> Dict[str, Any]:
        """Detect if a sensor has drifted from its baseline."""
        current_time = time.time()

        # Get baseline readings (older period)
        baseline_start = current_time - baseline_period - comparison_period
        baseline_end = current_time - comparison_period

        baseline_readings = [
            r
            for r in self.readings
            if (
                r.sensor_id == sensor_id
                and baseline_start <= r.timestamp <= baseline_end
            )
        ]

        # Get recent readings
        recent_readings = [
            r
            for r in self.readings
            if (
                r.sensor_id == sensor_id
                and r.timestamp >= current_time - comparison_period
            )
        ]

        if len(baseline_readings) < 10 or len(recent_readings) < 10:
            return {"status": "insufficient_data"}

        baseline_mean = sum(r.value for r in baseline_readings) / len(baseline_readings)
        recent_mean = sum(r.value for r in recent_readings) / len(recent_readings)

        drift_amount = recent_mean - baseline_mean
        drift_percentage = (
            (drift_amount / baseline_mean * 100) if baseline_mean != 0 else 0
        )

        # Classify drift severity
        if abs(drift_percentage) < 1:
            status = "stable"
        elif abs(drift_percentage) < 5:
            status = "minor_drift"
        elif abs(drift_percentage) < 15:
            status = "moderate_drift"
        else:
            status = "significant_drift"

        return {
            "status": status,
            "drift_amount": drift_amount,
            "drift_percentage": drift_percentage,
            "baseline_mean": baseline_mean,
            "recent_mean": recent_mean,
            "baseline_readings": len(baseline_readings),
            "recent_readings": len(recent_readings),
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
        return (celsius * 9 / 5) + 32

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
    def cartesian_to_spherical(
        x: float, y: float, z: float
    ) -> Tuple[float, float, float]:
        """Convert Cartesian to spherical coordinates."""
        r = math.sqrt(x**2 + y**2 + z**2)
        theta = math.acos(z / r) if r != 0 else 0
        phi = math.atan2(y, x)
        return r, theta, phi

    @staticmethod
    def spherical_to_cartesian(
        r: float, theta: float, phi: float
    ) -> Tuple[float, float, float]:
        """Convert spherical to Cartesian coordinates."""
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.sin(theta) * math.sin(phi)
        z = r * math.cos(theta)
        return x, y, z


__all__ = [
    "SensorType",
    "DeviceStatus",
    "SensorReading",
    "DeviceInterface",
    "SensorManager",
    "PhysicalConstants",
    "UnitConverter",
    "CoordinateSystem",
]
