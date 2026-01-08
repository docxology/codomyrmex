"""
Compression module for Codomyrmex.

This module provides data compression utilities and archive handling.
"""

from pathlib import Path
from typing import Optional

from codomyrmex.exceptions import CodomyrmexError

from .archive_manager import ArchiveManager
from .compressor import Compressor

__all__ = [
    "Compressor",
    "ArchiveManager",
    "compress",
    "decompress",
    "get_compressor",
]

__version__ = "0.1.0"


class CompressionError(CodomyrmexError):
    """Raised when compression operations fail."""

    pass


def compress(data: bytes, level: int = 6, format: str = "gzip") -> bytes:
    """Compress data."""
    compressor = Compressor(format=format)
    return compressor.compress(data, level)


def decompress(data: bytes, format: Optional[str] = None) -> bytes:
    """Decompress data."""
    compressor = Compressor(format=format)
    return compressor.decompress(data)


def get_compressor(format: str = "gzip") -> Compressor:
    """Get a compressor instance."""
    return Compressor(format=format)


