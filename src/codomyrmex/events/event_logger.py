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

# Import logging
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
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
        return {
            'event_id': self.event_id,
            'event_type': self.event.event_type.value,
            'priority': self.event.priority.value,
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
            start_time = time.time()
            try:
                # Log the event
                self.log_event(event)
            except Exception as e:
                logger.error(f"Error logging event {event.event_id}: {e}")
            finally:
                # Record processing time (approximate)
                processing_time = time.time() - start_time
                # Update the last entry with processing time
                with self.lock:
                    if self.entries:
                        self.entries[-1].processing_time = processing_time

        # Subscribe to all event types
        self.subscriber_id = subscribe_to_events(
            event_types=[],  # Empty list means all events
            handler=log_event_handler,
            subscriber_id="event_logger",
            priority=-1000  # Low priority to run after other handlers
        )

    def log_event(self, event: Event, handler_count: int = 0,
                  processing_time: Optional[float] = None) -> None:
        """
        Log an event.

        Args:
            event: Event to log
            handler_count: Number of handlers that processed the event
            processing_time: Time taken to process the event
        """
        entry = EventLogEntry(event, handler_count, processing_time)

        with self.lock:
            self.entries.append(entry)
            self.event_counts[event.event_type.value] += 1

            # Track errors
            if event.event_type in [EventType.ANALYSIS_ERROR, EventType.BUILD_ERROR,
                                  EventType.SYSTEM_ERROR, EventType.MODULE_ERROR]:
                self.error_counts[event.event_type.value] += 1

            # Track processing times
            if processing_time is not None:
                self.processing_times[event.event_type.value].append(processing_time)
                # Keep only last 100 processing times per event type
                if len(self.processing_times[event.event_type.value]) > 100:
                    self.processing_times[event.event_type.value].pop(0)

        # Log to standard logging system
        log_level = self._get_log_level(event)
        log_message = f"Event: {event.event_type.value} (ID: {event.event_id})"

        if event.source:
            log_message += f" from {event.source}"

        if event.data:
            # Truncate data if too long
            data_str = str(event.data)
            if len(data_str) > 200:
                data_str = data_str[:200] + "..."
            log_message += f" - {data_str}"

        logger.log(log_level, log_message)

    def _get_log_level(self, event: Event) -> int:
        """
        Get appropriate log level for an event.

        Args:
            event: Event to get log level for

        Returns:
            Logging level
        """
        if event.priority == EventPriority.CRITICAL:
            return logging.CRITICAL
        elif event.priority == EventPriority.ERROR:
            return logging.ERROR
        elif event.priority == EventPriority.WARNING:
            return logging.WARNING
        elif event.priority == EventPriority.DEBUG:
            return logging.DEBUG
        else:
            return logging.INFO

    def get_recent_events(self, limit: int = 100, event_type: Optional[EventType] = None) -> List[EventLogEntry]:
        """
        Get recent events.

        Args:
            limit: Maximum number of events to return
            event_type: Filter by event type

        Returns:
            List of recent event log entries
        """
        with self.lock:
            entries = list(self.entries)

        if event_type:
            entries = [e for e in entries if e.event.event_type == event_type]

        return entries[-limit:] if entries else []

    def get_event_statistics(self) -> Dict[str, Any]:
        """
        Get event statistics.

        Returns:
            Dictionary with event statistics
        """
        with self.lock:
            stats = {
                'total_events': len(self.entries),
                'event_counts': dict(self.event_counts),
                'error_counts': dict(self.error_counts),
                'unique_event_types': len(self.event_counts),
                'processing_times': {}
            }

            # Calculate average processing times
            for event_type, times in self.processing_times.items():
                if times:
                    stats['processing_times'][event_type] = {
                        'average': sum(times) / len(times),
                        'min': min(times),
                        'max': max(times),
                        'count': len(times)
                    }

        return stats

    def get_events_by_type(self, event_type: EventType, limit: int = 100) -> List[EventLogEntry]:
        """
        Get events of a specific type.

        Args:
            event_type: Event type to filter by
            limit: Maximum number of events to return

        Returns:
            List of events of the specified type
        """
        return self.get_recent_events(limit, event_type)

    def get_error_events(self, limit: int = 100) -> List[EventLogEntry]:
        """
        Get error events.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of error events
        """
        with self.lock:
            error_entries = [e for e in self.entries
                           if e.event.event_type in [EventType.ANALYSIS_ERROR,
                                                   EventType.BUILD_ERROR,
                                                   EventType.SYSTEM_ERROR,
                                                   EventType.MODULE_ERROR]]

        return error_entries[-limit:] if error_entries else []

    def get_events_in_time_range(self, start_time: datetime, end_time: datetime,
                               event_type: Optional[EventType] = None) -> List[EventLogEntry]:
        """
        Get events within a time range.

        Args:
            start_time: Start of time range
            end_time: End of time range
            event_type: Optional event type filter

        Returns:
            List of events in the time range
        """
        with self.lock:
            entries = [e for e in self.entries
                      if start_time <= e.timestamp <= end_time]

        if event_type:
            entries = [e for e in entries if e.event.event_type == event_type]

        return entries

    def clear_logs(self) -> None:
        """Clear all logged events."""
        with self.lock:
            self.entries.clear()
            self.event_counts.clear()
            self.error_counts.clear()
            self.processing_times.clear()

        logger.info("Event logs cleared")

    def export_logs(self, filepath: str, format: str = 'json') -> None:
        """
        Export logs to a file.

        Args:
            filepath: Path to export file
            format: Export format ('json' or 'csv')
        """
        with self.lock:
            entries = list(self.entries)

        if format.lower() == 'json':
            data = [entry.to_dict() for entry in entries]
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)

        elif format.lower() == 'csv':
            import csv
            with open(filepath, 'w', newline='') as f:
                if entries:
                    writer = csv.DictWriter(f, fieldnames=entries[0].to_dict().keys())
                    writer.writeheader()
                    writer.writerows(entry.to_dict() for entry in entries)

        logger.info(f"Exported {len(entries)} log entries to {filepath}")

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate a performance report based on logged events.

        Returns:
            Performance report dictionary
        """
        stats = self.get_event_statistics()

        # Calculate additional metrics
        total_processing_time = 0
        total_events_with_timing = 0

        with self.lock:
            for entry in self.entries:
                if entry.processing_time is not None:
                    total_processing_time += entry.processing_time
                    total_events_with_timing += 1

        report = {
            'event_statistics': stats,
            'total_processing_time': total_processing_time,
            'average_processing_time_per_event': (
                total_processing_time / total_events_with_timing
                if total_events_with_timing > 0 else 0
            ),
            'events_with_timing_info': total_events_with_timing,
            'error_rate': (
                sum(stats['error_counts'].values()) / stats['total_events']
                if stats['total_events'] > 0 else 0
            ),
            'generated_at': datetime.now().isoformat()
        }

        return report

    def shutdown(self) -> None:
        """Shutdown the event logger."""
        if self.subscriber_id:
            from .event_bus import unsubscribe_from_events
            unsubscribe_from_events(self.subscriber_id)
            self.subscriber_id = None

        logger.info("EventLogger shutdown")


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
