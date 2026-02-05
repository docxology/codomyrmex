"""Automated log rotation manager.

This module provides the LogRotationManager class for configuring automatic
log file rotation based on file size. This helps manage disk space and
maintain a rolling window of log history.

Example:
    >>> from codomyrmex.logging_monitoring.rotation import LogRotationManager
    >>> rotation_mgr = LogRotationManager("/var/log/myapp")
    >>> rotation_mgr.attach_rotating_handler("myapp", "app.log", max_bytes=5*1024*1024)
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional


class LogRotationManager:
    """Configures and manages rotating file handlers for loggers.

    Provides functionality to attach RotatingFileHandler instances to loggers,
    enabling automatic log file rotation when files reach a specified size.

    Attributes:
        log_dir: The directory where log files are stored.

    Example:
        >>> manager = LogRotationManager("./logs")
        >>> manager.attach_rotating_handler("api", "api.log", max_bytes=10*1024*1024, backup_count=10)
    """

    def __init__(self, log_dir: str = "logs"):
        """Initialize a LogRotationManager.

        Args:
            log_dir: The directory to store log files. Will be created if
                it does not exist. Defaults to "logs".
        """
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def attach_rotating_handler(
        self,
        logger_name: str,
        filename: str,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5
    ) -> RotatingFileHandler:
        """Attach a RotatingFileHandler to the specified logger.

        Creates a rotating file handler that automatically rotates log files
        when they reach the specified size, keeping a configurable number of
        backup files.

        Args:
            logger_name: The name of the logger to attach the handler to.
            filename: The name of the log file (will be created in log_dir).
            max_bytes: Maximum size of each log file in bytes before rotation.
                Defaults to 10 MB (10*1024*1024).
            backup_count: Number of backup files to keep. When rotation occurs,
                older files are renamed with numeric suffixes (.1, .2, etc.)
                and the oldest beyond this count is deleted. Defaults to 5.

        Returns:
            The configured RotatingFileHandler instance. The handler uses
            a fixed format: ``%(asctime)s - %(name)s - %(levelname)s - %(message)s``.

        Example:
            >>> manager = LogRotationManager("./logs")
            >>> handler = manager.attach_rotating_handler(
            ...     "database",
            ...     "db.log",
            ...     max_bytes=5*1024*1024,  # 5 MB
            ...     backup_count=3
            ... )
            # Creates: ./logs/db.log, and on rotation: db.log.1, db.log.2, db.log.3
        """
        logger = logging.getLogger(logger_name)
        file_path = os.path.join(self.log_dir, filename)

        handler = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        logger.addHandler(handler)
        return handler
