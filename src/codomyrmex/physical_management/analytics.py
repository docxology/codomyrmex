from collections import defaultdict, deque
from typing import Any, Callable, Optional
import json
import logging
import time

from dataclasses import dataclass, field
from enum import Enum
import statistics
import threading







"""Advanced analytics and data streaming for physical management."""


logger = logging.getLogger(__name__)


class AnalyticsMetric(Enum):
    """Types of analytics metrics."""

    MEAN = "mean"
    MEDIAN = "median"
    STD_DEV = "std_dev"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    RATE = "rate"
    PERCENTILE_95 = "percentile_95"
    PERCENTILE_99 = "percentile_99"


class StreamingMode(Enum):
    """Streaming modes for data processing."""

    REAL_TIME = "real_time"
    BATCH = "batch"
    WINDOWED = "windowed"
    TRIGGERED = "triggered"


@dataclass
class DataPoint:
    """A single data point in a stream."""

    timestamp: float
    value: float
    source_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsWindow:
    """Time window for analytics calculations."""

    start_time: float
    end_time: float
    duration: float
    data_points: list[DataPoint] = field(default_factory=list)

    def add_point(self, point: DataPoint) -> None:
        """Add a data point to the window."""
        if self.start_time <= point.timestamp <= self.end_time:
            self.data_points.append(point)

    def is_complete(self) -> bool:
        """Check if window is complete (past end time)."""
        return time.time() > self.end_time

    def calculate_metrics(self) -> dict[AnalyticsMetric, float]:
        """Calculate analytics metrics for the window."""
        if not self.data_points:
            return {}

        values = [p.value for p in self.data_points]
        metrics = {}

        try:
            metrics[AnalyticsMetric.MEAN] = statistics.mean(values)
            metrics[AnalyticsMetric.MEDIAN] = statistics.median(values)
            metrics[AnalyticsMetric.MIN] = min(values)
            metrics[AnalyticsMetric.MAX] = max(values)
            metrics[AnalyticsMetric.COUNT] = len(values)
            metrics[AnalyticsMetric.RATE] = (
                len(values) / self.duration if self.duration > 0 else 0
            )

            if len(values) > 1:
                metrics[AnalyticsMetric.STD_DEV] = statistics.stdev(values)

                # Calculate percentiles
                sorted_values = sorted(values)
                p95_idx = int(0.95 * len(sorted_values))
                p99_idx = int(0.99 * len(sorted_values))
                metrics[AnalyticsMetric.PERCENTILE_95] = sorted_values[
                    min(p95_idx, len(sorted_values) - 1)
                ]
                metrics[AnalyticsMetric.PERCENTILE_99] = sorted_values[
                    min(p99_idx, len(sorted_values) - 1)
                ]

        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")

        return metrics


class DataStream:
    """Real-time data stream with analytics capabilities."""

    def __init__(
        self, stream_id: str, buffer_size: int = 10000, window_duration: float = 60.0
    ):
        """Initialize DataStream.

        Args:
            stream_id: Unique identifier.
            buffer_size: Parameter for the operation.
            window_duration: Parameter for the operation.
        """
        self.stream_id = stream_id
        self.buffer_size = buffer_size
        self.window_duration = window_duration

        self.data_buffer = deque(maxlen=buffer_size)
        self.subscribers: list[Callable[[DataPoint], None]] = []
        self.windows: list[AnalyticsWindow] = []
        self.completed_windows: list[AnalyticsWindow] = []
        self.max_completed_windows = 1000

        self._lock = threading.RLock()
        self._stats = defaultdict(float)

        # Auto-create initial window
        self._create_new_window()

    def add_data_point(
        self, value: float, source_id: str, metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """Add a new data point to the stream."""
        point = DataPoint(
            timestamp=time.time(),
            value=value,
            source_id=source_id,
            metadata=metadata or {},
        )

        with self._lock:
            self.data_buffer.append(point)

            # Add to current windows
            for window in self.windows[:]:
                window.add_point(point)

                # Check if window is complete
                if window.is_complete():
                    self.windows.remove(window)
                    self.completed_windows.append(window)

                    # Limit completed windows
                    if len(self.completed_windows) > self.max_completed_windows:
                        self.completed_windows = self.completed_windows[
                            -self.max_completed_windows :
                        ]

            # Create new window if needed
            if not self.windows:
                self._create_new_window()

            # Update running statistics
            self._update_stats(point)

        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(point)
            except Exception as e:
                logger.error(f"Error in stream subscriber: {e}")

    def subscribe(self, callback: Callable[[DataPoint], None]) -> None:
        """Subscribe to stream updates."""
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[DataPoint], None]) -> bool:
        """Unsubscribe from stream updates."""
        try:
            self.subscribers.remove(callback)
            return True
        except ValueError:
            return False

    def get_recent_data(self, duration: float) -> list[DataPoint]:
        """Get data points from the last N seconds."""
        cutoff_time = time.time() - duration
        with self._lock:
            return [p for p in self.data_buffer if p.timestamp >= cutoff_time]

    def get_current_metrics(self) -> dict[AnalyticsMetric, float]:
        """Get current window metrics."""
        with self._lock:
            if self.windows:
                return self.windows[0].calculate_metrics()
            return {}

    def get_historical_metrics(
        self, num_windows: int = 10
    ) -> list[dict[AnalyticsMetric, float]]:
        """Get metrics from completed windows."""
        with self._lock:
            recent_windows = self.completed_windows[-num_windows:]
            return [window.calculate_metrics() for window in recent_windows]

    def get_stream_statistics(self) -> dict[str, Any]:
        """Get overall stream statistics."""
        with self._lock:
            return {
                "total_points": len(self.data_buffer),
                "current_windows": len(self.windows),
                "completed_windows": len(self.completed_windows),
                "subscribers": len(self.subscribers),
                "window_duration": self.window_duration,
                "buffer_utilization": len(self.data_buffer) / self.buffer_size,
                "average_rate": self._stats.get("rate", 0),
                "latest_value": (
                    self.data_buffer[-1].value if self.data_buffer else None
                ),
                "latest_timestamp": (
                    self.data_buffer[-1].timestamp if self.data_buffer else None
                ),
            }

    def _create_new_window(self) -> None:
        """Create a new analytics window."""
        now = time.time()
        window = AnalyticsWindow(
            start_time=now,
            end_time=now + self.window_duration,
            duration=self.window_duration,
        )
        self.windows.append(window)

    def _update_stats(self, point: DataPoint) -> None:
        """Update running statistics."""
        # Simple rate calculation (points per second over last minute)
        recent_points = self.get_recent_data(60.0)
        self._stats["rate"] = len(recent_points) / 60.0


