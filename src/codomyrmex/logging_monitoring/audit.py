"""Immutable audit logger for security events.

This module provides a specialized AuditLogger class for recording security
and compliance-related events. All audit records are immutable and include
structured data for event tracking and forensic analysis.

Example:
    >>> from codomyrmex.logging_monitoring.audit import AuditLogger
    >>> audit = AuditLogger()
    >>> audit.log_event("login", "user_123", {"ip": "192.168.1.1"})
"""

import logging
from typing import Any, Dict, Optional
from .json_formatter import JSONFormatter


class AuditLogger:
    """Specialized logger for recording immutable security and audit events.

    Provides structured audit logging with event type, user identification,
    status tracking, and extensible details. Output is formatted as JSON
    for easy parsing and analysis.

    Attributes:
        logger: The underlying Python logger instance.

    Example:
        >>> audit = AuditLogger("myapp.audit")
        >>> audit.log_event("file_access", "user_456", {"file": "/secret.txt"}, "denied")
    """

    def __init__(self, name: str = "codomyrmex.audit"):
        """Initialize an AuditLogger instance.

        Args:
            name: The logger name in the logging hierarchy.
                Defaults to "codomyrmex.audit".
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Ensure we have a handler for audit
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)

    def log_event(self, event_type: str, user_id: str, details: Dict[str, Any], status: str = "success") -> None:
        """Record an audit event with structured data.

        Creates an immutable audit record containing the event type, user
        identifier, status, and any additional details.

        Args:
            event_type: The type of event being logged (e.g., "login",
                "file_access", "permission_change").
            user_id: The identifier of the user or entity associated with
                the event.
            details: A dictionary of additional event details (e.g.,
                IP address, resource path, action parameters).
            status: The outcome status of the event. Common values include
                "success", "failure", "denied". Defaults to "success".

        Returns:
            None

        Example:
            >>> audit.log_event(
            ...     event_type="password_change",
            ...     user_id="user_789",
            ...     details={"method": "self_service", "mfa_used": True},
            ...     status="success"
            ... )
        """
        extra = {
            "event_type": event_type,
            "user_id": user_id,
            "status": status,
            "details": details
        }
        self.logger.info(f"Audit event: {event_type}", extra=extra)
