"""Immutable audit logger for security events.

Provides:
- AuditLogger: structured logging for security and compliance events
- Event severity levels, category filtering, and retention
- Query by user, event type, time range, and status
- Export to JSON Lines format
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from ..formatters import JSONFormatter


@dataclass
class AuditRecord:
    """An immutable audit record."""

    event_type: str
    user_id: str
    status: str = "success"  # success, failure, denied
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    severity: str = "info"  # info, warning, critical
    category: str = "general"  # auth, access, admin, data, system

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "event_type": self.event_type,
            "user_id": self.user_id,
            "status": self.status,
            "details": self.details,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "category": self.category,
        }

    def to_json(self) -> str:
        """to Json ."""
        return json.dumps(self.to_dict())


class AuditLogger:
    """Specialized logger for recording immutable security and audit events.

    Provides structured audit logging with event types, severity levels,
    category filtering, and queryable history.

    Example::

        audit = AuditLogger()
        audit.log_event("login", "user_123", details={"ip": "192.168.1.1"})
        audit.log_event("file_access", "user_456", status="denied",
                        severity="warning", category="access")
        recent = audit.query(user_id="user_123")
    """

    def __init__(self, name: str = "codomyrmex.audit", max_records: int = 10000) -> None:
        """Initialize this instance."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self._records: list[AuditRecord] = []
        self._max_records = max_records

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)

    def log_event(
        self,
        event_type: str,
        user_id: str,
        details: dict[str, Any] | None = None,
        status: str = "success",
        severity: str = "info",
        category: str = "general",
    ) -> AuditRecord:
        """Record an audit event with structured data.

        Args:
            event_type: Type of event (e.g., "login", "file_access").
            user_id: User or entity identifier.
            details: Additional event context.
            status: Outcome (success, failure, denied).
            severity: Event severity (info, warning, critical).
            category: Event category (auth, access, admin, data, system).

        Returns:
            The created AuditRecord.
        """
        record = AuditRecord(
            event_type=event_type,
            user_id=user_id,
            status=status,
            details=details or {},
            severity=severity,
            category=category,
        )
        self._records.append(record)

        # Trim if over max
        if len(self._records) > self._max_records:
            self._records = self._records[-self._max_records:]

        extra = record.to_dict()
        self.logger.info("Audit event: %s", event_type, extra={"extra": extra})
        return record

    # ── Query ───────────────────────────────────────────────────────

    def query(
        self,
        user_id: str | None = None,
        event_type: str | None = None,
        status: str | None = None,
        severity: str | None = None,
        category: str | None = None,
        since: float | None = None,
        limit: int = 100,
    ) -> list[AuditRecord]:
        """Query audit records with optional filters."""
        results = self._records
        if user_id:
            results = [r for r in results if r.user_id == user_id]
        if event_type:
            results = [r for r in results if r.event_type == event_type]
        if status:
            results = [r for r in results if r.status == status]
        if severity:
            results = [r for r in results if r.severity == severity]
        if category:
            results = [r for r in results if r.category == category]
        if since:
            results = [r for r in results if r.timestamp >= since]
        return results[-limit:]

    def count_by_type(self) -> dict[str, int]:
        """Count records by event type."""
        counts: dict[str, int] = {}
        for r in self._records:
            counts[r.event_type] = counts.get(r.event_type, 0) + 1
        return counts

    def count_by_user(self) -> dict[str, int]:
        """Count records by user."""
        counts: dict[str, int] = {}
        for r in self._records:
            counts[r.user_id] = counts.get(r.user_id, 0) + 1
        return counts

    def failures(self, limit: int = 50) -> list[AuditRecord]:
        """Get recent failure/denied events."""
        return [r for r in self._records if r.status in ("failure", "denied")][-limit:]

    @property
    def record_count(self) -> int:
        """record Count ."""
        return len(self._records)

    def export_jsonl(self) -> str:
        """Export all records as JSON Lines."""
        return "\n".join(r.to_json() for r in self._records)

    def clear(self) -> None:
        """Clear all records."""
        self._records.clear()

    def summary(self) -> dict[str, Any]:
        """Summary statistics."""
        return {
            "total_records": self.record_count,
            "by_type": self.count_by_type(),
            "by_status": {
                "success": sum(1 for r in self._records if r.status == "success"),
                "failure": sum(1 for r in self._records if r.status == "failure"),
                "denied": sum(1 for r in self._records if r.status == "denied"),
            },
        }
