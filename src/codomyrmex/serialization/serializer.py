"""Serializer for Codomyrmex Serialization module.

Provides serialization and deserialization of objects to various formats.
"""

import json
import pickle
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class SerializationFormat(Enum):
    """Supported serialization formats."""
    JSON = "json"
    PICKLE = "pickle"
    YAML = "yaml"


class SerializationError(Exception):
    """Raised when serialization fails."""
    pass


class Serializer:
    """Generic serializer supporting multiple formats."""

    def __init__(self, default_format: SerializationFormat = SerializationFormat.JSON):
        """Initialize serializer."""
        self.default_format = default_format

    def serialize(self, obj: Any, format: SerializationFormat | None = None) -> bytes:
        """Serialize an object to bytes."""
        fmt = format or self.default_format

        try:
            if fmt == SerializationFormat.JSON:
                return self._serialize_json(obj)
            elif fmt == SerializationFormat.PICKLE:
                return pickle.dumps(obj)
            elif fmt == SerializationFormat.YAML:
                return self._serialize_yaml(obj)
            else:
                raise SerializationError(f"Unsupported format: {fmt}")
        except Exception as e:
            raise SerializationError(f"Serialization failed: {e}") from e

    def deserialize(self, data: bytes, format: SerializationFormat | None = None,
                    target_type: type[T] | None = None) -> Any:
        """Deserialize bytes to an object."""
        fmt = format or self.default_format

        try:
            if fmt == SerializationFormat.JSON:
                return self._deserialize_json(data, target_type)
            elif fmt == SerializationFormat.PICKLE:
                return pickle.loads(data)
            elif fmt == SerializationFormat.YAML:
                return self._deserialize_yaml(data, target_type)
            else:
                raise SerializationError(f"Unsupported format: {fmt}")
        except Exception as e:
            raise SerializationError(f"Deserialization failed: {e}") from e

    def _serialize_json(self, obj: Any) -> bytes:
        """Serialize to JSON bytes."""
        return json.dumps(self._to_jsonable(obj), indent=2).encode('utf-8')

    def _deserialize_json(self, data: bytes, target_type: type[T] | None) -> Any:
        """Deserialize from JSON bytes."""
        parsed = json.loads(data.decode('utf-8'))
        if target_type and is_dataclass(target_type):
            return target_type(**parsed)
        return parsed

    def _serialize_yaml(self, obj: Any) -> bytes:
        """Serialize to YAML bytes."""
        if not YAML_AVAILABLE:
            raise SerializationError("PyYAML not installed")
        return yaml.dump(self._to_jsonable(obj), default_flow_style=False).encode('utf-8')

    def _deserialize_yaml(self, data: bytes, target_type: type[T] | None) -> Any:
        """Deserialize from YAML bytes."""
        if not YAML_AVAILABLE:
            raise SerializationError("PyYAML not installed")
        parsed = yaml.safe_load(data.decode('utf-8'))
        if target_type and is_dataclass(target_type):
            return target_type(**parsed)
        return parsed

    def _to_jsonable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable form."""
        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        elif is_dataclass(obj):
            return asdict(obj)
        elif isinstance(obj, dict):
            return {k: self._to_jsonable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._to_jsonable(item) for item in obj]
        elif isinstance(obj, Path):
            return str(obj)
        else:
            return str(obj)

    def to_file(self, obj: Any, file_path: str, format: SerializationFormat | None = None):
        """Serialize object to file."""
        data = self.serialize(obj, format)
        with open(file_path, 'wb') as f:
            f.write(data)

    def from_file(self, file_path: str, format: SerializationFormat | None = None,
                  target_type: type[T] | None = None) -> Any:
        """Deserialize object from file."""
        with open(file_path, 'rb') as f:
            data = f.read()
        return self.deserialize(data, format, target_type)


# Convenience functions
def serialize(obj: Any, format: SerializationFormat = SerializationFormat.JSON) -> bytes:
    """Serialize an object."""
    serializer = Serializer(format)
    return serializer.serialize(obj)

def deserialize(data: bytes, format: SerializationFormat = SerializationFormat.JSON) -> Any:
    """Deserialize bytes to object."""
    serializer = Serializer(format)
    return serializer.deserialize(data)
