# DEPRECATED(v0.2.0): Shim module. Import from compression.archives.archive_manager instead. Will be removed in v0.3.0.
"""Backward-compatible re-export shim.

This module has been moved to compression.archives.archive_manager.
All public names are re-exported here to preserve the existing API.
"""

from .archives.archive_manager import ArchiveManager  # noqa: F401
