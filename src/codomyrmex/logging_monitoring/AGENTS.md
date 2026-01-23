# Codomyrmex Agents — src/codomyrmex/logging_monitoring

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Foundation Layer module providing centralized logging and monitoring infrastructure. All other Codomyrmex modules depend on this module for consistent logging output (JSON/Text), session-based correlation, and structured telemetry.

## Active Components

### Primary Files

- `logger_config.py` - Primary configuration logic and logger factory
  - Key Functions: `setup_logging(config: dict = None)`, `get_logger(name: str)`
- `json_formatter.py` - Standardized `JSONFormatter` for structured output
  - Key Classes: `JSONFormatter`
- `audit.py` - Domain-specific audit logging
  - Key Classes: `AuditLogger`
- `rotation.py` - Log file rotation management
  - Key Classes: `RotatingFileHandler`

### Configuration

- `SPEC.md` - Functional specification (v0.1.0 Unified Streamline)
- `requirements.txt` - Module dependencies

## Key Classes and Functions

| Class/Function | Purpose |
| :--- | :--- |
| `setup_logging(config)` | Initialize logging system (call once at startup) |
| `get_logger(name)` | Get configured logger for a module |
| `JSONFormatter` | Format log records as JSON |
| `AuditLogger` | Domain-specific audit trail logging |

## Environment Configuration

| Variable | Default | Description |
| :--- | :--- | :--- |
| `CODOMYRMEX_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CODOMYRMEX_LOG_FILE` | None | Path to log file |
| `CODOMYRMEX_LOG_FORMAT` | `standard` | Format type (standard, detailed, json) |

## Operating Contracts

1. **Foundation Status**: This is a Foundation Layer module - no dependencies on other Codomyrmex modules
2. **Early Initialization**: `setup_logging()` must be called early in application startup
3. **Module Loggers**: Each module should get its own logger via `get_logger(__name__)`
4. **Structured Logging**: Use keyword arguments for structured data: `logger.info("event", user_id=123)`
5. **No Circular Dependencies**: This module must not import from other Codomyrmex modules

## Usage Pattern

```python
# Application entry point
from codomyrmex.logging_monitoring import setup_logging
setup_logging()

# In any module
from codomyrmex.logging_monitoring import get_logger
logger = get_logger(__name__)
logger.info("Operation completed", items_processed=42)
```

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules (Foundation Layer)

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| environment_setup | [../environment_setup/AGENTS.md](../environment_setup/AGENTS.md) | Environment validation |
| terminal_interface | [../terminal_interface/AGENTS.md](../terminal_interface/AGENTS.md) | Terminal UI |
| model_context_protocol | [../model_context_protocol/AGENTS.md](../model_context_protocol/AGENTS.md) | MCP standards |

### Related Documentation

- [README.md](README.md) - User documentation
- [SPEC.md](SPEC.md) - Functional specification
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tools
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Code examples
