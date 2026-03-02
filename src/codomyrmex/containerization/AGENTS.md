# Agent Guidelines - Containerization

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

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

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Key Parameters | Trust Level |
|------|-------------|----------------|-------------|
| `container_runtime_status` | Check availability of container runtimes (Docker, Kubernetes) | (none) | Safe |
| `container_build` | Build container images using Docker | `image_name`, `dockerfile_path`, `tag` | Destructive |
| `container_list` | List running containers managed by Docker | (none) | Safe |
| `container_security_scan` | Scan a container image for security vulnerabilities | `image` | Safe |

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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `container_runtime_status`, `container_build`, `container_list`, `container_security_scan`; full container lifecycle | TRUSTED |
| **Architect** | Read + Design | `container_list`, `container_runtime_status`; container architecture review, image design | OBSERVED |
| **QATester** | Validation | `container_security_scan`, `container_runtime_status`; security validation, runtime health | OBSERVED |

### Engineer Agent
**Use Cases**: Building container images during BUILD, listing running containers, scanning images for vulnerabilities during VERIFY.

### Architect Agent
**Use Cases**: Reviewing container configurations, designing Docker/K8s architecture, analyzing image layering.

### QATester Agent
**Use Cases**: Security scanning container images during VERIFY, confirming runtime health.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
