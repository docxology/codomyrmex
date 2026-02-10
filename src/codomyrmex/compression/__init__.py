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
    CompressionError,
    Compressor,
    auto_decompress,
    compress_data,
    decompress_data,
)
from .parallel import ParallelCompressor
from .zstd_compressor import ZstdCompressor

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the compression module."""
    return {
        "algorithms": {
            "help": "List available compression algorithms",
            "handler": lambda **kwargs: print(
                "Compression Algorithms:\n"
                "  - gzip: GNU zip (default, level 1-9)\n"
                "  - zlib: zlib deflate compression\n"
                "  - zip: ZIP archive format\n"
                "  - zstd: Zstandard compression (fast)\n"
                "  - parallel: Multi-threaded compression"
            ),
        },
        "stats": {
            "help": "Show compression module statistics",
            "handler": lambda **kwargs: print(
                "Compression Stats:\n"
                f"  Compressor: {Compressor.__name__} (available)\n"
                f"  Archive Manager: {ArchiveManager.__name__} (available)\n"
                f"  Zstd Compressor: {ZstdCompressor.__name__} (available)\n"
                f"  Parallel Compressor: {ParallelCompressor.__name__} (available)\n"
                "  Auto-decompress: available\n"
                "  Supported formats: gzip, zlib, zip, zstd"
            ),
        },
    }


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
    # CLI
    "cli_commands",
]


__version__ = "0.1.0"


from codomyrmex.exceptions import CompressionError


def compress(data: bytes, level: int = 6, format: str = "gzip") -> bytes:
    """Compress data."""
    compressor = Compressor(format=format)
    return compressor.compress(data, level)


def decompress(data: bytes, format: str | None = None) -> bytes:
    """Decompress data."""
    compressor = Compressor(format=format)
    return compressor.decompress(data)


def get_compressor(format: str = "gzip") -> Compressor:
    """Get a compressor instance."""
    return Compressor(format=format)


def compress_file(input_path: str, output_path: str | None = None, format: str = "gzip", level: int = 6) -> str:
    """Compress a file."""
    compressor = Compressor(format=format)
    return compressor.compress_file(input_path, output_path, level)


def decompress_file(input_path: str, output_path: str | None = None, format: str = "gzip") -> str:
    """Decompress a file."""
    compressor = Compressor(format=format)
    return compressor.decompress_file(input_path, output_path)


