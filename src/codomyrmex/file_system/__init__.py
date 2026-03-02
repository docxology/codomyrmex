"""
File system module for Codomyrmex.

Provides a unified interface for filesystem operations like CRUD,
directory management, searching, and metadata retrieval.
"""

from .core import FileSystemManager, create_file_system_manager

__all__ = [
    "FileSystemManager",
    "create_file_system_manager",
]
