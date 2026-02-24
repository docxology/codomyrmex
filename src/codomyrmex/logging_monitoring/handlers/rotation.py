"""Automated log rotation with cleanup, health monitoring, and stats.

Provides:
- LogRotationManager: rotating file handler attachment with size/count config
- Cleanup of old log files beyond retention
- Disk usage analysis for log directories
- Handler listing and removal
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Any


class LogRotationManager:
    """Configures and manages rotating file handlers for loggers.

    Supports handler attachment, disk monitoring, and log cleanup.

    Example::

        mgr = LogRotationManager("./logs")
        mgr.attach_rotating_handler("api", "api.log", max_bytes=5*1024*1024)
        print(mgr.disk_usage())
    """

    def __init__(self, log_dir: str = "logs") -> None:
        """Execute   Init   operations natively."""
        self.log_dir = log_dir
        self._handlers: dict[str, RotatingFileHandler] = {}
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def attach_rotating_handler(
        self,
        logger_name: str,
        filename: str,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        level: int = logging.DEBUG,
    ) -> RotatingFileHandler:
        """Attach a RotatingFileHandler to a logger.

        Args:
            logger_name: Logger name.
            filename: Log file name (created in log_dir).
            max_bytes: Max file size before rotation (default 10 MB).
            backup_count: Number of backup files to keep.
            level: Logging level for the handler.

        Returns:
            The configured handler.
        """
        logger = logging.getLogger(logger_name)
        file_path = os.path.join(self.log_dir, filename)

        handler = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        self._handlers[f"{logger_name}:{filename}"] = handler
        return handler

    def remove_handler(self, logger_name: str, filename: str) -> bool:
        """Remove a previously attached handler."""
        key = f"{logger_name}:{filename}"
        handler = self._handlers.pop(key, None)
        if handler:
            logging.getLogger(logger_name).removeHandler(handler)
            handler.close()
            return True
        return False

    def list_handlers(self) -> list[str]:
        """List all managed handler keys (logger:filename)."""
        return sorted(self._handlers.keys())

    # ── Disk monitoring ─────────────────────────────────────────────

    def disk_usage(self) -> dict[str, Any]:
        """Calculate disk usage of the log directory.

        Returns:
            Dict with total_bytes, file_count, and largest_file.
        """
        log_path = Path(self.log_dir)
        if not log_path.exists():
            return {"total_bytes": 0, "file_count": 0, "largest_file": ""}

        files = list(log_path.glob("*"))
        total = sum(f.stat().st_size for f in files if f.is_file())
        largest = max(files, key=lambda f: f.stat().st_size if f.is_file() else 0, default=None)

        return {
            "total_bytes": total,
            "total_mb": round(total / (1024 * 1024), 2),
            "file_count": len([f for f in files if f.is_file()]),
            "largest_file": largest.name if largest else "",
        }

    def log_files(self) -> list[dict[str, Any]]:
        """List all files in the log directory with metadata."""
        log_path = Path(self.log_dir)
        if not log_path.exists():
            return []
        result = []
        for f in sorted(log_path.iterdir()):
            if f.is_file():
                stat = f.stat()
                result.append({
                    "name": f.name,
                    "size_bytes": stat.st_size,
                    "modified": stat.st_mtime,
                })
        return result

    def cleanup_old_logs(self, max_age_days: float = 30.0) -> int:
        """Remove log files older than max_age_days.

        Returns:
            Number of files removed.
        """
        log_path = Path(self.log_dir)
        if not log_path.exists():
            return 0
        cutoff = time.time() - (max_age_days * 86400)
        removed = 0
        for f in log_path.iterdir():
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink()
                removed += 1
        return removed

    @property
    def handler_count(self) -> int:
        """Execute Handler Count operations natively."""
        return len(self._handlers)
