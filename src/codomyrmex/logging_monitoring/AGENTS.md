# Agent Guidelines - Logging Monitoring

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Centralized structured logging infrastructure for all Codomyrmex modules and PAI agents. Provides JSON-formatted log emission, correlation ID propagation, audit trails, log rotation, and monitoring integration. Every PAI Algorithm phase emits structured logs via `logging_format_structured`; the LEARN phase archives logs for retrospective analysis. Use this module to add observability to any component.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `setup_logging`, `get_logger` |
| `core/` | `LogContext`, `log_with_context`, `create_correlation_id` |
| `formatters/structured_formatter.py` | `StructuredFormatter`, `LogLevel`, `LogContext`, `StructuredLogEntry` |
| `handlers/` | `LogRotationManager`, `PerformanceLogger` |
| `audit/` | `AuditLogger` for immutable security/audit events |
| `mcp_tools.py` | Exposes `logging_format_structured` as MCP tool |

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `logging_format_structured` | Format a log entry as structured JSON for pipeline ingestion. Accepts level, message, module, correlation_id, fields. | SAFE |

## Agent Instructions

1. **Use structured** — Prefer JSON for machine parsing; pass `fields={"key": "val"}` for metadata
2. **Add context** — Include `correlation_id` for request tracing across module boundaries
3. **Set levels correctly** — DEBUG for dev, WARNING for prod; never log credentials or PII
4. **Rotate logs** — Use `LogRotationManager` for long-running processes
5. **Audit sensitive** — Use `AuditLogger` for security events; audit logs are immutable

## Common Patterns

```python
from codomyrmex.logging_monitoring import (
    get_logger, configure_logging, AuditLogger
)

# Configure logging
configure_logging({
    "level": "INFO",
    "format": "json",
    "output": ["console", "file"]
})

# Get module logger
log = get_logger("my_module")
log.info("Processing started", extra={"request_id": req_id})
log.error("Failed to process", extra={"error": str(e)})

# Audit logging
audit = AuditLogger("auth")
audit.log_event("login", user_id=user.id, success=True)
audit.log_event("access_denied", user_id=user.id, resource="admin")
```

## Testing Patterns

```python
# Verify logger creation
log = get_logger("test")
assert log is not None
assert hasattr(log, "info")

# Verify JSON formatting
from codomyrmex.logging_monitoring import JSONFormatter
fmt = JSONFormatter()
record = create_log_record("test")
output = fmt.format(record)
import json
assert json.loads(output)  # Valid JSON
```

## Operating Contracts

**DO:**
- Call `setup_logging()` once at application start before any other logging
- Include `correlation_id` in every log emitted within a request or workflow boundary
- Use `AuditLogger` for all security-sensitive events (auth, data access, config changes)
- Use `logging_format_structured` MCP tool to emit logs from agent workflows

**DO NOT:**
- Log secrets, API keys, passwords, or PII in any field
- Create module-level loggers before `setup_logging()` is called
- Use Python's built-in `print()` for any operational output — use `get_logger()` instead

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `logging_format_structured`; structured log emission, monitoring integration, alert configuration | TRUSTED |
| **Architect** | Read + Design | Log format review, observability architecture design | OBSERVED |
| **QATester** | Validation | Log output validation, structured log correctness, monitoring pipeline health checks | OBSERVED |
| **Researcher** | Read-only | Inspect log output during analysis; use `logging_format_structured` for research audit trail | SAFE |

### Engineer Agent
**Use Cases**: Emitting structured logs during EXECUTE phase, configuring monitoring integrations, alerting setup.

### Architect Agent
**Use Cases**: Designing observability strategy, reviewing log schema, setting alert thresholds.

### QATester Agent
**Use Cases**: Validating log format compliance, verifying monitoring pipeline during VERIFY phase.

### Researcher Agent
**Use Cases**: Creating an audit trail of research operations, inspecting log output for debugging analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/logging_monitoring.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/logging_monitoring.cursorrules)
