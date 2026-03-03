# Reporting Module

Reporting capabilities for Codomyrmex.


**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

Reporting module for generating and processing system reports within Codomyrmex. The `Reporting` class allows processing data strings into structured reports, encapsulating this logic for the rest of the application. The MCP tool `reporting_process` exposes this functionality directly.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **VERIFY** | Generate system reports | `reporting_process` |

PAI agents access this module via the MCP bridge to aggregate data and summarize activities. The `reporting_process` tool handles the core of this generation.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Functions

- **`create_reporting()`** -- Factory function to create a new `Reporting` instance.

### Classes

- **`Reporting`** -- Main class containing `process(self, data: Any)` to process incoming data strings into reports.

## Directory Contents

- `__init__.py` - Package marker with module docstring
- `reporting.py` - Core reporting logic implementation
- `mcp_tools.py` - MCP tool definitions for the reporting module
- `AGENTS.md` - AGENTS documentation
- `API_SPECIFICATION.md` - API specification
- `CHANGELOG.md` - Changelog
- `MCP_TOOL_SPECIFICATION.md` - MCP tool specification
- `SECURITY.md` - Security documentation
- `SPEC.md` - Module specification
- `USAGE_EXAMPLES.md` - Usage examples

## Quick Start

```python
from codomyrmex.reporting import create_reporting

reporter = create_reporting()
result = reporter.process("Sample data")
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k reporting -v
```

## Navigation

- **Full Documentation**: [docs/modules/reporting/](../../../docs/modules/reporting/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
