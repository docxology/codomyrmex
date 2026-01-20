"""
Serialization module for Codomyrmex.

This module provides unified data serialization/deserialization with support
for JSON, YAML, TOML, MessagePack, and other formats.
"""

from typing import Any, Optional, Union

from codomyrmex.exceptions import CodomyrmexError

from .serializer import Serializer, SerializationFormat, SerializationError
from .serialization_manager import SerializationManager
from .binary_formats import MsgpackSerializer, AvroSerializer, ParquetSerializer

__all__ = [
    "Serializer",
    "SerializationManager",
    "SerializationFormat",
    "SerializationError",
    "serialize",
    "deserialize",
    "MsgpackSerializer",
    "AvroSerializer",
    "ParquetSerializer",
]

__version__ = "0.1.0"


def serialize(obj: Any, format: Union[str, SerializationFormat] = "json") -> bytes:
    """Serialize an object to bytes."""
    fmt = SerializationFormat(format) if isinstance(format, str) else format
    serializer = Serializer(default_format=fmt)
    return serializer.serialize(obj)


def deserialize(data: bytes, format: Union[str, SerializationFormat] = "json") -> Any:
    """Deserialize data to an object."""
    fmt = SerializationFormat(format) if isinstance(format, str) else format
    serializer = Serializer(default_format=fmt)
    return serializer.deserialize(data)


