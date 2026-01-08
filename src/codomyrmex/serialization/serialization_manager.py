"""
Serialization manager for managing multiple serializers.
"""

from typing import Any, Optional, Union

from codomyrmex.logging_monitoring.logger_config import get_logger

from .serializer import Serializer

logger = get_logger(__name__)


class SerializationManager:
    """Manager for serialization operations."""

    def __init__(self):
        """Initialize serialization manager."""
        self._serializers: dict[str, Serializer] = {}

    def get_serializer(self, format: str = "json") -> Serializer:
        """Get a serializer for a format.

        Args:
            format: Serialization format

        Returns:
            Serializer instance
        """
        if format not in self._serializers:
            self._serializers[format] = Serializer(format=format)
        return self._serializers[format]

    def serialize(self, obj: Any, format: str = "json") -> Union[str, bytes]:
        """Serialize an object.

        Args:
            obj: Object to serialize
            format: Serialization format

        Returns:
            Serialized data
        """
        serializer = self.get_serializer(format)
        return serializer.serialize(obj)

    def deserialize(self, data: Union[str, bytes], format: Optional[str] = None) -> Any:
        """Deserialize data.

        Args:
            data: Serialized data
            format: Format to use (if None, auto-detect)

        Returns:
            Deserialized object
        """
        if format is None:
            # Try to detect format
            serializer = Serializer()
            format = serializer.detect_format(data)
            if format is None:
                format = "json"  # Default fallback

        serializer = self.get_serializer(format)
        return serializer.deserialize(data, format)


