"""
Serialization module for Codomyrmex.

This module provides unified data serialization/deserialization with support
for JSON, YAML, TOML, MessagePack, and other formats.
"""

from typing import Any, Optional, Union

from codomyrmex.exceptions import CodomyrmexError

from .serializer import Serializer
from .serialization_manager import SerializationManager

__all__ = [
    "Serializer",
    "SerializationManager",
    "serialize",
    "deserialize",
    "detect_format",
]

__version__ = "0.1.0"


class SerializationError(CodomyrmexError):
    """Raised when serialization operations fail."""

    pass


def serialize(obj: Any, format: str = "json") -> Union[str, bytes]:
    """Serialize an object to string or bytes."""
    serializer = Serializer(format=format)
    return serializer.serialize(obj)


def deserialize(data: Union[str, bytes], format: Optional[str] = None) -> Any:
    """Deserialize data to an object."""
    serializer = Serializer(format=format)
    return serializer.deserialize(data)


def detect_format(data: Union[str, bytes]) -> Optional[str]:
    """Detect the serialization format from data."""
    serializer = Serializer()
    return serializer.detect_format(data)

