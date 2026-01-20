"""Immutable audit logger for security events."""

import logging
from typing import Any, Dict, Optional
from .json_formatter import JSONFormatter

class AuditLogger:
    """Specialized logger for recording immutable security and audit events."""
    
    def __init__(self, name: str = "codomyrmex.audit"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Ensure we have a handler for audit
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)

    def log_event(self, event_type: str, user_id: str, details: Dict[str, Any], status: str = "success"):
        """Record an audit event."""
        extra = {
            "event_type": event_type,
            "user_id": user_id,
            "status": status,
            "details": details
        }
        self.logger.info(f"Audit event: {event_type}", extra=extra)
