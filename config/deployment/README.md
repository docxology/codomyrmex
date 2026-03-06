# Deployment Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Deployment strategies including canary, blue-green, and rolling deployments. Provides DeploymentManager, GitOps synchronization, health checks, and automated rollback.

## Quick Configuration

```bash
export DEPLOY_HOST="localhost"    # Target deployment host address
export DEPLOY_BASE_PORT="8000"    # Base port for deployment instances
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `DEPLOY_HOST` | str | `localhost` | Target deployment host address |
| `DEPLOY_BASE_PORT` | str | `8000` | Base port for deployment instances |

## PAI Integration

PAI agents interact with deployment through direct Python imports. Deployment strategies are selected per-deployment. Canary analysis thresholds and health check intervals are configurable per strategy.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep deployment

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/deployment/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
