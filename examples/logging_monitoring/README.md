# Logging Monitoring Examples

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025
This directory contains examples demonstrating the **Logging Monitoring** module of Codomyrmex.

## Overview

The Logging Monitoring module provides centralized logging infrastructure for the entire Codomyrmex platform, ensuring consistent log formatting, configurable output destinations, and proper log level management.

## Examples

### Basic Usage (`example_basic.py`)

Demonstrates core logging functionality:
- Setting up the centralized logging system
- Creating hierarchical loggers with `get_logger()`
- Logging at different severity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Configuring TEXT vs JSON output formats
- Structured logging with additional context

**Tested Methods:**
- `setup_logging()` - Initialize logging system (from `test_logging_monitoring.py`)
- `get_logger(name)` - Get configured logger instance (from `test_logging_monitoring.py`)
- `JsonFormatter` - JSON log formatting (from `test_logging_monitoring.py`)

## Configuration

### config.yaml / config.json

Key configuration options:

```yaml
logging:
  level: INFO              # Log level threshold
  file: logs/example.log   # Log file path (empty for console only)
  output_type: TEXT        # TEXT or JSON format
  format: DETAILED         # DETAILED or default format (TEXT mode only)
```

### Environment Variables

The logging system respects these environment variables:
- `CODOMYRMEX_LOG_LEVEL` - Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `CODOMYRMEX_LOG_FILE` - Override log file path
- `CODOMYRMEX_LOG_FORMAT` - Override log format
- `CODOMYRMEX_LOG_OUTPUT_TYPE` - Override output type (TEXT, JSON)

## Running the Examples

```bash
# Basic usage
cd examples/logging_monitoring
python example_basic.py

# With custom log level
CODOMYRMEX_LOG_LEVEL=DEBUG python example_basic.py

# With JSON output
CODOMYRMEX_LOG_OUTPUT_TYPE=JSON python example_basic.py
```

## Expected Output

The example will:
1. Setup the logging system
2. Create multiple hierarchical loggers
3. Log messages at different levels
4. Demonstrate error logging with tracebacks
5. Write logs to the configured file
6. Save results to output directory

Check the log file at `logs/logging_monitoring_example.log` to see the formatted output.

## Integration with Other Modules

The Logging Monitoring module is foundational and used by all other Codomyrmex modules:
- All modules use `get_logger(__name__)` for consistent logging
- The example demonstrates the pattern that other modules follow
- Configuration can be shared across the entire application

## Related Documentation

- [Module README](../../src/codomyrmex/logging_monitoring/README.md)
- [API Specification](../../src/codomyrmex/logging_monitoring/API_SPECIFICATION.md)
- [Unit Tests](../../testing/unit/test_logging_monitoring.py)

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)