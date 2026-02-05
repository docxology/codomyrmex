# containerization/docker

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Docker container management utilities. Provides programmatic interfaces for building, running, inspecting, and managing Docker containers and images, plus Docker Compose orchestration for multi-service environments.

## Key Exports

### Data Classes

- **`ContainerConfig`** -- Full container configuration including image, name, command, entrypoint, environment variables, volume mounts, port mappings, labels, network, resource limits (memory/CPU), and restart policy. Includes `to_run_args()` to convert to `docker run` CLI arguments
- **`ImageInfo`** -- Docker image metadata: ID, repository, tag, creation date, and size. Provides `full_name` property returning `repository:tag`
- **`ContainerInfo`** -- Running container metadata: ID, name, image, status, ports, and creation date. Provides `is_running` property based on status string

### Clients

- **`DockerClient`** -- Full Docker CLI wrapper with methods for:
  - `build()` -- Build images with Dockerfile, tags, build args, multi-stage targets, and cache control
  - `run()` -- Run containers in detach or foreground mode with full `ContainerConfig` support
  - `stop()` / `remove()` -- Stop and remove containers with force and timeout options
  - `logs()` -- Retrieve container logs with optional follow (streaming) and tail support
  - `exec()` -- Execute commands inside running containers with user and workdir options
  - `list_containers()` -- List containers with optional filters; parses JSON output
  - `list_images()` -- List images with optional repository filter
  - `pull()` / `push()` / `tag()` -- Registry operations for images
- **`DockerComposeClient`** -- Docker Compose wrapper for multi-service orchestration:
  - `up()` -- Start services with optional build and detach
  - `down()` -- Stop services with optional volume cleanup and orphan removal
  - `ps()` -- List running services in JSON format

## Directory Contents

- `__init__.py` - Docker client classes, config dataclasses, and image/container info models (445 lines)
- `build_generator.py` - Dockerfile generation utilities
- `docker_manager.py` - Higher-level Docker management operations
- `image_optimizer.py` - Docker image optimization and layer analysis
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [containerization](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
