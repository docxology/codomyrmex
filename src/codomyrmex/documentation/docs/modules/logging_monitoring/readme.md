# Logging Monitoring

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Codomyrmex Logging Monitoring Module.

## Architecture Overview

```
logging_monitoring/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`cli_commands`**
- **`setup_logging`**
- **`get_logger`**
- **`new_correlation_id`**
- **`get_correlation_id`**
- **`set_correlation_id`**
- **`clear_correlation_id`**
- **`with_correlation`**
- **`CorrelationFilter`**
- **`enrich_event_data`**
- **`create_mcp_correlation_header`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `logging_format_structured` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/logging_monitoring/](../../../../src/codomyrmex/logging_monitoring/)
- **Parent**: [All Modules](../README.md)
