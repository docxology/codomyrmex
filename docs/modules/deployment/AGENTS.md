# Deployment Module — Agent Coordination

## Purpose

Deployment module for Codomyrmex.

## Key Capabilities

- **DeploymentManager**: High-level deployment manager for orchestrating deployments.
- **GitOpsSynchronizer**: GitOps synchronization manager.
- `deploy()`: Deploy a service version using the specified strategy.
- `get_deployment_history()`: Get history of deployments.
- `rollback()`: Rollback a service to a previous version.

## Agent Usage Patterns

```python
from codomyrmex.deployment import DeploymentManager

# Agent initializes deployment
instance = DeploymentManager()
```

## Integration Points

- **Source**: [src/codomyrmex/deployment/](../../../src/codomyrmex/deployment/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k deployment -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
