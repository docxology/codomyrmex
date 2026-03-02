# Codomyrmex Agents -- src/codomyrmex/logging_monitoring/audit

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides immutable audit logging for security and compliance events with
structured records, queryable history, severity levels, category filtering,
and JSON Lines export. Designed for tracking authentication, access control,
and administrative actions.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `audit_logger.py` | `AuditRecord` | Immutable dataclass for a single audit event (event_type, user_id, status, severity, category) |
| `audit_logger.py` | `AuditLogger` | Structured audit logger with event recording, multi-field querying, aggregation, and JSONL export |

## Operating Contracts

- `AuditLogger` maintains an in-memory record store capped at `max_records` (default 10000); oldest records are trimmed on overflow.
- Records are immutable after creation -- no update or delete operations on individual records.
- Status values: `success`, `failure`, `denied`. Severity values: `info`, `warning`, `critical`.
- Category values: `general`, `auth`, `access`, `admin`, `data`, `system`.
- `query()` supports filtering by user_id, event_type, status, severity, category, and time range.
- Output is formatted via `JSONFormatter` from sibling `formatters/` module.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `logging_monitoring.formatters.JSONFormatter`, stdlib `json`, `logging`, `time`, `dataclasses`
- **Used by**: `logging_monitoring.core.logger_config` (re-exports `AuditLogger`), security modules, PAI trust gateway

## Navigation

- **Parent**: [logging_monitoring](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
