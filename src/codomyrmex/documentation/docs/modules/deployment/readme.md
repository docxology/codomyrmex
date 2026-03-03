# Deployment

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Deployment module for Codomyrmex.

## Architecture Overview

```
deployment/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`health_checks`**
- **`strategies`**
- **`rollback`**
- **`DeploymentState`**
- **`DeploymentTarget`**
- **`DeploymentResult`**
- **`DeploymentStrategy`**
- **`RollingDeployment`**
- **`BlueGreenDeployment`**
- **`CanaryDeployment`**
- **`create_strategy`**
- **`StrategyProgress`**
- **`CanaryStrategy`**
- **`BlueGreenStrategy`**
- **`RollingStrategy`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `deployment_execute` | Safe |
| `deployment_list_strategies` | Safe |
| `deployment_get_history` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/deployment/](../../../../src/codomyrmex/deployment/)
- **Parent**: [All Modules](../README.md)
