# Agent Guidelines - System Discovery

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Module introspection, capability scanning, and system health reporting for the Codomyrmex platform.
Provides `SystemDiscovery` to scan all 128 modules and report their status, `CapabilityScanner` for
feature-level capability queries, and `StatusReporter` for health score generation. Three MCP tools
(`health_check`, `list_modules`, `dependency_tree`) expose these capabilities to PAI agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `SystemDiscovery`, `CapabilityScanner`, `StatusReporter`, `HealthChecker`, `get_system_context` |
| `system_discovery.py` | `SystemDiscovery` — scan all modules, return status objects |
| `capability_scanner.py` | `CapabilityScanner` — query modules by feature/capability |
| `status_reporter.py` | `StatusReporter` — generate health score and status report |
| `health_checker.py` | `HealthChecker` — individual module health checks |
| `mcp_tools.py` | MCP tools: `health_check`, `list_modules`, `dependency_tree` |

## Key Classes

- **SystemDiscovery** — Scan all Codomyrmex modules
- **CapabilityScanner** — Extract module capabilities
- **StatusReporter** — System status reporting
- **HealthChecker** — Module health checks
- **get_system_context()** — Get LLM context string

## Agent Instructions

1. **Scan at startup** — Discover available modules early
2. **Cache results** — Module list changes infrequently
3. **Use context for LLM** — Use `get_system_context()` in prompts
4. **Check health regularly** — Monitor module status
5. **Filter by capability** — Query modules by needed features

## Common Patterns

```python
from codomyrmex.system_discovery import (
    SystemDiscovery, CapabilityScanner, StatusReporter, get_system_context
)

# Discover all modules
discovery = SystemDiscovery()
modules = discovery.scan()

for module in modules:
    print(f"{module.name}: {module.status}")

# Get LLM system context
context = get_system_context()  # Include in agent prompt

# Check module capabilities
scanner = CapabilityScanner()
if scanner.has_capability("llm", "chat"):
    use_llm_chat()

# Generate health report
reporter = StatusReporter()
report = reporter.generate()
print(f"Health: {report.health_score}%")
```

## Testing Patterns

```python
# Verify module discovery
discovery = SystemDiscovery()
modules = discovery.scan()
assert len(modules) > 0
assert any(m.name == "llm" for m in modules)

# Verify health reporting
reporter = StatusReporter()
report = reporter.generate()
assert 0 <= report.health_score <= 100
```

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `health_check` | Run a health check on the system or a specific module | SAFE |
| `list_modules` | List all registered modules and their availability | SAFE |
| `dependency_tree` | Show the dependency tree for a specific module | SAFE |

## Operating Contracts

- `SystemDiscovery.scan()` returns a list of module status objects — always check `module.status` before using
- `CapabilityScanner.has_capability(module, capability)` returns `False` if module is not loaded — not an error
- `get_system_context()` produces a formatted string for LLM prompts — do not parse it programmatically
- `health_check` is a point-in-time snapshot — run before critical operations, not cached
- **DO NOT** modify module status returned by `scan()` — results are read-only snapshots

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `health_check`, `list_modules`, `dependency_tree` | TRUSTED |
| **Architect** | Read + Design | `list_modules`, `dependency_tree` — module inventory, dependency architecture analysis | OBSERVED |
| **QATester** | Validation | `health_check`, `list_modules` — system health verification, module availability | OBSERVED |
| **Researcher** | Read-only | `health_check`, `list_modules`, `dependency_tree` — full read access for analysis | SAFE |

### Engineer Agent
**Use Cases**: System health checks during OBSERVE, module enumeration, dependency tree analysis before BUILD.

### Architect Agent
**Use Cases**: Module inventory for architectural decisions, dependency tree review, planning module relationships.

### QATester Agent
**Use Cases**: System health verification during VERIFY, confirming all 128 modules are discoverable.

### Researcher Agent
**Use Cases**: Full read access for research-phase system discovery, module health inspection, dependency analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/system_discovery.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/system_discovery.cursorrules)
