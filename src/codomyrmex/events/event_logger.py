"""Event Logger for Codomyrmex Event System

This module provides logging capabilities for events, including structured logging,
event history, and monitoring dashboards.
"""

import json
import logging
import threading
from collections import defaultdict, deque
from datetime import datetime
from typing import Any

# Import logger config
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

from .event_bus import EventBus, get_event_bus
from .event_schema import Event, EventType


class EventLogEntry:
    def __init__(self, event: Event, handler_count: int = 0, processing_time: float | None = None):
        self.event = event
        self.timestamp = datetime.now()
        self.handler_count = handler_count
        self.processing_time = processing_time
        self.event_id = event.event_id

    def to_dict(self) -> dict[str, Any]:
        etype = self.event.event_type.value if hasattr(self.event.event_type, 'value') else str(self.event.event_type)
        priority = self.event.priority.value if hasattr(self.event.priority, 'value') else str(self.event.priority)
        return {
            'event_id': self.event_id,
            'event_type': etype,
            'priority': priority,
            'timestamp': self.timestamp.isoformat(),
            'handler_count': self.handler_count,
            'processing_time': self.processing_time,
            'source': self.event.source,
            'data': self.event.data,
            'metadata': self.event.metadata
        }


class EventLogger:
    def __init__(self, max_entries: int = 10000, event_bus: EventBus | None = None):
        self.max_entries = max_entries
        self.event_bus = event_bus or get_event_bus()
        self.entries: deque[EventLogEntry] = deque(maxlen=max_entries)
        self.event_counts: dict[str, int] = defaultdict(int)
        self.error_counts: dict[str, int] = defaultdict(int)
        self.processing_times: dict[str, list[float]] = defaultdict(list)
        self.lock = threading.Lock()
        self.event_bus.subscribe(["*"], self.log_event)

    def log_event(self, event: Event, handler_count: int = 0, processing_time: float | None = 0.0) -> None:
        with self.lock:
            entry = EventLogEntry(event, handler_count, processing_time)
            self.entries.append(entry)
            etype = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)
            self.event_counts[etype] += 1
            if "error" in etype.lower():
                self.error_counts[etype] += 1
            self.processing_times[etype].append(processing_time or 0.0)

    def get_event_statistics(self) -> dict[str, Any]:
        with self.lock:
            return {
                "total_events": sum(self.event_counts.values()),
                "event_counts": dict(self.event_counts),
                "error_counts": dict(self.error_counts)
            }

    def get_events(self, event_type: str | None = None, start_time=None, end_time=None) -> list[EventLogEntry]:
        with self.lock:
            res = list(self.entries)
            if event_type:
                res = [e for e in res if (e.event.event_type.value if hasattr(e.event.event_type, 'value') else str(e.event.event_type)) == event_type]
            if start_time: res = [e for e in res if e.timestamp >= start_time]
            if end_time: res = [e for e in res if e.timestamp <= end_time]
            return res

    def get_events_by_type(self, event_type: EventType | str) -> list[EventLogEntry]:
        t = event_type.value if hasattr(event_type, 'value') else str(event_type)
        return self.get_events(event_type=t)

    def get_error_events(self) -> list[EventLogEntry]:
        with self.lock:
            return [e for e in self.entries if "error" in (e.event.event_type.value if hasattr(e.event.event_type, 'value') else str(e.event.event_type)).lower()]

    def get_events_in_time_range(self, start, end) -> list[EventLogEntry]:
        return self.get_events(start_time=start, end_time=end)

    def get_recent_events(self, limit: int = 50) -> list[EventLogEntry]:
        with self.lock: return list(self.entries)[-limit:]

    def clear(self) -> None:
        with self.lock:
            self.entries.clear()
            self.event_counts.clear()
            self.error_counts.clear()
            self.processing_times.clear()


    def get_performance_report(self) -> dict[str, Any]:
        with self.lock:
            total_time = sum(sum(t) for t in self.processing_times.values())
            total_count = sum(len(t) for t in self.processing_times.values())
            report = {
                "event_statistics": dict(self.event_counts),
                "total_processing_time": total_time,
                "average_processing_time_per_event": total_time / total_count if total_count > 0 else 0
            }
            return report

    def export_logs(self, path: str, format: str = 'json') -> None:
        with self.lock:
            data = [e.to_dict() for e in self.entries]
            if format == 'json':
                with open(path, 'w') as f: json.dump(data, f)
            else:
                with open(path, 'w') as f: f.write("id,type\n" + "\n".join([f"{e['event_id']},{e['event_type']}" for e in data]))


_logger = None
def get_event_logger():
    global _logger
    if _logger is None: _logger = EventLogger()
    return _logger

def get_event_stats(): return get_event_logger().get_event_statistics()
def get_recent_events(limit=50): return get_event_logger().get_recent_events(limit)
def get_events(**kwargs): return get_event_logger().get_events(**kwargs)
def generate_performance_report(): return get_event_logger().get_performance_report()
def log_event_to_monitoring(e, c=0, t=0): get_event_logger().log_event(e, c, t)
def export_event_logs(p, f='json'): get_event_logger().export_logs(p, f)
