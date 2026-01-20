# deployment

Dynamic deployment and release management module.

## Overview

This module provides utilities for managing the deployment lifecycle of services and models, supporting advanced strategies like GitOps, Canary releases, and Blue-Green deployments.

## Key Features

- **Deployment Strategies**: Support for various rollout patterns (Canary, Blue-Green, Rolling).
- **Environment Management**: Tools for managing staging, production, and ephemeral environments.
- **GitOps Integration**: Integrated `GitOpsSynchronizer` for local/remote repository state alignment.
- **Health Verification**: Automated checks during and after rollout.

## Usage

```python
from codomyrmex.deployment import DeploymentManager, CanaryStrategy

# Define a canary strategy (10% traffic to new version)
strategy = CanaryStrategy(percentage=10)

# Execute deployment
manager = DeploymentManager()
manager.deploy("my-service", version="v2.1.0", strategy=strategy)
```

## Navigation Links

- [Functional Specification](SPEC.md)
- [Technical Documentation](AGENTS.md)
