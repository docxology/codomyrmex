# Agent Guidelines - Containerization

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Docker container management, image building, security scanning, and orchestration. Provides
`ContainerManager` for full container lifecycle (run, stop, logs), `ImageBuilder` for Docker image
construction, `DockerCompose` for multi-service compose management, and `container_security_scan`
for vulnerability detection. Four MCP tools expose the full container lifecycle to PAI agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `ContainerManager`, `ImageBuilder`, `DockerCompose`, `Container` |
| `container_manager.py` | `ContainerManager` — container lifecycle (run, stop, logs, list) |
| `image_builder.py` | `ImageBuilder` — Docker image construction |
| `docker_compose.py` | `DockerCompose` — compose file management (`up`, `down`, `ps`) |
| `mcp_tools.py` | MCP tools: `container_runtime_status`, `container_build`, `container_list`, `container_security_scan` |

## Key Classes

- **ContainerManager** — Manage container lifecycle (run, stop, logs, list)
- **ImageBuilder** — Build Docker images from Dockerfiles
- **DockerCompose** — Compose file management (`up`, `down`, `ps`)
- **Container** — Container operations handle

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `container_runtime_status` | Check availability of container runtimes (Docker, Kubernetes) | SAFE |
| `container_build` | Build container images using Docker | TRUSTED |
| `container_list` | List running containers managed by Docker | SAFE |
| `container_security_scan` | Scan a container image for security vulnerabilities | SAFE |

## Agent Instructions

1. **Use multi-stage builds** — Produces smaller, more secure images
2. **Pin versions** — Always specify exact base image tags
3. **Clean build** — Remove build artifacts from final stage
4. **Health checks** — Add `HEALTHCHECK` to container definitions
5. **Log to stdout** — Container logging best practice for orchestrators

## Operating Contracts

- `container_build` is a destructive (TRUSTED) operation — requires explicit authorization
- `ImageBuilder.build()` requires Docker daemon running; raises if not available
- `ContainerManager.run()` returns a `Container` handle — always `stop()` after use in tests
- `container_security_scan` is read-only and does not modify images
- **DO NOT** use `latest` tags in production builds — always specify version

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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `container_runtime_status`, `container_build`, `container_list`, `container_security_scan` | TRUSTED |
| **Architect** | Read + Design | `container_list`, `container_runtime_status` — container architecture review, image design | OBSERVED |
| **QATester** | Validation | `container_security_scan`, `container_runtime_status` — security validation, runtime health | OBSERVED |
| **Researcher** | Read-only | `container_runtime_status`, `container_list` — inspect runtime and container state | SAFE |

### Engineer Agent
**Use Cases**: Building container images during BUILD, listing running containers, scanning images for vulnerabilities during VERIFY.

### Architect Agent
**Use Cases**: Reviewing container configurations, designing Docker/K8s architecture, analyzing image layering.

### QATester Agent
**Use Cases**: Security scanning container images during VERIFY, confirming runtime health.

### Researcher Agent
**Use Cases**: Inspecting container runtime availability and listing active containers for analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/containerization.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/containerization.cursorrules)