class StreamingAnalytics:
    """Central streaming analytics manager."""

    def __init__(self):
        """  Init  .
            """
        self.streams: dict[str, DataStream] = {}
        self.processors: list[Callable[[str, DataPoint], None]] = []
        self.alerts: list[dict[str, Any]] = []
        self.max_alerts = 1000
        self._lock = threading.RLock()

    def create_stream(
        self, stream_id: str, buffer_size: int = 10000, window_duration: float = 60.0
    ) -> DataStream:
        """Create a new data stream."""
        with self._lock:
            if stream_id in self.streams:
                raise ValueError(f"Stream {stream_id} already exists")

            stream = DataStream(stream_id, buffer_size, window_duration)
            self.streams[stream_id] = stream

            # Subscribe to stream updates for processing
            stream.subscribe(lambda point: self._process_data_point(stream_id, point))

            return stream

    def get_stream(self, stream_id: str) -> Optional[DataStream]:
        """Get a stream by ID."""
        return self.streams.get(stream_id)

    def delete_stream(self, stream_id: str) -> bool:
        """Delete a stream."""
        with self._lock:
            if stream_id in self.streams:
                del self.streams[stream_id]
                return True
            return False

    def add_data(
        self,
        stream_id: str,
        value: float,
        source_id: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Add data to a stream."""
        stream = self.get_stream(stream_id)
        if stream:
            stream.add_data_point(value, source_id, metadata)
            return True
        return False

    def add_processor(self, processor: Callable[[str, DataPoint], None]) -> None:
        """Add a data processor that runs on all streams."""
        self.processors.append(processor)

    def remove_processor(self, processor: Callable[[str, DataPoint], None]) -> bool:
        """Remove a data processor."""
        try:
            self.processors.remove(processor)
            return True
        except ValueError:
            return False

    def create_alert(
        self, stream_id: str, condition: str, threshold: float, message: str
    ) -> None:
        """Create an alert condition."""
        alert = {
            "stream_id": stream_id,
            "condition": condition,  # "above", "below", "equal", "rate_above", etc.
            "threshold": threshold,
            "message": message,
            "created": time.time(),
            "active": True,
        }

        with self._lock:
            self.alerts.append(alert)

            # Limit alerts
            if len(self.alerts) > self.max_alerts:
                self.alerts = self.alerts[-self.max_alerts :]

    def check_alerts(self, stream_id: str, point: DataPoint) -> list[dict[str, Any]]:
        """Check alert conditions for a data point."""
        triggered_alerts = []

        for alert in self.alerts:
            if not alert.get("active", True) or alert["stream_id"] != stream_id:
                continue

            condition = alert["condition"]
            threshold = alert["threshold"]
            triggered = False

            if condition == "above" and point.value > threshold:
                triggered = True
            elif condition == "below" and point.value < threshold:
                triggered = True
            elif condition == "equal" and abs(point.value - threshold) < 1e-10:
                triggered = True
            # Add more conditions as needed

            if triggered:
                triggered_alert = alert.copy()
                triggered_alert["triggered_time"] = point.timestamp
                triggered_alert["triggered_value"] = point.value
                triggered_alerts.append(triggered_alert)

        return triggered_alerts

    def get_analytics_summary(self) -> dict[str, Any]:
        """Get summary of all analytics."""
        with self._lock:
            summary = {
                "total_streams": len(self.streams),
                "total_processors": len(self.processors),
                "total_alerts": len(self.alerts),
                "streams": {},
            }

            for stream_id, stream in self.streams.items():
                summary["streams"][stream_id] = stream.get_stream_statistics()

            return summary

    def export_stream_data(self, stream_id: str, format: str = "json") -> Optional[str]:
        """Export stream data in specified format."""
        stream = self.get_stream(stream_id)
        if not stream:
            return None

        with stream._lock:
            data = {
                "stream_id": stream_id,
                "exported_at": time.time(),
                "data_points": [
                    {
                        "timestamp": p.timestamp,
                        "value": p.value,
                        "source_id": p.source_id,
                        "metadata": p.metadata,
                    }
                    for p in stream.data_buffer
                ],
                "completed_windows": [
                    {
                        "start_time": w.start_time,
                        "end_time": w.end_time,
                        "duration": w.duration,
                        "metrics": w.calculate_metrics(),
                    }
                    for w in stream.completed_windows
                ],
            }

        if format == "json":
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _process_data_point(self, stream_id: str, point: DataPoint) -> None:
        """Process a data point through all processors."""
        # Run custom processors
        for processor in self.processors:
            try:
                processor(stream_id, point)
            except Exception as e:
                logger.error(f"Error in data processor: {e}")

        # Check alerts
        triggered_alerts = self.check_alerts(stream_id, point)
        for alert in triggered_alerts:
            logger.warning(
                f"Alert triggered: {alert['message']} (value: {point.value})"
            )


class PredictiveAnalytics:
    """Simple predictive analytics using statistical methods."""

    def __init__(self, min_data_points: int = 10):
        self.min_data_points = min_data_points

    def predict_linear_trend(
        self, data_points: list[DataPoint], future_seconds: float
    ) -> Optional[float]:
        """Predict future value using linear regression."""
        if len(data_points) < self.min_data_points:
            return None

        try:
            # Simple linear regression
            x_values = [p.timestamp for p in data_points]
            y_values = [p.value for p in data_points]

            n = len(data_points)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_xx = sum(x * x for x in x_values)

            # Calculate slope and intercept
            denominator = n * sum_xx - sum_x * sum_x
            if abs(denominator) < 1e-10:
                return None

            slope = (n * sum_xy - sum_x * sum_y) / denominator
            intercept = (sum_y - slope * sum_x) / n

            # Predict future value
            future_time = data_points[-1].timestamp + future_seconds
            predicted_value = slope * future_time + intercept

            return predicted_value

        except Exception as e:
            logger.error(f"Error in linear trend prediction: {e}")
            return None

    def detect_anomalies(
        self, data_points: list[DataPoint], std_dev_threshold: float = 3.0
    ) -> list[DataPoint]:
        """Detect anomalies using standard deviation method."""
        if len(data_points) < self.min_data_points:
            return []

        try:
            values = [p.value for p in data_points]
            mean_val = statistics.mean(values)
            std_dev = statistics.stdev(values)

            if std_dev == 0:
                return []

            anomalies = []
            for point in data_points:
                z_score = abs((point.value - mean_val) / std_dev)
                if z_score > std_dev_threshold:
                    anomalies.append(point)

            return anomalies

        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return []

    def calculate_correlation(
        self, stream1_data: list[DataPoint], stream2_data: list[DataPoint]
    ) -> Optional[float]:
        """Calculate correlation between two data streams."""
        if (
            len(stream1_data) < self.min_data_points
            or len(stream2_data) < self.min_data_points
        ):
            return None

        try:
            # Align data points by timestamp (simple approach)
            values1 = [p.value for p in stream1_data]
            values2 = [p.value for p in stream2_data]

            # Take minimum length
            min_len = min(len(values1), len(values2))
            values1 = values1[:min_len]
            values2 = values2[:min_len]

            if min_len < 2:
                return None

            # Calculate Pearson correlation coefficient
            mean1 = statistics.mean(values1)
            mean2 = statistics.mean(values2)

            numerator = sum(
                (v1 - mean1) * (v2 - mean2) for v1, v2 in zip(values1, values2)
            )
            sum_sq1 = sum((v1 - mean1) ** 2 for v1 in values1)
            sum_sq2 = sum((v2 - mean2) ** 2 for v2 in values2)

            denominator = (sum_sq1 * sum_sq2) ** 0.5

            if abs(denominator) < 1e-10:
                return None

            correlation = numerator / denominator
            return correlation

        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return None


__all__ = [
    "AnalyticsMetric",
    "StreamingMode",
    "DataPoint",
    "AnalyticsWindow",
    "DataStream",
    "StreamingAnalytics",
    "PredictiveAnalytics",
]
