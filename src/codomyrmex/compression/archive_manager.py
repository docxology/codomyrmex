"""Backward-compatible re-export shim.

This module has been moved to compression.archives.archive_manager.
All public names are re-exported here to preserve the existing API.
"""

from .archives.archive_manager import ArchiveManager  # noqa: F401
