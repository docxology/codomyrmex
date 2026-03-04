# Collaboration -- Configuration Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the collaboration module. Multi-agent collaboration capabilities including agent management, communication channels, task coordination, consensus protocols, and swarm behavior.

## Configuration Requirements

Before using collaboration in any PAI workflow, ensure:

1. The module is importable via `from codomyrmex.collaboration import *`
2. Any optional dependencies are installed (check with `codomyrmex check`)

## Agent Instructions

1. Import the module directly: `from codomyrmex.collaboration import ...`
2. Check module availability with `list_modules()` from system_discovery
3. Available MCP tools: `swarm_submit_task`, `pool_status`, `list_agents`
4. Collaboration sessions are created programmatically. Agent registry maintains worker and supervisor roles. Communication uses in-process channels.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("collaboration.setting")

# Update configuration
set_config("collaboration.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/collaboration/AGENTS.md)
