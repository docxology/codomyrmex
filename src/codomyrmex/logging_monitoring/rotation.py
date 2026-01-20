"""Automated log rotation manager."""

import logging
from logging.handlers import RotatingFileHandler
import os

class LogRotationManager:
    """Configures and manages rotating file handlers for loggers."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def attach_rotating_handler(self, logger_name: str, filename: str, max_bytes: int = 10*1024*1024, backup_count: int = 5):
        """Ataches a RotatingFileHandler to the specified logger."""
        logger = logging.getLogger(logger_name)
        file_path = os.path.join(self.log_dir, filename)
        
        handler = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        logger.addHandler(handler)
        return handler
