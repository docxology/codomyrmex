"""Audit logging subpackage.

Provides specialized audit logging for security and compliance events.
The AuditLogger class records immutable, structured audit events with
event type, user identification, status, and extensible details.
"""

from .audit_logger import AuditLogger

__all__ = ["AuditLogger"]
