# Cerebrum -- Configuration Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the cerebrum module. Case-Enabled Reasoning Engine with Bayesian Representations for Unified Modeling.

## Configuration Requirements

Before using cerebrum in any PAI workflow, ensure:

1. The module is importable via `from codomyrmex.cerebrum import *`
2. Any optional dependencies are installed (check with `codomyrmex check`)

## Agent Instructions

1. Import the module directly: `from codomyrmex.cerebrum import ...`
2. Check module availability with `list_modules()` from system_discovery
3. Available MCP tools: `query_knowledge_base`, `add_case_reference`
4. The CerebrumEngine is instantiated with case base size limits and inference parameters. Integrates with logging_monitoring for operational logging.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("cerebrum.setting")

# Update configuration
set_config("cerebrum.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/cerebrum/AGENTS.md)
