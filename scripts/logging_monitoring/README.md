# Logging Monitoring Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.logging_monitoring` module.

## Purpose

This orchestrator provides command-line interface for testing and managing the logging system.

## Usage

```bash
# Test logging functionality
python scripts/logging_monitoring/orchestrate.py test-logging

# Show module information
python scripts/logging_monitoring/orchestrate.py info
```

## Commands

- `test-logging` - Test logging functionality with different log levels
- `info` - Show module information and configuration

## Related Documentation

- **[Module README](../../src/codomyrmex/logging_monitoring/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/logging_monitoring/API_SPECIFICATION.md)**: Detailed API reference
- **[Usage Examples](../../src/codomyrmex/logging_monitoring/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.logging_monitoring.setup_logging`
- `codomyrmex.logging_monitoring.get_logger`

See `codomyrmex.cli.py` for main CLI integration.

