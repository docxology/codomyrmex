# audit

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Audit logging and event tracking for the security module. Records structured security-relevant events (authentication, data access, permission changes, admin actions) with SHA-256 integrity signatures. Supports pluggable storage backends including an in-memory store with configurable retention and a file-based JSONL store, plus convenience methods for common event patterns.

## Key Exports

- **`AuditEventType`** -- Enum of audit event categories: AUTH_LOGIN, AUTH_LOGOUT, AUTH_FAILED, DATA_ACCESS, DATA_CREATE, DATA_UPDATE, DATA_DELETE, PERMISSION_CHANGE, CONFIG_CHANGE, SYSTEM_ERROR, ADMIN_ACTION
- **`AuditSeverity`** -- Enum of event severity levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **`AuditEvent`** -- Dataclass representing an audit log entry with actor, resource, IP address, details, timestamp, and a SHA-256 signature property for integrity verification
- **`AuditStore`** -- Abstract base class defining the store/query interface for audit event persistence
- **`InMemoryAuditStore`** -- Thread-safe in-memory audit store with configurable max event retention (default 10,000)
- **`FileAuditStore`** -- File-based audit store that appends events as JSONL and supports filtered queries by time range, event type, and actor
- **`AuditLogger`** -- Main audit logging service with auto-generated event IDs, pluggable store backend, and convenience methods: `log()`, `log_login()`, `log_data_access()`, `log_admin_action()`, and `query()`

## Directory Contents

- `__init__.py` - All audit classes, enums, dataclasses, and storage backends
- `README.md` - This file
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI algorithm context
- `py.typed` - PEP 561 typing marker

## Navigation

- **Parent Module**: [security](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
