# Agent Guidelines - Containerization

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Docker container management, image building, and orchestration.

## Key Classes

- **ContainerManager** — Manage container lifecycle
- **ImageBuilder** — Build Docker images
- **DockerCompose** — Compose file management
- **Container** — Container operations

## Agent Instructions

1. **Use multi-stage** — Smaller images
2. **Pin versions** — Specific base image tags
3. **Clean build** — Remove build artifacts
4. **Health checks** — Add container health checks
5. **Log to stdout** — Container logging best practice

## Common Patterns

```python
from codomyrmex.containerization import (
    ContainerManager, ImageBuilder, DockerCompose
)

# Build image
builder = ImageBuilder()
image = builder.build(
    dockerfile="./Dockerfile",
    tag="myapp:v1.0",
    build_args={"ENV": "production"}
)

# Manage containers
manager = ContainerManager()
container = manager.run(
    image="myapp:v1.0",
    ports={"8080/tcp": 8080},
    environment={"API_KEY": key}
)

# Container operations
manager.logs(container.id)
manager.stop(container.id)

# Docker Compose
compose = DockerCompose("docker-compose.yml")
compose.up(detach=True)
compose.down()
```

## Testing Patterns

```python
# Verify image build
builder = ImageBuilder()
image = builder.build("./test/Dockerfile", tag="test:latest")
assert image is not None

# Verify container management
manager = ContainerManager()
containers = manager.list()
assert isinstance(containers, list)
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
