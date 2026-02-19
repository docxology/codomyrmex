# DEPRECATED(v0.2.0): Shim module. Import from compression.engines.parallel instead. Will be removed in v0.3.0.
"""Backward-compatible re-export shim.

This module has been moved to compression.engines.parallel.
All public names are re-exported here to preserve the existing API.
"""

from .engines.parallel import ParallelCompressor  # noqa: F401
