# Ide

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

IDE Integration Module.

## Architecture Overview

```
ide/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`IDEClient`**
- **`IDEStatus`**
- **`IDECommand`**
- **`IDECommandResult`**
- **`FileInfo`**
- **`IDEError`**
- **`ConnectionError`**
- **`CommandExecutionError`**
- **`SessionError`**
- **`ArtifactError`**
- **`CursorClient`**
- **`VSCodeClient`**
- **`AntigravityClient`**
- **`cli_commands`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `ide_get_active_file` | Safe |
| `ide_list_tools` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/ide/](../../../../src/codomyrmex/ide/)
- **Parent**: [All Modules](../README.md)
