from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Iterator
import json
import logging
import os
import sys
import time

from contextlib import contextmanager
import threading
import uuid


# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# More detailed log format for debug purposes, can be set via env variable
DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"

_logging_configured = False


# Custom JSON Formatter
class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging output.
    """
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name, # Use "name" instead of "logger" for test compliance
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "context"):
            log_data["context"] = record.context
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
            
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "message", "context", "correlation_id"
            ]:
                log_data[key] = value
                
        return json.dumps(log_data)

def setup_logging(force=True): # Default to force True for test robustness
    global _logging_configured
    if _logging_configured and not force:
        return

    log_level_str = os.getenv("CODOMYRMEX_LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("CODOMYRMEX_LOG_FILE")
    log_format_str_text = os.getenv("CODOMYRMEX_LOG_FORMAT", DEFAULT_LOG_FORMAT)
    log_output_type = os.getenv("CODOMYRMEX_LOG_OUTPUT_TYPE", "TEXT").upper()

    if log_format_str_text == "DETAILED":
        log_format_str_text = DETAILED_LOG_FORMAT
    elif not log_format_str_text:
        log_format_str_text = DEFAULT_LOG_FORMAT

    log_level = getattr(logging, log_level_str, logging.INFO)
    if not isinstance(log_level, int):
        log_level = logging.INFO

    if log_output_type == "JSON":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(log_format_str_text)

    handlers = []
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    if log_file:
        try:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, mode="a")
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except OSError:
            pass

    logging.basicConfig(level=log_level, handlers=handlers, force=True)
    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_with_context(level: str, message: str, context: Dict[str, Any]) -> None:
    logger = get_logger(__name__)
    log_method = getattr(logger, level.lower(), logger.info)
    extra = {"context": context}
    if hasattr(_correlation_context, "correlation_id"):
        extra["correlation_id"] = _correlation_context.correlation_id
    log_method(message, extra=extra)


def create_correlation_id() -> str:
    return str(uuid.uuid4())


_correlation_context = threading.local()


class LogContext:
    def __init__(self, correlation_id: Optional[str] = None, additional_context: Optional[Dict[str, Any]] = None):
        self.correlation_id = correlation_id or create_correlation_id()
        self.additional_context = additional_context or {}
        self.previous_context = getattr(_correlation_context, 'correlation_id', None)

    def __enter__(self):
        _correlation_context.correlation_id = self.correlation_id
        _correlation_context.additional_context = self.additional_context
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_context is not None:
            _correlation_context.correlation_id = self.previous_context
        elif hasattr(_correlation_context, 'correlation_id'):
            delattr(_correlation_context, 'correlation_id')


class PerformanceLogger:
    def __init__(self, logger_name: str = "performance"):
        self.logger = get_logger(logger_name)
        self._timers: Dict[str, float] = {}

    def start_timer(self, operation: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._timers[operation] = time.time()
        self.logger.debug(f"Started timing: {operation}", extra={"operation": operation, "context": context or {}})

    def end_timer(self, operation: str, context: Optional[Dict[str, Any]] = None) -> float:
        if operation not in self._timers: return 0.0
        start_time = self._timers.pop(operation)
        duration = time.time() - start_time
        self.logger.info(f"Operation completed: {operation}", extra={"operation": operation, "duration_seconds": duration, "context": context or {}})
        return duration

    @contextmanager
    def time_operation(self, operation: str, context: Optional[Dict[str, Any]] = None):
        self.start_timer(operation, context)
        try: yield
        finally: self.end_timer(operation, context)

    def log_metric(self, name: str, value: Any, unit: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        extra = {"metric_name": name, "metric_value": value, "context": context or {}}
        if unit: extra["metric_unit"] = unit
        self.logger.info(f"Metric: {name} = {value}", extra=extra)


class AuditLogger:
    def __init__(self, logger_name: str = "audit", log_file: Optional[str] = None):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        formatter = JSONFormatter()
        if log_file:
            handler = logging.FileHandler(log_file, mode='a')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def log(self, actor: str, action: str, resource: str, outcome: str = "success", details: Optional[Dict[str, Any]] = None) -> None:
        audit_record = {"audit_id": str(uuid.uuid4()), "timestamp": datetime.now().isoformat(), "actor": actor, "action": action, "resource": resource, "outcome": outcome, "details": details or {}}
        self.logger.info(f"AUDIT: {actor} {action} {resource} -> {outcome}", extra={"audit": audit_record})
        
    def log_access(self, actor: str, resource: str, access_type: str = "read", granted: bool = True) -> None:
        self.log(actor=actor, action=f"access:{access_type}", resource=resource, outcome="granted" if granted else "denied")
