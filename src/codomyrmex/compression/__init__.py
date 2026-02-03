"""
Compression module for Codomyrmex.

This module provides data compression utilities and archive handling:
- gzip, zlib, and ZIP format support
- Configurable compression levels
- Stream-based compression
- Automatic format detection
- File compression utilities
- Archive creation and extraction
"""

from pathlib import Path
from typing import Optional

from codomyrmex.exceptions import CodomyrmexError

from .archive_manager import ArchiveManager
from .compressor import (
    Compressor,
    CompressionError,
    compress_data,
    decompress_data,
    auto_decompress,
)
from .zstd_compressor import ZstdCompressor
from .parallel import ParallelCompressor

__all__ = [
    # Classes
    "Compressor",
    "ArchiveManager",
    "CompressionError",
    "ZstdCompressor",
    "ParallelCompressor",
    # Functions
    "compress",
    "decompress",
    "get_compressor",
    "compress_data",
    "decompress_data",
    "auto_decompress",
    "compress_file",
    "decompress_file",
]


__version__ = "0.1.0"


from codomyrmex.exceptions import CompressionError


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


def compress_file(input_path: str, output_path: Optional[str] = None, format: str = "gzip", level: int = 6) -> str:
    """Compress a file."""
    compressor = Compressor(format=format)
    return compressor.compress_file(input_path, output_path, level)


def decompress_file(input_path: str, output_path: Optional[str] = None, format: str = "gzip") -> str:
    """Decompress a file."""
    compressor = Compressor(format=format)
    return compressor.decompress_file(input_path, output_path)


