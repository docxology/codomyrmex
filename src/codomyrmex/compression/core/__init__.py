"""Core compression utilities."""

from .compressor import (
    CompressionError,
    Compressor,
    auto_decompress,
    compare_formats,
    compress_data,
    decompress_data,
)

__all__ = [
    "CompressionError",
    "Compressor",
    "auto_decompress",
    "compare_formats",
    "compress_data",
    "decompress_data",
]
