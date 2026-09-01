"""
Cache serialization utilities.

Provides serializers for cache values.
"""

import base64
import hashlib
import hmac
import json
import os
import pickle
import zlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_PICKLE_SECRET_KEY = os.urandom(32)


class CacheSerializer(ABC):
    """Abstract base class for cache serializers."""

    @abstractmethod
    def serialize(self, value: Any) -> bytes:
        """Serialize a value to bytes."""

    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to a value."""


class JSONSerializer(CacheSerializer):
    """JSON serializer for cache values."""

    def __init__(self, indent: int | None = None):
        self.indent = indent

    def serialize(self, value: Any) -> bytes:
        """Serialize this object to a portable format."""
        return json.dumps(value, indent=self.indent, default=str).encode("utf-8")

    def deserialize(self, data: bytes) -> Any:
        """Deserialize from a portable format and return an instance."""
        return json.loads(data.decode("utf-8"))


class PickleSerializer(CacheSerializer):
    """Pickle serializer for cache values.

    .. warning::
        Pickle can execute arbitrary code during deserialization.
        Only use this with **trusted** data. Prefer ``JSONSerializer``
        for untrusted or network-sourced cache entries.
    """

    def __init__(
        self,
        protocol: int = pickle.HIGHEST_PROTOCOL,
        secret_key: bytes | str | None = None,
    ):
        self.protocol = protocol
        if secret_key:
            self.secret_key = (
                secret_key.encode("utf-8")
                if isinstance(secret_key, str)
                else secret_key
            )
        else:
            self.secret_key = _PICKLE_SECRET_KEY

    def serialize(self, value: Any) -> bytes:
        """Serialize this object to a portable format."""
        payload = pickle.dumps(value, protocol=self.protocol)
        mac = hmac.new(self.secret_key, payload, hashlib.sha256).digest()
        return mac + payload

    def deserialize(self, data: bytes) -> Any:
        """Deserialize from a portable format and return an instance."""
        if len(data) < 32:
            raise ValueError("Invalid payload: too short")
        mac = data[:32]
        payload = data[32:]
        expected_mac = hmac.new(self.secret_key, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("Invalid payload: signature mismatch")
        return pickle.loads(payload)


class CompressedSerializer(CacheSerializer):
    """Wrapper that adds compression."""

    def __init__(
        self,
        base_serializer: CacheSerializer,
        compression_level: int = 6,
    ):
        self.base = base_serializer
        self.level = compression_level

    def serialize(self, value: Any) -> bytes:
        """Serialize this object to a portable format."""
        data = self.base.serialize(value)
        return zlib.compress(data, level=self.level)

    def deserialize(self, data: bytes) -> Any:
        """Deserialize from a portable format and return an instance."""
        decompressed = zlib.decompress(data)
        return self.base.deserialize(decompressed)


class Base64Serializer(CacheSerializer):
    """Wrapper that adds base64 encoding."""

    def __init__(self, base_serializer: CacheSerializer):
        self.base = base_serializer

    def serialize(self, value: Any) -> bytes:
        """Serialize this object to a portable format."""
        data = self.base.serialize(value)
        return base64.b64encode(data)

    def deserialize(self, data: bytes) -> Any:
        """Deserialize from a portable format and return an instance."""
        decoded = base64.b64decode(data)
        return self.base.deserialize(decoded)


class StringSerializer(CacheSerializer):
    """Simple string serializer."""

    def __init__(self, encoding: str = "utf-8"):
        self.encoding = encoding

    def serialize(self, value: Any) -> bytes:
        """Serialize this object to a portable format."""
        return str(value).encode(self.encoding)

    def deserialize(self, data: bytes) -> Any:
        """Deserialize from a portable format and return an instance."""
        return data.decode(self.encoding)


class TypedSerializer(CacheSerializer):
    """Serializer that preserves type information."""

    # Pre-allocate the type map mapping as a class variable to avoid
    # the overhead of recreating this dictionary on every deserialize call.
    # This provides a small but measurable performance improvement.
    _TYPE_MAP = {
        "int": int,
        "float": float,
        "bool": bool,
        "str": str,
        "list": list,
        "dict": dict,
    }

    def __init__(self, base_serializer: CacheSerializer | None = None):
        self.base = base_serializer or JSONSerializer()

    def serialize(self, value: Any) -> bytes:
        """Serialize this object to a portable format."""
        type_name = type(value).__name__
        wrapped = {
            "_type": type_name,
            "_value": value if self._is_json_serializable(value) else str(value),
        }
        return self.base.serialize(wrapped)

    def deserialize(self, data: bytes) -> Any:
        """Deserialize from a portable format and return an instance."""
        wrapped = self.base.deserialize(data)
        type_name = wrapped.get("_type")
        value = wrapped.get("_value")

        if type_name in self._TYPE_MAP:
            return self._TYPE_MAP[type_name](value)

        return value

    def _is_json_serializable(self, value: Any) -> bool:
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError) as e:
            logger.debug("Value is not JSON serializable: %s", e)
            return False


def create_serializer(
    serializer_type: str = "json", compress: bool = False, **kwargs
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
    "Base64Serializer",
    "CacheSerializer",
    "CompressedSerializer",
    "JSONSerializer",
    "PickleSerializer",
    "StringSerializer",
    "TypedSerializer",
    "create_serializer",
]
