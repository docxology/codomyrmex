# System Discovery Module - Agent Coordination

**Version**: v1.0.8 | **Last Updated**: March 2026

## Overview

The System Discovery module enables agents to discover all available modules, their capabilities, health status, and dependency relationships within the Codomyrmex ecosystem. It is the primary tool for agents performing system introspection during the OBSERVE phase.

## Key Files

| File | Class/Function | Role |
|------|---------------|------|
| `core/discovery_engine.py` | `SystemDiscovery` | Main discovery engine with module scanning |
| `core/discovery_engine.py` | `ModuleInfo`, `ModuleCapability` | Structured metadata dataclasses |
| `core/capability_scanner.py` | `CapabilityScanner` | Advanced function/class/method scanner |
| `core/capability_scanner.py` | `FunctionCapability`, `ClassCapability` | Capability metadata |
| `core/context.py` | `get_system_context()` | System context retrieval |
| `core/dependency_analyzer.py` | `DependencyAnalyzer` | Module dependency graph analysis |
| `core/health_checker.py` | `SystemHealthChecker` | System health validation |
| `reporting/status_reporter.py` | `StatusReporter` | Report generation |
| `mcp_tools.py` | `health_check`, `list_modules`, `dependency_tree` | MCP tools |

## MCP Tools Available

| Tool | Category | Description |
|------|----------|-------------|
| `health_check` | system_discovery | Run health checks on all or a specific module |
| `list_modules` | system_discovery | List all registered modules with availability status |
| `dependency_tree` | system_discovery | Show exports and dependency information for a module |

## Agent Instructions

1. Use `list_modules` as the first step when exploring the platform.
2. Use `health_check` without parameters for full system assessment, or pass a module name for targeted checks.
3. Use `dependency_tree` to understand what a module exports before using it.
4. `CapabilityScanner` provides function-level metadata including signatures, decorators, and complexity scores.

## Operating Contracts

- `health_check` returns `{"status": "success", "healthy": bool}` or `{"status": "error", "message": str}`.
- `list_modules` returns all modules with availability flags.
- `dependency_tree` surfaces ImportError explicitly when a module cannot be imported.

## Common Patterns

```python
from codomyrmex.system_discovery.mcp_tools import health_check, list_modules, dependency_tree

modules = list_modules()
health = health_check()
tree = dependency_tree(module="orchestrator")
```

## PAI Agent Role Access Matrix

| Agent | Access Level | Primary Tools |
|-------|-------------|---------------|
| Architect | Full | `list_modules`, `dependency_tree`, `CapabilityScanner` |
| Engineer | Read | `health_check`, `list_modules` |
| QATester | Read | `health_check` |

## Navigation

- [readme.md](readme.md) -- Module overview
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../../../system_discovery/)
