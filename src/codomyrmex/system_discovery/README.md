# System Discovery Module

**Version**: v0.1.0 | **Status**: Active

Module scanning, capability discovery, and system status reporting.


## Installation

```bash
uv uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`FunctionCapability`** — Metadata about a discovered function capability.
- **`ClassCapability`** — Metadata about a discovered class capability.
- **`ModuleCapability`** — Aggregated capability information for a module.
- **`CapabilityScanner`** — Advanced capability scanner for the Codomyrmex ecosystem.
- **`ModuleInfo`** — Aggregated metadata and capabilities for a single discovered Codomyrmex module.
- **`SystemDiscovery`** — Comprehensive system discovery and orchestration for Codomyrmex.
- **`HealthStatus`** — Health status enumeration.
- **`HealthCheckResult`** — Result of a health check.

### Functions
- **`get_system_context()`** — Get the current system context for agents.
- **`check_module_availability()`** — Check if a module is available and importable.

## Quick Start

```python
from codomyrmex.system_discovery import (
    SystemDiscovery, StatusReporter, CapabilityScanner, get_system_context
)

# Discover all modules
discovery = SystemDiscovery()
modules = discovery.scan()

for module in modules:
    print(f"{module.name}: {len(module.capabilities)} capabilities")

# Get system context for LLM
context = get_system_context()
print(context)

# Scan capabilities
scanner = CapabilityScanner()
capabilities = scanner.scan_module("codomyrmex.llm")
for cap in capabilities:
    print(f"  - {cap.name}: {cap.description}")

# Generate status report
reporter = StatusReporter()
report = reporter.generate()
print(f"Modules: {report.module_count}")
print(f"Health: {report.health_score}%")
```

## Exports

| Class | Description |
|-------|-------------|
| `SystemDiscovery` | Scan all Codomyrmex modules |
| `CapabilityScanner` | Extract capabilities from modules |
| `StatusReporter` | Generate system health reports |
| `get_system_context()` | Get context string for LLM |

## Use Cases

- **Module introspection** — Discover available functionality
- **Health monitoring** — Check module status
- **LLM context** — Provide system awareness to agents


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k system_discovery -v
```


## Documentation

- [Module Documentation](../../../docs/modules/system_discovery/README.md)
- [Agent Guide](../../../docs/modules/system_discovery/AGENTS.md)
- [Specification](../../../docs/modules/system_discovery/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
