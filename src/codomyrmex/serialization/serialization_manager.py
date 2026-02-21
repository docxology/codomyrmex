"""Serialization manager — registry and orchestrator for multiple formats.

Manages named serializers, auto-detection by format, schema validation,
batch serialization, and serialization statistics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

from .serializer import Serializer, SerializationFormat

logger = get_logger(__name__)


@dataclass
class SerializationResult:
    """Result of a serialization operation."""

    format: str
    input_type: str
    output_size: int
    duration_seconds: float
    success: bool
    error: str = ""


class SerializationManager:
    """Manager for serialization operations with statistics and format detection.

    Example::

        mgr = SerializationManager()
        data = {"name": "test", "value": 42}
        serialized = mgr.serialize(data, format="json")
        deserialized = mgr.deserialize(serialized, format="json")
        assert deserialized == data
    """

    def __init__(self) -> None:
        self._serializers: dict[str, Serializer] = {}
        self._stats: list[SerializationResult] = []

    def get_serializer(self, format: str = "json") -> Serializer:
        """Get or create a serializer for a format.

        Args:
            format: Serialization format (json, yaml, toml, pickle, etc.)

        Returns:
            Serializer instance.
        """
        if format not in self._serializers:
            fmt = SerializationFormat(format) if format in [f.value for f in SerializationFormat] else SerializationFormat.JSON
            self._serializers[format] = Serializer(default_format=fmt)
        return self._serializers[format]

    def register_serializer(self, format: str, serializer: Serializer) -> None:
        """Register a custom serializer for a format."""
        self._serializers[format] = serializer
        logger.info("Registered custom serializer for format: %s", format)

    def supported_formats(self) -> list[str]:
        """List all registered/available formats."""
        return sorted(self._serializers.keys())

    # ── Serialize / Deserialize ─────────────────────────────────────

    def serialize(self, obj: Any, format: str = "json") -> str | bytes:
        """Serialize an object with timing and error tracking.

        Args:
            obj: Object to serialize.
            format: Target format.

        Returns:
            Serialized data.
        """
        start = time.time()
        try:
            serializer = self.get_serializer(format)
            result = serializer.serialize(obj)
            self._stats.append(SerializationResult(
                format=format,
                input_type=type(obj).__name__,
                output_size=len(result) if isinstance(result, (str, bytes)) else 0,
                duration_seconds=time.time() - start,
                success=True,
            ))
            return result
        except Exception as e:
            self._stats.append(SerializationResult(
                format=format,
                input_type=type(obj).__name__,
                output_size=0,
                duration_seconds=time.time() - start,
                success=False,
                error=str(e),
            ))
            raise

    def deserialize(self, data: str | bytes, format: str | None = None) -> Any:
        """Deserialize data with auto-detection fallback.

        Args:
            data: Serialized data.
            format: Format to use (if None, auto-detect).

        Returns:
            Deserialized object.
        """
        if format is None:
            serializer = Serializer()
            format = serializer.detect_format(data)
            if format is None:
                format = "json"
        serializer = self.get_serializer(format)
        return serializer.deserialize(data, format)

    def serialize_batch(self, objects: list[Any], format: str = "json") -> list[str | bytes]:
        """Serialize multiple objects in sequence.

        Args:
            objects: List of objects to serialize.
            format: Target format.

        Returns:
            List of serialized outputs.
        """
        return [self.serialize(obj, format=format) for obj in objects]

    def round_trip(self, obj: Any, format: str = "json") -> Any:
        """Serialize then deserialize — useful for testing consistency.

        Returns:
            The deserialized object after a round trip.
        """
        serialized = self.serialize(obj, format=format)
        return self.deserialize(serialized, format=format)

    # ── Statistics ──────────────────────────────────────────────────

    @property
    def operation_count(self) -> int:
        return len(self._stats)

    @property
    def error_count(self) -> int:
        return sum(1 for s in self._stats if not s.success)

    def summary(self) -> dict[str, Any]:
        """Return serialization statistics summary."""
        if not self._stats:
            return {"operations": 0, "errors": 0}
        successful = [s for s in self._stats if s.success]
        return {
            "operations": len(self._stats),
            "errors": self.error_count,
            "formats_used": list({s.format for s in self._stats}),
            "total_bytes": sum(s.output_size for s in successful),
            "avg_duration_ms": (sum(s.duration_seconds for s in successful) / max(len(successful), 1)) * 1000,
        }

    def clear_stats(self) -> None:
        """Reset operation statistics."""
        self._stats.clear()
