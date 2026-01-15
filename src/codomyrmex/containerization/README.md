# Containerization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview
The `containerization` module provides the tooling to package Codomyrmex applications and agents into portable, isolated execution units. It abstracts the complexity of Docker and Kubernetes interaction, allowing for programmatic management of container lifecycles, image building, and orchestration. This module is essential for scalable deployment and reproducible research environments.

## Key Features
- **Docker Management**: The `docker_manager.py` handles container lifecycle (start, stop, exec), volume mounting, and network configuration.
- **Orchestration**: The `kubernetes_orchestrator.py` provides interfaces for deploying agents to Kubernetes clusters.
- **Build Automation**: `build_generator.py` automatically generates Dockerfiles and build contexts based on application requirements.
- **Optimization**: `image_optimizer.py` and `performance_optimizer.py` ensure container images are minimal and runtimes are tuned efficiently.
- **Security Scanning**: `security_scanner.py` integrates vulnerability scanning into the build pipeline.

## Quick Start

```python
from codomyrmex.containerization.docker_manager import DockerManager

manager = DockerManager()

# Build an image
manager.build_image(tag="my-agent:latest", path="./agent_context")

# Run a container
container = manager.run_container(
    image="my-agent:latest",
    command=["python", "main.py"],
    environment={"API_KEY": "secret"}
)

print(f"Agent running in container {container.id}")
```

## Module Structure

- `docker_manager.py`: Interface for local Docker daemon interactions.
- `kubernetes_orchestrator.py`: Interface for K8s API interactions.
- `build_generator.py`: Dockerfile generation logic.
- `container_registry.py`: Interaction with registries (Docker Hub, GCR).
- `image_optimizer.py`: Tools for multi-stage builds and layer reduction.
- `security_scanner.py`: Integration with tools like Trivy or Grype.

## Navigation Links
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Security Policy**: [SECURITY.md](SECURITY.md)
- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [README](../../../README.md)
