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
| `core/capability_scanner.py` | `FunctionCapability`, `ClassCapability` | Capability metadata dataclasses |
| `core/context.py` | `get_system_context()` | System context retrieval |
| `core/dependency_analyzer.py` | `DependencyAnalyzer` | Module dependency graph analysis |
| `core/health_checker.py` | `SystemHealthChecker` | System health validation |
| `reporting/status_reporter.py` | `StatusReporter` | System status report generation |
| `mcp_tools.py` | `health_check()` | MCP tool: run health checks |
| `mcp_tools.py` | `list_modules()` | MCP tool: enumerate available modules |
| `mcp_tools.py` | `dependency_tree()` | MCP tool: show module exports |

## MCP Tools Available

| Tool | Category | Description |
|------|----------|-------------|
| `health_check` | system_discovery | Run health checks on all or a specific module |
| `list_modules` | system_discovery | List all registered modules with availability status |
| `dependency_tree` | system_discovery | Show exports and dependency information for a module |

## Agent Instructions

1. Use `list_modules` as the first step when exploring the platform to understand available capabilities.
2. Use `health_check` without parameters for a full system health assessment, or pass a module name for targeted checks.
3. Use `dependency_tree` to understand what a module exports before attempting to use it.
4. The `CapabilityScanner` provides granular function-level metadata including signatures, docstrings, decorators, and complexity scores.
5. `SystemDiscovery` checks for test presence (`has_tests`), documentation presence (`has_docs`), and importability (`is_importable`) per module.

## Operating Contracts

- `health_check` returns `{"status": "success", "healthy": bool}` on success or `{"status": "error", "message": str}` on failure.
- `list_modules` returns all modules from `codomyrmex.list_modules()` with availability status.
- `dependency_tree` uses `importlib.import_module` and reads `__all__` -- if a module cannot be imported, the error is surfaced explicitly.
- The `CapabilityScanner` uses both AST parsing and runtime inspection for comprehensive capability discovery.

## Common Patterns

```python
# MCP tool usage
from codomyrmex.system_discovery.mcp_tools import health_check, list_modules, dependency_tree

# Get all modules
modules = list_modules()
# {'status': 'success', 'modules': [{'name': '...', 'available': True}, ...], 'count': N}

# Check system health
health = health_check()
# {'status': 'success', 'healthy': True, 'module': 'all', 'details': ...}

# Inspect a module
tree = dependency_tree(module="orchestrator")
# {'status': 'success', 'module': 'orchestrator', 'exports': [...], 'export_count': N}
```

## PAI Agent Role Access Matrix

| Agent | Access Level | Primary Tools |
|-------|-------------|---------------|
| Architect | Full | `list_modules`, `dependency_tree`, `CapabilityScanner` |
| Engineer | Read | `health_check`, `list_modules` |
| QATester | Read | `health_check` |

## Navigation

- [README.md](README.md) -- Module overview
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../src/codomyrmex/system_discovery/)
