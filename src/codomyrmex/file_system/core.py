"""
Core implementation of the File System module.

This module provides the main FileSystemManager class for managing
files and directories, as well as several utility functions.
"""

import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class FileSystemManager:
    """Main class for filesystem operations in Codomyrmex."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the FileSystemManager.

        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        logger.info("FileSystemManager initialized")

    def create_file(self, path: Union[str, Path], content: str = "", overwrite: bool = True) -> Path:
        """
        Create a file with the given content.

        Args:
            path: Path to the file.
            content: String content to write.
            overwrite: Whether to overwrite existing file.

        Returns:
            The Path of the created file.

        Raises:
            FileExistsError: If file exists and overwrite is False.
        """
        path = Path(path)
        if path.exists() and not overwrite:
            logger.error(f"File already exists: {path}")
            raise FileExistsError(f"File exists: {path}")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        logger.info(f"File created: {path}")
        return path

    def read_file(self, path: Union[str, Path]) -> str:
        """
        Read file content as a string.

        Args:
            path: Path to the file.

        Returns:
            The content of the file.

        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        path = Path(path)
        if not path.is_file():
            logger.error(f"File not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")
        
        return path.read_text(encoding='utf-8')

    def append_to_file(self, path: Union[str, Path], content: str) -> Path:
        """
        Append content to an existing file.

        Args:
            path: Path to the file.
            content: Content to append.

        Returns:
            The Path of the updated file.
        """
        path = Path(path)
        with path.open("a", encoding='utf-8') as f:
            f.write(content)
        logger.debug(f"Appended to file: {path}")
        return path

    def delete(self, path: Union[str, Path], recursive: bool = False) -> bool:
        """
        Delete a file or directory.

        Args:
            path: Path to delete.
            recursive: If directory, delete contents as well.

        Returns:
            True if deletion was successful.

        Raises:
            OSError: For various deletion failures.
        """
        path = Path(path)
        if not path.exists():
            logger.warning(f"Path does not exist, nothing to delete: {path}")
            return False
        
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            if recursive:
                shutil.rmtree(path)
            else:
                path.rmdir()
        
        logger.info(f"Deleted path: {path}")
        return True

    def create_directory(self, path: Union[str, Path], exist_ok: bool = True) -> Path:
        """
        Create a new directory.

        Args:
            path: Path of the directory to create.
            exist_ok: Don't raise error if directory exists.

        Returns:
            Path of the created directory.
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=exist_ok)
        logger.info(f"Directory created: {path}")
        return path

    def list_dir(self, path: Union[str, Path] = ".", recursive: bool = False) -> List[Path]:
        """
        List directory contents.

        Args:
            path: Directory to list.
            recursive: If True, list recursively.

        Returns:
            A list of Path objects for all items.
        """
        path = Path(path)
        if recursive:
            return list(path.rglob("*"))
        return list(path.iterdir())

    def get_info(self, path: Union[str, Path]) -> Dict[str, Any]:
        """
        Retrieve detailed information about a file or directory.

        Args:
            path: Path to analyze.

        Returns:
            A dictionary containing metadata.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        stats = path.stat()
        return {
            "name": path.name,
            "path": str(path.absolute()),
            "size": stats.st_size,
            "is_dir": path.is_dir(),
            "extension": path.suffix.lower(),
            "created_at": datetime.fromtimestamp(stats.st_ctime),
            "modified_at": datetime.fromtimestamp(stats.st_mtime),
            "permissions": oct(stats.st_mode)[-3:],
        }

    def find_files(self, pattern: str, search_path: Union[str, Path] = ".") -> List[Path]:
        """
        Search for files by pattern.

        Args:
            pattern: Glob pattern (e.g., "*.txt").
            search_path: Directory to start search from.

        Returns:
            List of matching Path objects.
        """
        search_path = Path(search_path)
        return list(search_path.rglob(pattern))

    def get_hash(self, path: Union[str, Path], algorithm: str = "sha256") -> str:
        """
        Calculate a file's content hash.

        Args:
            path: File to hash.
            algorithm: Hash algorithm name.

        Returns:
            Hex digest of the file content.
        """
        path = Path(path)
        if not path.is_file():
            raise ValueError(f"Not a file: {path}")
            
        hasher = hashlib.new(algorithm)
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def find_duplicates(self, path: Union[str, Path] = ".") -> Dict[str, List[Path]]:
        """
        Find duplicate files based on content hash.

        Args:
            path: Directory to search for duplicates.

        Returns:
            Dict mapping hashes to lists of duplicate Path objects.
        """
        path = Path(path)
        hashes = {}
        for item in path.rglob("*"):
            if item.is_file():
                try:
                    h = self.get_hash(item)
                    if h not in hashes:
                        hashes[h] = []
                    hashes[h].append(item)
                except Exception as e:
                    logger.error(f"Error hashing {item}: {e}")
        
        # Only return items with duplicates
        return {h: paths for h, paths in hashes.items() if len(paths) > 1}

    def get_disk_usage(self, path: Union[str, Path] = ".") -> Dict[str, Any]:
        """
        Calculate disk usage for the given path.

        Args:
            path: Path to analyze.

        Returns:
            Dict with total, used, and free space (in bytes).
        """
        path = Path(path).resolve()
        # Fallback to current directory if path doesn't exist for usage stats
        p = str(path) if path.exists() else "."
        usage = shutil.disk_usage(p)
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": (usage.used / usage.total) * 100 if usage.total > 0 else 0
        }


def create_file_system_manager(config: Optional[Dict[str, Any]] = None) -> FileSystemManager:
    """Convenience function to create FileSystemManager."""
    return FileSystemManager(config)
