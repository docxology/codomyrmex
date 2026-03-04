# Deployment -- Configuration Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the deployment module. Deployment strategies including canary, blue-green, and rolling deployments.

## Configuration Requirements

Before using deployment in any PAI workflow, ensure:

1. `DEPLOY_HOST` is set (default: `localhost`) -- Target deployment host address
2. `DEPLOY_BASE_PORT` is set (default: `8000`) -- Base port for deployment instances

## Agent Instructions

1. Verify required environment variables are set before invoking deployment tools
2. Use `get_config("deployment.<key>")` from config_management to read module settings
3. This module has no auto-discovered MCP tools; use direct Python imports
4. Deployment strategies are selected per-deployment. Canary analysis thresholds and health check intervals are configurable per strategy.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("deployment.setting")

# Update configuration
set_config("deployment.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/deployment/AGENTS.md)
