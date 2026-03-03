# Operating System

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Codomyrmex Operating System Module.

## Architecture Overview

```
operating_system/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`OSPlatform`**
- **`ServiceStatus`**
- **`ProcessStatus`**
- **`SystemInfo`**
- **`ProcessInfo`**
- **`DiskInfo`**
- **`ServiceInfo`**
- **`NetworkInfo`**
- **`CommandResult`**
- **`OSProviderBase`**
- **`detect_platform`**
- **`get_provider`**
- **`get_system_info`**
- **`list_processes`**
- **`get_disk_usage`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `os_system_info` | Safe |
| `os_list_processes` | Safe |
| `os_disk_usage` | Safe |
| `os_network_info` | Safe |
| `os_execute_command` | Safe |
| `os_environment_variables` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/operating_system/](../../../../src/codomyrmex/operating_system/)
- **Parent**: [All Modules](../README.md)
