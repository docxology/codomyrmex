# Data Visualization -- Configuration Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the data_visualization module. Chart and dashboard generation supporting bar, line, scatter, heatmap, histogram, pie, area, and box plot chart types.

## Configuration Requirements

Before using data_visualization in any PAI workflow, ensure:

1. The module is importable via `from codomyrmex.data_visualization import *`
2. Any optional dependencies are installed (check with `codomyrmex check`)

## Agent Instructions

1. Import the module directly: `from codomyrmex.data_visualization import ...`
2. Check module availability with `list_modules()` from system_discovery
3. Available MCP tools: `generate_chart`, `export_dashboard`
4. Visual themes are configurable. Chart output formats include PNG, SVG, and HTML. Dashboard export produces self-contained HTML files.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("data_visualization.setting")

# Update configuration
set_config("data_visualization.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/data_visualization/AGENTS.md)
