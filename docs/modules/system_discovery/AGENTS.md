# Agent Guidelines - System Discovery

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Module introspection, capability scanning, and system health reporting.

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

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
