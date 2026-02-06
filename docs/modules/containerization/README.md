# Containerization Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Docker container management, image building, and orchestration.

## Key Features

- **Images** — Build Docker images
- **Containers** — Manage container lifecycle
- **Compose** — Docker Compose support
- **Registry** — Push/pull from registries

## Quick Start

```python
from codomyrmex.containerization import ContainerManager, ImageBuilder

builder = ImageBuilder()
image = builder.build("./Dockerfile", tag="myapp:v1")

manager = ContainerManager()
container = manager.run(image, ports={"8080": 8080})
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/containerization/](../../../src/codomyrmex/containerization/)
- **Parent**: [Modules](../README.md)
