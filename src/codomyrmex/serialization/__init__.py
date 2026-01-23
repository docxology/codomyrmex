"""
Serialization module for Codomyrmex.

This module provides unified data serialization/deserialization with support
for JSON, YAML, TOML, MessagePack, and other formats.
"""

from typing import Any, Optional, Union

from .serializer import Serializer, SerializationFormat
from .serialization_manager import SerializationManager
from .binary_formats import MsgpackSerializer, AvroSerializer, ParquetSerializer
from .exceptions import (
    SerializationError,
    DeserializationError,
    SchemaValidationError,
    EncodingError,
    FormatNotSupportedError,
    CircularReferenceError,
    TypeConversionError,
    BinaryFormatError,
)

__all__ = [
    # Core classes
    "Serializer",
    "SerializationManager",
    "SerializationFormat",
    "MsgpackSerializer",
    "AvroSerializer",
    "ParquetSerializer",
    # Functions
    "serialize",
    "deserialize",
    # Exceptions
    "SerializationError",
    "DeserializationError",
    "SchemaValidationError",
    "EncodingError",
    "FormatNotSupportedError",
    "CircularReferenceError",
    "TypeConversionError",
    "BinaryFormatError",
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


