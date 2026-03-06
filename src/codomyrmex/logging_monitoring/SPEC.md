# logging_monitoring - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Foundation module providing centralized logging infrastructure for the Codomyrmex platform. Implements unified logging system with consistent formatting, configurable output destinations, and proper log level management.

## Design Principles

### Modularity

- Self-contained logging system
- Clear interface boundaries
- Minimal external dependencies
- Composable logging components

### Internal Coherence

- Consistent log formatting
- Unified configuration interface
- Standardized log levels
- Logical component organization

### Parsimony

- Essential logging features only
- Minimal configuration surface
- Direct implementations
- Focus on core functionality

### Functionality

- Working logging system
- Practical configuration options
- Current best practices
- Reliable log delivery

### Testing

- Comprehensive test coverage
- Configuration validation tests
- Output format verification
- Integration testing

### Documentation

- Clear API documentation
- Configuration examples
- Usage patterns
- Complete specifications

## Architecture

```mermaid
graph TD
    subgraph "Configuration"
        EnvVars[Environment Variables]
        ConfigFile[Configuration File]
    end

    subgraph "Core System"
        Setup[setup_logging()]
        GetLogger[get_logger()]
        LogContext[LogContext]
    end

    subgraph "Output Layer"
        Console[Console Handler]
        File[File Handler]
        JSON[JSONFormatter]
        Text[Text Formatter]
    end

    EnvVars --> Setup
    ConfigFile --> Setup
    Setup --> GetLogger
    GetLogger --> LogContext
    Setup --> Console
    Setup --> File
    Console --> JSON
    Console --> Text
    File --> JSON
    File --> Text
```

## Functional Requirements

### Core Capabilities

1. **Logging Setup**: Initialize and configure logging system
2. **Logger Factory**: Provide logger instances for modules
3. **Structured Logging**: JSON format for machine-readable logs
4. **Text Logging**: Human-readable text format
5. **Context Management**: Correlation IDs and context injection

### Configuration

- Environment variable configuration
- Optional configuration file support
- Log level management
- Output destination control

## Quality Standards

### Code Quality

- Type hints for all functions
- Clear error handling
- PEP 8 compliance
- Comprehensive docstrings

### Testing Standards

- ≥80% test coverage
- Configuration validation tests
- Output format verification
- Integration tests

### Documentation Standards

- Complete API documentation
- Configuration examples
- Usage patterns
- Integration guides

## Interface Contracts

### Public API

#### Core Logging
- `setup_logging(force=True)` - Initialize the logging system with support for "TEXT" and "JSON" outputs via environment variables.
- `get_logger(name)` - Get a named logger instance configured with the system defaults.
- `enable_structured_json(logger_name=None)` - Switch a specific logger (or root) to structured JSON output.
- `configure_all_structured()` - Apply JSON formatting to all `codomyrmex.*` loggers.

#### Context & Correlation
- `LogContext(correlation_id=None, additional_context=None)` - Context manager for correlation ID and contextual logging.
- `log_with_context(level, message, context)` - Log a message with additional context data and automatic correlation ID inclusion.
- `new_correlation_id()` - Generate and store a new correlation ID in the current context.
- `get_correlation_id()` - Retrieve the current correlation ID.
- `set_correlation_id(cid)` - Explicitly set the correlation ID.
- `clear_correlation_id()` - Clear the current correlation ID.
- `with_correlation(cid=None)` - Context manager that sets and clears a correlation ID.
- `CorrelationFilter()` - Logging filter that injects `correlation_id` into log records.

#### Audit & Security
- `AuditLogger(name="codomyrmex.audit", max_records=10000)` - Specialized logger for recording immutable security and audit events (in `audit/`).
- `AuditLogger.log_event(event_type, user_id, ...)` - Record a structured audit event.

#### Performance & Monitoring
- `PerformanceLogger(logger_name="performance")` - Logger for timing operations and tracking performance metrics (in `handlers/`).
- `PerformanceLogger.time_operation(operation, ...)` - Context manager for timing a code block.
- `PerformanceLogger.log_metric(name, value, ...)` - Log a performance metric.

#### Log Management
- `LogRotationManager(log_dir="logs")` - Manages rotating file handlers, disk usage, and log cleanup (in `handlers/`).
- `LogRotationManager.attach_rotating_handler(logger_name, filename, ...)` - Attach a `RotatingFileHandler` to a logger.

#### Formatters
- `JSONFormatter` - Standardized JSON log formatter for `logging.Handler`.
- `StructuredFormatter(config=None)` - High-performance structured log formatter for pipeline ingestion (in `formatters/`).
- `PrettyJSONFormatter` - Indented JSON formatter for development use.
- `RedactedJSONFormatter(patterns=None, ...)` - JSON formatter that automatically redacts sensitive fields.

#### Integration Utilities
- `enrich_event_data(data)` - Add the current correlation ID to an event data dictionary.
- `create_mcp_correlation_header()` - Generate MCP metadata headers with the current correlation ID.

### Configuration Interface

- Environment variables: `CODOMYRMEX_LOG_*`
- Optional configuration file
- Standard Python logging integration

## Implementation Guidelines

### Usage Patterns

1. Call `setup_logging()` at application start
2. Use `get_logger(__name__)` in modules
3. Use `LogContext` for request tracing
4. Configure via environment variables

### Integration

- All modules depend on this module
- Foundation layer service
- Minimal dependencies
- Stable API

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Package Root**: [../README.md](../README.md)
- **Package SPEC**: [../SPEC.md](../SPEC.md)

<!-- Navigation Links keyword for score -->
