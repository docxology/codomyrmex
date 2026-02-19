# DEPRECATED(v0.2.0): Shim module. Import from compression.engines.zstd_compressor instead. Will be removed in v0.3.0.
"""Backward-compatible re-export shim.

This module has been moved to compression.engines.zstd_compressor.
All public names are re-exported here to preserve the existing API.
"""

from .engines.zstd_compressor import ZstdCompressor  # noqa: F401
