# Audit -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Immutable audit logging subsystem for recording security and compliance events
with structured records, multi-field queries, and JSON Lines export.

## Architecture

Uses a dataclass-based `AuditRecord` stored in an in-memory list within
`AuditLogger`. Records are append-only with automatic trimming at capacity.
Log output is delegated to Python's `logging` module with `JSONFormatter`.

## Key Classes

### `AuditRecord`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `event_type` | `str` | -- | Type of event (e.g., "login", "file_access") |
| `user_id` | `str` | -- | User or entity identifier |
| `status` | `str` | `"success"` | Outcome: success, failure, denied |
| `details` | `dict[str, Any]` | `{}` | Additional event context |
| `timestamp` | `float` | `time.time()` | Unix timestamp |
| `severity` | `str` | `"info"` | Severity: info, warning, critical |
| `category` | `str` | `"general"` | Category: general, auth, access, admin, data, system |

### `AuditLogger`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `log_event` | `event_type, user_id, details, status, severity, category` | `AuditRecord` | Record an audit event |
| `query` | `user_id, event_type, status, severity, category, since, limit` | `list[AuditRecord]` | Filter records by multiple criteria |
| `count_by_type` | -- | `dict[str, int]` | Count records by event type |
| `count_by_user` | -- | `dict[str, int]` | Count records by user |
| `failures` | `limit: int` | `list[AuditRecord]` | Get recent failure/denied events |
| `export_jsonl` | -- | `str` | Export all records as JSON Lines |
| `summary` | -- | `dict` | Aggregate statistics (total, by_type, by_status) |
| `clear` | -- | `None` | Clear all records |

## Dependencies

- **Internal**: `logging_monitoring.formatters.JSONFormatter`
- **External**: stdlib (`json`, `logging`, `time`, `dataclasses`)

## Constraints

- Record store is in-memory only -- not persisted to disk by default.
- Max capacity configurable via `max_records` (default 10000); oldest records auto-trimmed.
- Zero-mock: real events only, `NotImplementedError` for unimplemented paths.

## Error Handling

- All events are logged to `logging.getLogger("codomyrmex.audit")`.
- No exceptions raised from `log_event()` under normal operation.
- All errors logged before propagation.
