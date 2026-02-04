# Security Audit Submodule

**Version**: v0.1.0 | **Source**: [`src/codomyrmex/security/audit/__init__.py`](../../../../src/codomyrmex/security/audit/__init__.py)

## Overview

Audit logging and event tracking with pluggable storage backends. Provides typed audit events with 11 event types, 5 severity levels, SHA-256 integrity signatures, and both in-memory and file-based storage.

## Components

| Class | Description |
|-------|-------------|
| `AuditLogger` | Main audit logging service. Generates unique event IDs, stores events, provides convenience methods for common operations |
| `AuditEvent` | Dataclass representing an audit event with SHA-256 `signature` property for integrity verification |
| `AuditStore` | Abstract base class for audit storage backends |
| `InMemoryAuditStore` | Thread-safe in-memory storage with configurable max events (default: 10,000) |
| `FileAuditStore` | Append-only file-based storage with JSON-lines format |

## Enums

### AuditEventType (11 values)
| Value | String |
|-------|--------|
| `AUTH_LOGIN` | `auth.login` |
| `AUTH_LOGOUT` | `auth.logout` |
| `AUTH_FAILED` | `auth.failed` |
| `DATA_ACCESS` | `data.access` |
| `DATA_CREATE` | `data.create` |
| `DATA_UPDATE` | `data.update` |
| `DATA_DELETE` | `data.delete` |
| `PERMISSION_CHANGE` | `permission.change` |
| `CONFIG_CHANGE` | `config.change` |
| `SYSTEM_ERROR` | `system.error` |
| `ADMIN_ACTION` | `admin.action` |

### AuditSeverity (5 values)
`DEBUG` | `INFO` | `WARNING` | `ERROR` | `CRITICAL`

## Usage

```python
from codomyrmex.security.audit import (
    AuditLogger, AuditEventType, AuditSeverity,
    InMemoryAuditStore, FileAuditStore,
)

# Basic usage (in-memory store)
audit = AuditLogger()
event = audit.log(
    event_type=AuditEventType.AUTH_LOGIN,
    action="user_login",
    actor="user@example.com",
    ip_address="192.168.1.1",
    details={"method": "password"},
)
print(f"Event signature: {event.signature}")

# Convenience methods
audit.log_login("admin@example.com", ip_address="10.0.0.1", success=True)
audit.log_data_access("user@example.com", resource="users_table", resource_id="123")
audit.log_admin_action("admin@example.com", "reset_password", details={"target": "user123"})

# Query events
events = audit.query(actor="admin@example.com", event_type=AuditEventType.ADMIN_ACTION)

# File-based storage
file_store = FileAuditStore("/var/log/audit.jsonl")
audit = AuditLogger(store=file_store)
```

## Thread Safety

Both `InMemoryAuditStore` and `FileAuditStore` use `threading.Lock` for all write operations. `AuditLogger` uses a lock for event ID generation.

## Event Integrity

Each `AuditEvent` computes a `signature` property using SHA-256 over `id:event_type:action:timestamp`, returning the first 16 hex characters. This enables tamper detection for stored events.

## Dependencies

No external dependencies. Uses only Python standard library (`json`, `threading`, `hashlib`, `pathlib`, `dataclasses`, `enum`, `abc`).

## Tests

[`src/codomyrmex/tests/unit/security/audit/test_audit.py`](../../../../src/codomyrmex/tests/unit/security/audit/test_audit.py)

## Navigation

- **Parent**: [Security Module](../README.md)
- **Source**: [`src/codomyrmex/security/audit/`](../../../../src/codomyrmex/security/audit/)
