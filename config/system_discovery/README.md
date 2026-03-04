# System Discovery Module

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The System Discovery module scans, discovers, and reports on all modules within the Codomyrmex ecosystem. It provides capability scanning (functions, classes, methods, constants), dependency analysis, health checking, and status reporting across the entire platform.

## PAI Integration

| Algorithm Phase | System Discovery Role |
|----------------|----------------------|
| OBSERVE | Primary module for discovering available capabilities and system state |
| VERIFY | Health checks validate module importability, test presence, and documentation completeness |
| LEARN | Capability scanner produces structured metadata for agent knowledge bases |

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `SystemDiscovery` | class | Main discovery engine -- scans modules, capabilities, and system status |
| `CapabilityScanner` | class | Advanced scanner for functions, classes, methods across the ecosystem |
| `StatusReporter` | class | Generates system status reports |
| `get_system_context` | function | Returns the current system context for cross-module queries |
| `cli_commands` | function | Returns CLI command definitions for the system_discovery module |

## Quick Start

```python
from codomyrmex.system_discovery import SystemDiscovery, CapabilityScanner

# Discover all modules
discovery = SystemDiscovery()
modules = discovery.discover_all()

# Scan capabilities of a specific module
scanner = CapabilityScanner()
capabilities = scanner.scan_module("codomyrmex.orchestrator")
```

## Architecture

```
system_discovery/
  __init__.py              # Public API exports
  mcp_tools.py             # MCP tools: health_check, list_modules, dependency_tree
  core/
    capability_scanner.py  # FunctionCapability, ClassCapability, ModuleCapability, CapabilityScanner
    context.py             # get_system_context()
    dependency_analyzer.py # DependencyAnalyzer for module dependency graphs
    discovery_engine.py    # SystemDiscovery, ModuleInfo, ModuleCapability
    health_checker.py      # SystemHealthChecker
  health/                  # Health check implementations
  reporting/
    status_reporter.py     # StatusReporter for system reports
```

## MCP Tools

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `health_check` | Run health checks on the system or a specific module | `module` (str, optional) |
| `list_modules` | List all registered modules and their availability | None |
| `dependency_tree` | Show the dependency tree (exports) for a specific module | `module` (str, required) |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/system_discovery/ -v
```

## Navigation

- [AGENTS.md](AGENTS.md) -- Agent coordination documentation
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../src/codomyrmex/system_discovery/)
