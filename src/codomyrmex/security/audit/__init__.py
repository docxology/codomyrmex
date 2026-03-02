"""
Security Audit Module

Audit logging and event tracking.
"""

__version__ = "0.1.0"

import hashlib
import json
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditEventType(Enum):
    """Types of audit events."""
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_FAILED = "auth.failed"
    DATA_ACCESS = "data.access"
    DATA_CREATE = "data.create"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"
    PERMISSION_CHANGE = "permission.change"
    CONFIG_CHANGE = "config.change"
    SYSTEM_ERROR = "system.error"
    ADMIN_ACTION = "admin.action"


class AuditSeverity(Enum):
    """Severity of audit events."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """An audit log event."""
    id: str
    event_type: AuditEventType
    action: str
    actor: str = "system"
    resource: str = ""
    resource_id: str = ""
    severity: AuditSeverity = AuditSeverity.INFO
    ip_address: str = ""
    user_agent: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def signature(self) -> str:
        """Generate event signature for integrity."""
        content = f"{self.id}:{self.event_type.value}:{self.action}:{self.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.event_type.value,
            "action": self.action,
            "actor": self.actor,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "signature": self.signature,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class AuditStore(ABC):
    """Base class for audit storage."""

    @abstractmethod
    def store(self, event: AuditEvent) -> None:
        """Store an audit event."""
        pass

    @abstractmethod
    def query(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        event_type: AuditEventType | None = None,
        actor: str | None = None,
    ) -> list[AuditEvent]:
        """Query audit events."""
        pass


class InMemoryAuditStore(AuditStore):
    """In-memory audit storage."""

    def __init__(self, max_events: int = 10000):
        """Initialize this instance."""
        self.max_events = max_events
        self._events: list[AuditEvent] = []
        self._lock = threading.Lock()

    def store(self, event: AuditEvent) -> None:
        """Store an event."""
        with self._lock:
            self._events.append(event)
            if len(self._events) > self.max_events:
                self._events = self._events[-self.max_events:]

    def query(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        event_type: AuditEventType | None = None,
        actor: str | None = None,
    ) -> list[AuditEvent]:
        """Query events."""
        results = []
        for event in self._events:
            if start and event.timestamp < start:
                continue
            if end and event.timestamp > end:
                continue
            if event_type and event.event_type != event_type:
                continue
            if actor and event.actor != actor:
                continue
            results.append(event)
        return results

    def get_all(self) -> list[AuditEvent]:
        """Get all events."""
        return list(self._events)

    def clear(self) -> None:
        """Clear all events."""
        with self._lock:
            self._events.clear()


class FileAuditStore(AuditStore):
    """File-based audit storage."""

    def __init__(self, log_path: str):
        """Initialize this instance."""
        self.log_path = Path(log_path)
        self._lock = threading.Lock()

    def store(self, event: AuditEvent) -> None:
        """Store event to file."""
        with self._lock:
            with open(self.log_path, 'a') as f:
                f.write(event.to_json() + '\n')

    def query(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        event_type: AuditEventType | None = None,
        actor: str | None = None,
    ) -> list[AuditEvent]:
        """Query events from file."""
        results = []
        if not self.log_path.exists():
            return results

        with open(self.log_path) as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    event_ts = datetime.fromisoformat(data['timestamp'])

                    if start and event_ts < start:
                        continue
                    if end and event_ts > end:
                        continue
                    if event_type and data['type'] != event_type.value:
                        continue
                    if actor and data['actor'] != actor:
                        continue

                    # Reconstruct event
                    event = AuditEvent(
                        id=data['id'],
                        event_type=AuditEventType(data['type']),
                        action=data['action'],
                        actor=data['actor'],
                        resource=data.get('resource', ''),
                        resource_id=data.get('resource_id', ''),
                        severity=AuditSeverity(data['severity']),
                    )
                    results.append(event)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        return results


class AuditLogger:
    """
    Main audit logging service.

    Usage:
        audit = AuditLogger()

        # Log events
        audit.log(
            event_type=AuditEventType.AUTH_LOGIN,
            action="user_login",
            actor="user@example.com",
            details={"ip": "192.168.1.1"},
        )

        # Query events
        events = audit.query(actor="user@example.com")
    """

    def __init__(self, store: AuditStore | None = None):
        """Initialize this instance."""
        self.store = store or InMemoryAuditStore()
        self._counter = 0
        self._lock = threading.Lock()

    def _generate_id(self) -> str:
        """Generate unique event ID."""
        with self._lock:
            self._counter += 1
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"audit_{ts}_{self._counter}"

    def log(
        self,
        event_type: AuditEventType,
        action: str,
        actor: str = "system",
        resource: str = "",
        resource_id: str = "",
        severity: AuditSeverity = AuditSeverity.INFO,
        ip_address: str = "",
        user_agent: str = "",
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """
        Log an audit event.

        Args:
            event_type: Type of event
            action: Action description
            actor: Who performed the action
            resource: What resource was affected
            resource_id: ID of the resource
            severity: Event severity
            ip_address: Client IP address
            user_agent: Client user agent
            details: Additional details

        Returns:
            The created AuditEvent
        """
        event = AuditEvent(
            id=self._generate_id(),
            event_type=event_type,
            action=action,
            actor=actor,
            resource=resource,
            resource_id=resource_id,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
        )

        self.store.store(event)
        return event

    def log_login(self, actor: str, ip_address: str = "", success: bool = True) -> AuditEvent:
        """Log login attempt."""
        return self.log(
            event_type=AuditEventType.AUTH_LOGIN if success else AuditEventType.AUTH_FAILED,
            action="login_attempt",
            actor=actor,
            ip_address=ip_address,
            severity=AuditSeverity.INFO if success else AuditSeverity.WARNING,
            details={"success": success},
        )

    def log_data_access(
        self,
        actor: str,
        resource: str,
        resource_id: str = "",
    ) -> AuditEvent:
        """Log data access."""
        return self.log(
            event_type=AuditEventType.DATA_ACCESS,
            action="data_access",
            actor=actor,
            resource=resource,
            resource_id=resource_id,
        )

    def log_admin_action(
        self,
        actor: str,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Log admin action."""
        return self.log(
            event_type=AuditEventType.ADMIN_ACTION,
            action=action,
            actor=actor,
            severity=AuditSeverity.WARNING,
            details=details,
        )

    def query(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        event_type: AuditEventType | None = None,
        actor: str | None = None,
    ) -> list[AuditEvent]:
        """Query audit events."""
        return self.store.query(start=start, end=end, event_type=event_type, actor=actor)


__all__ = [
    # Enums
    "AuditEventType",
    "AuditSeverity",
    # Data classes
    "AuditEvent",
    # Stores
    "AuditStore",
    "InMemoryAuditStore",
    "FileAuditStore",
    # Core
    "AuditLogger",
]

from .audit_trail import *  # noqa: E402, F401, F403
