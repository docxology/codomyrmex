# Config Monitoring -- Configuration Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the config_monitoring module. Configuration monitoring, auditing, and hot-reload watching.

## Configuration Requirements

Before using config_monitoring in any PAI workflow, ensure:

1. The module is importable via `from codomyrmex.config_monitoring import *`
2. Any optional dependencies are installed (check with `codomyrmex check`)

## Agent Instructions

1. Import the module directly: `from codomyrmex.config_monitoring import ...`
2. Check module availability with `list_modules()` from system_discovery
3. This module has no auto-discovered MCP tools; use direct Python imports
4. ConfigWatcher uses filesystem events to detect config changes. ConfigurationMonitor tracks snapshots for drift analysis. Polling interval is configurable.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("config_monitoring.setting")

# Update configuration
set_config("config_monitoring.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/config_monitoring/AGENTS.md)
