# Codomyrmex Agents — src/codomyrmex/security/audit

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Security audit logging with two complementary systems: an event-based `AuditLogger` with pluggable storage backends, and an immutable HMAC-chained `AuditTrail` for tamper-evident agent action recording.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `AuditEventType` | Enum of 11 event types: `AUTH_LOGIN`, `AUTH_LOGOUT`, `AUTH_FAILED`, `DATA_ACCESS`, `DATA_CREATE`, `DATA_UPDATE`, `DATA_DELETE`, `PERMISSION_CHANGE`, `CONFIG_CHANGE`, `SYSTEM_ERROR`, `ADMIN_ACTION` |
| `__init__.py` | `AuditSeverity` | Enum: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `__init__.py` | `AuditEvent` | Dataclass with SHA-256 `.signature` property and `.to_dict()` / `.to_json()` serialization |
| `__init__.py` | `AuditStore` (ABC) | Abstract storage interface: `store()`, `query()` |
| `__init__.py` | `InMemoryAuditStore` | Thread-safe in-memory store with LRU eviction at `max_events` (default 10,000) |
| `__init__.py` | `FileAuditStore` | Thread-safe JSONL append-only file store |
| `__init__.py` | `AuditLogger` | Main service: `log()`, `log_login()`, `log_data_access()`, `log_admin_action()`, `query()` |
| `audit_trail.py` | `AuditEntry` | Dataclass with `previous_hash`, `entry_hash` for chain integrity |
| `audit_trail.py` | `AuditTrail` | Append-only HMAC-SHA256 chained trail: `record()`, `verify_chain()`, `entries_by_actor()`, `to_jsonl()` |

## Operating Contracts

- Both `InMemoryAuditStore` and `FileAuditStore` use `threading.Lock` for safe concurrent writes.
- `AuditTrail` uses HMAC-SHA256 with a configurable `signing_key` (default `b"codomyrmex-audit"`) for chain integrity.
- `verify_chain()` validates the full chain from genesis and returns `False` on any tampered entry.
- `FileAuditStore.query()` performs a full linear scan; no indexing.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging)
- **Used by**: PAI trust gateway audit, agent action tracking, security compliance checks

## Navigation

- **Parent**: [security](../README.md)
- **Root**: [Root](../../../../README.md)
