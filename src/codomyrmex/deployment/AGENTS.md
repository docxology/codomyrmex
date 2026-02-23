# Agent Guidelines - Deployment

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Container deployment, infrastructure automation, and environment management.

## Key Classes

- **DeploymentManager** — Orchestrate deployments
- **ContainerBuilder** — Docker/OCI image building
- **InfrastructureConfig** — Infrastructure as code
- **EnvironmentManager** — Manage deployment environments

## Agent Instructions

1. **Validate configs** — Check before deploying
2. **Use staging first** — Never deploy directly to prod
3. **Rollback ready** — Always have rollback plan
4. **Health checks** — Wait for health before marking success
5. **Log everything** — Capture deployment logs

## Common Patterns

```python
from codomyrmex.deployment import (
    DeploymentManager, ContainerBuilder, EnvironmentManager
)

# Build container
builder = ContainerBuilder()
image = builder.build("./Dockerfile", tag="app:v1.0")

# Deploy to environment
deployer = DeploymentManager()
result = deployer.deploy(
    image="app:v1.0",
    environment="staging",
    replicas=3
)

# Wait for health
if deployer.wait_healthy(timeout=300):
    deployer.promote("production")
else:
    deployer.rollback()
```

## Testing Patterns

```python
# Verify config validation
config = InfrastructureConfig(path="infra.yaml")
errors = config.validate()
assert len(errors) == 0

# Verify deployment (dry run)
deployer = DeploymentManager(dry_run=True)
result = deployer.deploy(image="test", environment="test")
assert result.dry_run
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
