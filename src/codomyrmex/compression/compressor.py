"""Backward-compatible re-export shim.

This module has been moved to compression.core.compressor.
All public names are re-exported here to preserve the existing API.
"""

from .core.compressor import (  # noqa: F401
    CompressionError,
    Compressor,
    auto_decompress,
    compare_formats,
    compress_data,
    decompress_data,
)
