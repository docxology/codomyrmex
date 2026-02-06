# Personal AI Infrastructure — Containerization Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Containerization module provides PAI integration for Docker container management.

## PAI Capabilities

### Container Management

Manage Docker containers:

```python
from codomyrmex.containerization import ContainerManager

manager = ContainerManager()
container = manager.run("python:3.11", command="python app.py")

logs = container.logs()
container.stop()
```

### Image Building

Build Docker images:

```python
from codomyrmex.containerization import ImageBuilder

builder = ImageBuilder()
image = builder.build("./Dockerfile", tag="myapp:v1")
builder.push(image, registry="docker.io")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `ContainerManager` | Run containers |
| `ImageBuilder` | Build images |
| `ComposeManager` | Docker Compose |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
