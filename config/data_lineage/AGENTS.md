# Data Lineage -- Configuration Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the data_lineage module. Data lineage tracking through transformations with graph-based analysis.

## Configuration Requirements

Before using data_lineage in any PAI workflow, ensure:

1. The module is importable via `from codomyrmex.data_lineage import *`
2. Any optional dependencies are installed (check with `codomyrmex check`)

## Agent Instructions

1. Import the module directly: `from codomyrmex.data_lineage import ...`
2. Check module availability with `list_modules()` from system_discovery
3. This module has no auto-discovered MCP tools; use direct Python imports
4. Lineage graphs are built incrementally as data flows through transformations. Storage is in-memory by default.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("data_lineage.setting")

# Update configuration
set_config("data_lineage.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/data_lineage/AGENTS.md)
