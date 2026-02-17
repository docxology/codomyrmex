from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from codomyrmex.logging_monitoring.logger_config import get_logger

"""Physical surveillance monitoring."""

logger = get_logger(__name__)


class EventType(Enum):
    """Types of physical security events."""
    ACCESS = "access"
    MOVEMENT = "movement"
    ALARM = "alarm"
    INTRUSION = "intrusion"
    TAILGATING = "tailgating"
    MAINTENANCE = "maintenance"
    ENVIRONMENTAL = "environmental"
    EMERGENCY = "emergency"


@dataclass
class PhysicalEvent:
    """Represents a physical security event."""

    event_id: str
    event_type: str  # access, movement, alarm, etc.
    location: str
    timestamp: datetime
    description: str
    severity: str  # low, medium, high, critical


class SurveillanceMonitor:
    """Monitors physical security events."""

    def __init__(self):

        self.events: list[PhysicalEvent] = []
        logger.info("SurveillanceMonitor initialized")

    def log_event(
        self,
        event_type: str,
        location: str,
        description: str,
        severity: str = "medium",
    ) -> PhysicalEvent:
        """Log a physical security event."""
        event = PhysicalEvent(
            event_id=f"event_{len(self.events)}",
            event_type=event_type,
            location=location,
            timestamp=datetime.now(),
            description=description,
            severity=severity,
        )
        self.events.append(event)
        logger.info(f"Logged {severity} event: {event_type} at {location}")
        return event

    def monitor_physical_access(self, location: str, user_id: str) -> PhysicalEvent:
        """Monitor physical access event."""
        return self.log_event(
            event_type="access",
            location=location,
            description=f"Physical access by {user_id}",
            severity="low",
        )

    def get_events(
        self,
        location: str | None = None,
        severity: str | None = None,
        event_type: str | None = None,
    ) -> list[PhysicalEvent]:
        """Filter events by location, severity, and/or event type."""
        results = self.events

        if location is not None:
            results = [e for e in results if e.location == location]

        if severity is not None:
            results = [e for e in results if e.severity == severity]

        if event_type is not None:
            results = [e for e in results if e.event_type == event_type]

        return results

    def get_recent_events(self, count: int = 10) -> list[PhysicalEvent]:
        """Return the last N events."""
        return self.events[-count:]


def monitor_physical_access(
    location: str,
    user_id: str,
    monitor: SurveillanceMonitor | None = None,
) -> PhysicalEvent:
    """Monitor physical access."""
    if monitor is None:
        monitor = SurveillanceMonitor()
    return monitor.monitor_physical_access(location, user_id)


def log_physical_event(
    event_type: str,
    location: str,
    description: str,
    severity: str = "medium",
    monitor: SurveillanceMonitor | None = None,
) -> PhysicalEvent:
    """Log a physical event."""
    if monitor is None:
        monitor = SurveillanceMonitor()
    return monitor.log_event(event_type, location, description, severity)

