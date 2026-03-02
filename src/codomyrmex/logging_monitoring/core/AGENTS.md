# Codomyrmex Agents -- src/codomyrmex/logging_monitoring/core

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Centralized logging configuration, correlation ID propagation, log aggregation,
and audit trail support. This is the foundation layer that all other modules
depend on for structured logging output.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `logger_config.py` | `setup_logging()` | Configure logging system from environment variables (level, file, format, JSON/text) |
| `logger_config.py` | `get_logger()` | Get a named logger instance inheriting root config |
| `logger_config.py` | `LogContext` | Context manager for correlation ID scoping with nesting support |
| `logger_config.py` | `JSONFormatter` | JSON formatter for structured log output |
| `logger_config.py` | `AuditLogger` | Security audit logger with actor/action/resource/outcome recording |
| `logger_config.py` | `log_with_context()` | Log a message with attached context dictionary |
| `logger_config.py` | `enable_structured_json()` | Switch a logger to structured JSON output |
| `correlation.py` | `CorrelationFilter` | Logging filter injecting `correlation_id` into every log record |
| `correlation.py` | `with_correlation()` | Context manager that sets/clears correlation IDs |
| `correlation.py` | `enrich_event_data()` | Add correlation ID to event data dicts |
| `correlation.py` | `create_mcp_correlation_header()` | Generate MCP metadata headers with correlation ID |
| `log_aggregator.py` | `LogAggregator` | In-memory log aggregation with search, filtering, and analytics |
| `log_aggregator.py` | `LogRecord` / `LogQuery` / `LogStats` | Data models for aggregated log records, search queries, and statistics |

## Operating Contracts

- `setup_logging()` should be called once at application startup; subsequent calls require `force=True`.
- Environment variables: `CODOMYRMEX_LOG_LEVEL`, `CODOMYRMEX_LOG_FILE`, `CODOMYRMEX_LOG_FORMAT`, `CODOMYRMEX_LOG_OUTPUT_TYPE`.
- Correlation IDs use `contextvars.ContextVar` for async-safe propagation.
- `LogAggregator` caps in-memory records at `max_records` (default 100,000).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `logging_monitoring.audit.audit_logger` (re-exports `AuditLogger`), `logging_monitoring.formatters`, stdlib `logging`, `contextvars`
- **Used by**: Every module in codomyrmex (foundation layer), MCP bridge, EventBus

## Navigation

- **Parent**: [logging_monitoring](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
