"""
Serialization module for Codomyrmex.

This module provides unified data serialization/deserialization with support
for JSON, YAML, TOML, MessagePack, and other formats.
"""

from typing import Any, Optional, Union

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .binary_formats import AvroSerializer, MsgpackSerializer, ParquetSerializer
from .exceptions import (
    BinaryFormatError,
    CircularReferenceError,
    DeserializationError,
    EncodingError,
    FormatNotSupportedError,
    SchemaValidationError,
    SerializationError,
    TypeConversionError,
)
from .serialization_manager import SerializationManager
from .serializer import SerializationFormat, Serializer

def cli_commands():
    """Return CLI commands for the serialization module."""
    def _formats(**kwargs):
        """List supported serialization formats."""
        print("=== Serialization Formats ===")
        for fmt in SerializationFormat:
            print(f"  {fmt.value}")
        print("\nBinary formats:")
        print("  msgpack    - MessagePack (MsgpackSerializer)")
        print("  avro       - Apache Avro (AvroSerializer)")
        print("  parquet    - Apache Parquet (ParquetSerializer)")

    def _convert(**kwargs):
        """Convert data between serialization formats."""
        src_fmt = kwargs.get("from", "json")
        dst_fmt = kwargs.get("to", "yaml")
        path = kwargs.get("path")
        if not path:
            print("Usage: serialization convert --path <file> --from json --to yaml")
            return
        try:
            with open(path, "rb") as f:
                raw = f.read()
            obj = deserialize(raw, format=src_fmt)
            output = serialize(obj, format=dst_fmt)
            print(output.decode("utf-8", errors="replace"))
        except Exception as e:
            print(f"Conversion error: {e}")

    return {
        "formats": {"handler": _formats, "help": "List serialization formats"},
        "convert": {"handler": _convert, "help": "Convert between serialization formats"},
    }


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
    "cli_commands",
]

__version__ = "0.1.0"


def serialize(obj: Any, format: str | SerializationFormat = "json") -> bytes:
    """Serialize an object to bytes."""
    fmt = SerializationFormat(format) if isinstance(format, str) else format
    serializer = Serializer(default_format=fmt)
    return serializer.serialize(obj)


def deserialize(data: bytes, format: str | SerializationFormat = "json") -> Any:
    """Deserialize data to an object."""
    fmt = SerializationFormat(format) if isinstance(format, str) else format
    serializer = Serializer(default_format=fmt)
    return serializer.deserialize(data)


