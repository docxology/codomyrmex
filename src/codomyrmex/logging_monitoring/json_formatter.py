"""Structured JSON formatter for logging."""

import json
import logging

class JSONFormatter(logging.Formatter):
    """Formatter that outputs log records as JSON objects."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
            
        return json.dumps(log_entry)

