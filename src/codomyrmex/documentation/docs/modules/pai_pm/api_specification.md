# PAI PM - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `pai_pm` module wraps the PAI Project Manager Bun/TypeScript server as a Python module with MCP tools. Provides lifecycle management for the PM server and Python client bindings.

## 2. Prerequisites
- **Bun runtime**: `https://bun.sh`
- **Install**: `cd src/codomyrmex/pai_pm/server && bun install`

## 3. Core Components

### 3.1 Classes

| Class | Description |
|-------|-------------|
| `PaiPmServerManager` | Lifecycle manager (start, stop, health check) for the Bun PM server |
| `PaiPmConfig` | Configuration dataclass (host, port, timeout) |

### 3.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_config` | `() -> PaiPmConfig` | Load/return the current PM configuration |
| `get_bun_version` | `() -> str` | Return installed Bun version string |

### 3.3 Exceptions

| Exception | Description |
|-----------|-------------|
| `PaiPmError` | Base exception |
| `PaiPmNotInstalledError` | Bun runtime not found |
| `PaiPmConnectionError` | Cannot connect to PM server |
| `PaiPmServerError` | Server returned an error |
| `PaiPmTimeoutError` | Server operation timed out |

### 3.4 Constants

| Name | Type | Description |
|------|------|-------------|
| `HAS_BUN` | `bool` | `True` when `bun` binary is available in PATH |

## 4. Usage Example

```python
from codomyrmex.pai_pm import PaiPmServerManager, get_config, HAS_BUN

if HAS_BUN:
    config = get_config()
    manager = PaiPmServerManager(config)
    manager.start()
    # Server running on config.host:config.port
```

## 5. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
