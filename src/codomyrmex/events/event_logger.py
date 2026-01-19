"""
Event Logger for Codomyrmex Event System

This module provides logging capabilities for events, including structured logging,
event history, and monitoring dashboards.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict, deque
import threading

import logging

# Import logger config
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

from .event_bus import subscribe_to_events, EventBus, get_event_bus
from .event_schema import Event, EventType, EventPriority


class EventLogEntry:
    """
    Represents a logged event entry with metadata.
    """

    def __init__(self, event: Event, handler_count: int = 0,
                 processing_time: Optional[float] = None):
        """
        Initialize an event log entry.

        Args:
            event: The event that was logged
            handler_count: Number of handlers that processed the event
            processing_time: Time taken to process the event (seconds)
        """
        self.event = event
        self.timestamp = datetime.now()
        self.handler_count = handler_count
        self.processing_time = processing_time
        self.event_id = event.event_id

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the log entry to a dictionary.

        Returns:
            Dictionary representation
        """
        priority_val = self.event.priority.value if hasattr(self.event.priority, 'value') else self.event.priority
        return {
            'event_id': self.event_id,
            'event_type': self.event.event_type.value,
            'priority': priority_val,
            'timestamp': self.timestamp.isoformat(),
            'handler_count': self.handler_count,
            'processing_time': self.processing_time,
            'source': self.event.source,
            'data': self.event.data,
            'metadata': self.event.metadata
        }

    def to_json(self) -> str:
        """
        Convert the log entry to JSON.

        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=2, default=str)


class EventLogger:
    """
    Event logger that captures and stores event information for monitoring and debugging.
    """

    def __init__(self, max_entries: int = 10000, event_bus: Optional[EventBus] = None):
        """
        Initialize the event logger.

        Args:
            max_entries: Maximum number of entries to keep in memory
            event_bus: Event bus to subscribe to (uses global if None)
        """
        self.max_entries = max_entries
        self.event_bus = event_bus or get_event_bus()
        self.entries: deque[EventLogEntry] = deque(maxlen=max_entries)
        self.event_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.processing_times: Dict[str, List[float]] = defaultdict(list)
        self.subscriber_id: Optional[str] = None
        self.lock = threading.Lock()

        # Auto-subscribe to all events
        self._subscribe_to_events()

        logger.info(f"EventLogger initialized with max_entries={max_entries}")

    def _subscribe_to_events(self) -> None:
        """Subscribe to all events for logging."""
        def log_event_handler(event: Event) -> None:
            """Internal handler for logging events."""
            start_time = time.time()
            try:
                # Basic logging
                self.log_event(event, processing_time=0.0)
            except Exception as e:
                # Avoid infinite recursion if logging fails
                pass

        # Subscribe with high priority to capture everything
        self.subscriber_id = self.event_bus.subscribe(
            list(EventType), 
            log_event_handler, 
            f"event_logger_{id(self)}", 
            priority=EventPriority.MONITORING
        )

    def log_event(self, event: Event, handler_count: int = 0,
                  processing_time: Optional[float] = None) -> None:
        """Log an event."""
        with self.lock:
            entry = EventLogEntry(event, handler_count, processing_time)
            self.entries.append(entry)
            
            # Update stats
            self.event_counts[event.event_type.value] += 1
            if event.event_type in [EventType.SYSTEM_ERROR, EventType.MODULE_ERROR, EventType.PLUGIN_ERROR]:
                self.error_counts[event.event_type.value] += 1
            
            if processing_time is not None:
                self.processing_times[event.event_type.value].append(processing_time)
                # Keep only last 100 processing times per type
                if len(self.processing_times[event.event_type.value]) > 100:
                    self.processing_times[event.event_type.value].pop(0)

    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event statistics."""
        with self.lock:
            return {
                "total_events": sum(self.event_counts.values()),
                "event_counts": dict(self.event_counts),
                "error_counts": dict(self.error_counts),
                "uptime": "N/A"  # Could track start time
            }

    def get_recent_events(self, limit: int = 50) -> List[EventLogEntry]:
        """Get recent events."""
        with self.lock:
            return list(self.entries)[-limit:]

    def export_logs(self, filepath: str, format: str = 'json') -> None:
        """Export logs to file."""
        with self.lock:
            data = [entry.to_dict() for entry in self.entries]
            
        with open(filepath, 'w') as f:
            if format == 'json':
                json.dump(data, f, indent=2)
            else:
                # Basic CSV or other format
                f.write(str(data))

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report."""
        with self.lock:
            report = {}
            for event_type, times in self.processing_times.items():
                if times:
                    report[event_type] = {
                        "avg": sum(times) / len(times),
                        "max": max(times),
                        "min": min(times),
                        "count": len(times)
                    }
            return report


# Global event logger instance
_event_logger: Optional[EventLogger] = None
_event_logger_lock = threading.Lock()


def get_event_logger() -> EventLogger:
    """
    Get the global event logger instance.

    Returns:
        EventLogger instance
    """
    global _event_logger

    if _event_logger is None:
        with _event_logger_lock:
            if _event_logger is None:
                _event_logger = EventLogger()

    return _event_logger


def log_event_to_monitoring(event: Event, handler_count: int = 0,
                           processing_time: Optional[float] = None) -> None:
    """
    Log an event to the monitoring system.

    Args:
        event: Event to log
        handler_count: Number of handlers that processed the event
        processing_time: Time taken to process the event
    """
    logger = get_event_logger()
    logger.log_event(event, handler_count, processing_time)


# Convenience functions for monitoring
def get_event_stats() -> Dict[str, Any]:
    """
    Get current event statistics.

    Returns:
        Event statistics dictionary
    """
    logger = get_event_logger()
    return logger.get_event_statistics()


def get_recent_events(limit: int = 50) -> List[EventLogEntry]:
    """
    Get recent events.

    Args:
        limit: Maximum number of events to return

    Returns:
        List of recent event log entries
    """
    logger = get_event_logger()
    return logger.get_recent_events(limit)


def export_event_logs(filepath: str, format: str = 'json') -> None:
    """
    Export event logs to a file.

    Args:
        filepath: Path to export file
        format: Export format ('json' or 'csv')
    """
    logger = get_event_logger()
    logger.export_logs(filepath, format)


def generate_performance_report() -> Dict[str, Any]:
    """
    Generate a performance report.

    Returns:
        Performance report dictionary
    """
    logger = get_event_logger()
    return logger.get_performance_report()
