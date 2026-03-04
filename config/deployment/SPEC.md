# Deployment Configuration Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Deployment strategies including canary, blue-green, and rolling deployments. Provides DeploymentManager, GitOps synchronization, health checks, and automated rollback. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `DEPLOY_HOST` | string | No | `localhost` | Target deployment host address |
| `DEPLOY_BASE_PORT` | string | No | `8000` | Base port for deployment instances |

## Environment Variables

```bash
# Optional (defaults shown)
export DEPLOY_HOST="localhost"    # Target deployment host address
export DEPLOY_BASE_PORT="8000"    # Base port for deployment instances
```

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- All configuration options have sensible defaults
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/deployment/SPEC.md)
