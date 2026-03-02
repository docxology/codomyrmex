# Agent Guidelines - Logging Monitoring

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Centralized logging with structured output, rotation, and audit trails.

## Key Classes

- **get_logger(name)** — Get configured logger
- **configure_logging(config)** — Set logging configuration
- **JSONFormatter** — Structured JSON log output
- **LogRotator** — Log file rotation
- **AuditLogger** — Security audit logging

## Agent Instructions

1. **Use structured** — Prefer JSON for machine parsing
2. **Add context** — Include request_id, user_id in logs
3. **Set levels correctly** — DEBUG for dev, WARNING for prod
4. **Rotate logs** — Use `LogRotator` for long-running
5. **Audit sensitive** — Use `AuditLogger` for security events

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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `logging_format_structured`; structured log emission, monitoring integration, alert configuration | TRUSTED |
| **Architect** | Read + Design | Log format review, observability architecture design | OBSERVED |
| **QATester** | Validation | Log output validation, structured log correctness, monitoring pipeline health checks | OBSERVED |

### Engineer Agent
**Use Cases**: Emitting structured logs during EXECUTE phase, configuring monitoring integrations, alerting setup.

### Architect Agent
**Use Cases**: Designing observability strategy, reviewing log schema, setting alert thresholds.

### QATester Agent
**Use Cases**: Validating log format compliance, verifying monitoring pipeline during VERIFY phase.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
