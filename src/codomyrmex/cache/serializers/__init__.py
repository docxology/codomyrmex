"""
Cache serialization utilities.

Provides serializers for cache values.
"""

import base64
import json
import pickle
import zlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


class CacheSerializer(ABC):
    """Abstract base class for cache serializers."""

    @abstractmethod
    def serialize(self, value: Any) -> bytes:
        """Serialize a value to bytes."""
        pass

    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to a value."""
        pass


class JSONSerializer(CacheSerializer):
    """JSON serializer for cache values."""

    def __init__(self, indent: int | None = None):
        """Execute   Init   operations natively."""
        self.indent = indent

    def serialize(self, value: Any) -> bytes:
        """Execute Serialize operations natively."""
        return json.dumps(value, indent=self.indent, default=str).encode('utf-8')

    def deserialize(self, data: bytes) -> Any:
        """Execute Deserialize operations natively."""
        return json.loads(data.decode('utf-8'))


class PickleSerializer(CacheSerializer):
    """Pickle serializer for cache values.

    .. warning::
        Pickle can execute arbitrary code during deserialization.
        Only use this with **trusted** data. Prefer ``JSONSerializer``
        for untrusted or network-sourced cache entries.
    """

    def __init__(self, protocol: int = pickle.HIGHEST_PROTOCOL):
        """Execute   Init   operations natively."""
        self.protocol = protocol

    def serialize(self, value: Any) -> bytes:
        """Execute Serialize operations natively."""
        return pickle.dumps(value, protocol=self.protocol)

    def deserialize(self, data: bytes) -> Any:
        """Execute Deserialize operations natively."""
        return pickle.loads(data)


class CompressedSerializer(CacheSerializer):
    """Wrapper that adds compression."""

    def __init__(
        self,
        base_serializer: CacheSerializer,
        compression_level: int = 6,
    ):
        """Execute   Init   operations natively."""
        self.base = base_serializer
        self.level = compression_level

    def serialize(self, value: Any) -> bytes:
        """Execute Serialize operations natively."""
        data = self.base.serialize(value)
        return zlib.compress(data, level=self.level)

    def deserialize(self, data: bytes) -> Any:
        """Execute Deserialize operations natively."""
        decompressed = zlib.decompress(data)
        return self.base.deserialize(decompressed)


class Base64Serializer(CacheSerializer):
    """Wrapper that adds base64 encoding."""

    def __init__(self, base_serializer: CacheSerializer):
        """Execute   Init   operations natively."""
        self.base = base_serializer

    def serialize(self, value: Any) -> bytes:
        """Execute Serialize operations natively."""
        data = self.base.serialize(value)
        return base64.b64encode(data)

    def deserialize(self, data: bytes) -> Any:
        """Execute Deserialize operations natively."""
        decoded = base64.b64decode(data)
        return self.base.deserialize(decoded)


class StringSerializer(CacheSerializer):
    """Simple string serializer."""

    def __init__(self, encoding: str = 'utf-8'):
        """Execute   Init   operations natively."""
        self.encoding = encoding

    def serialize(self, value: Any) -> bytes:
        """Execute Serialize operations natively."""
        return str(value).encode(self.encoding)

    def deserialize(self, data: bytes) -> Any:
        """Execute Deserialize operations natively."""
        return data.decode(self.encoding)


class TypedSerializer(CacheSerializer):
    """Serializer that preserves type information."""

    def __init__(self, base_serializer: CacheSerializer | None = None):
        """Execute   Init   operations natively."""
        self.base = base_serializer or JSONSerializer()

    def serialize(self, value: Any) -> bytes:
        """Execute Serialize operations natively."""
        type_name = type(value).__name__
        wrapped = {
            "_type": type_name,
            "_value": value if self._is_json_serializable(value) else str(value),
        }
        return self.base.serialize(wrapped)

    def deserialize(self, data: bytes) -> Any:
        """Execute Deserialize operations natively."""
        wrapped = self.base.deserialize(data)
        type_name = wrapped.get("_type")
        value = wrapped.get("_value")

        type_map = {
            "int": int,
            "float": float,
            "bool": bool,
            "str": str,
            "list": list,
            "dict": dict,
        }

        if type_name in type_map:
            return type_map[type_name](value)

        return value

    def _is_json_serializable(self, value: Any) -> bool:
        """Execute  Is Json Serializable operations natively."""
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError):
            return False


def create_serializer(
    serializer_type: str = "json",
    compress: bool = False,
    **kwargs
) -> CacheSerializer:
    """Factory function to create serializers."""
    serializers = {
        "json": JSONSerializer,
        "pickle": PickleSerializer,
        "string": StringSerializer,
        "typed": TypedSerializer,
    }

    serializer_class = serializers.get(serializer_type)
    if not serializer_class:
        raise ValueError(f"Unknown serializer: {serializer_type}")

    serializer = serializer_class(**kwargs)

    if compress:
        serializer = CompressedSerializer(serializer)

    return serializer


__all__ = [
    "CacheSerializer",
    "JSONSerializer",
    "PickleSerializer",
    "CompressedSerializer",
    "Base64Serializer",
    "StringSerializer",
    "TypedSerializer",
    "create_serializer",
]
