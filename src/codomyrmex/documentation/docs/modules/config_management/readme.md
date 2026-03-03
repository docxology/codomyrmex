# Config Management

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Configuration Management Module for Codomyrmex.

## Architecture Overview

```
config_management/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`ConfigurationManager`**
- **`load_configuration`**
- **`validate_configuration`**
- **`Configuration`**
- **`ConfigSchema`**
- **`ConfigurationDeployer`**
- **`deploy_configuration`**
- **`ConfigDeployment`**
- **`ConfigurationMonitor`**
- **`monitor_config_changes`**
- **`ConfigAudit`**
- **`ConfigWatcher`**
- **`cli_commands`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `get_config` | Safe |
| `set_config` | Safe |
| `validate_config` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/config_management/](../../../../src/codomyrmex/config_management/)
- **Parent**: [All Modules](../README.md)
