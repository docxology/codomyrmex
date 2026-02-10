# System Discovery Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Automatic system capability detection, dependency resolution, and environment profiling.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **FunctionCapability** — Metadata about a discovered function capability.
- **ClassCapability** — Metadata about a discovered class capability.
- **ModuleCapability** — Aggregated capability information for a module.
- **CapabilityScanner** — Advanced capability scanner for the Codomyrmex ecosystem.
- **ModuleInfo** — Aggregated metadata and capabilities for a single discovered Codomyrmex module.
- **SystemDiscovery** — Comprehensive system discovery and orchestration for Codomyrmex.
- `get_system_context()` — Get the current system context for agents.
- `check_module_availability()` — Check if a module is available and importable.
- `generate_health_report()` — Convenience function to generate a health report.
- `format_health_report()` — Convenience function to format a health report.

## Quick Start

```python
from codomyrmex.system_discovery import FunctionCapability, ClassCapability, ModuleCapability

instance = FunctionCapability()
```

## Source Files

- `capability_scanner.py`
- `context.py`
- `discovery_engine.py`
- `health_checker.py`
- `health_reporter.py`
- `profilers.py`
- `status_reporter.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k system_discovery -v
```

## Navigation

- **Source**: [src/codomyrmex/system_discovery/](../../../src/codomyrmex/system_discovery/)
- **Parent**: [Modules](../README.md)
