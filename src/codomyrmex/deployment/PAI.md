# Personal AI Infrastructure — Deployment Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Deployment module provides PAI integration for application deployment.

## PAI Capabilities

### Deployment Automation

Deploy applications:

```python
from codomyrmex.deployment import Deployer

deployer = Deployer(target="production")
deployer.deploy(version="v1.2.0")
```

### Rollback Support

Rollback deployments:

```python
from codomyrmex.deployment import Deployer

deployer = Deployer(target="production")
deployer.rollback(to_version="v1.1.0")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Deployer` | Deploy apps |
| `rollback` | Rollback versions |
| `HealthCheck` | Verify deployment |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
