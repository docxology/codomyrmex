# build_synthesis

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Build automation, dependency management, artifact synthesis, and deployment orchestration. Takes raw source code, configuration, and assets, and transforms them into deployable artifacts (Python packages, Docker images, static sites). Abstracts complexities of different build systems (pip, docker, npm) behind a unified Pythonic interface with support for cross-language builds and parallel execution.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `build_manager.py` – File
- `build_orchestrator.py` – File
- `docs/` – Subdirectory
- `requirements.txt` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.build_synthesis import (
    BuildManager,
    BuildTarget,
    BuildType,
    create_python_build_target,
    trigger_build,
    orchestrate_build_pipeline,
)

# Create Python build target
target = create_python_build_target(
    name="myapp",
    source_dir="src/",
    output_dir="dist/"
)

# Build project
build_mgr = BuildManager()
result = trigger_build(target)
print(f"Build status: {result.status}")
print(f"Artifacts: {result.artifacts}")

# Orchestrate complete build pipeline
pipeline_result = orchestrate_build_pipeline(
    steps=[
        {"name": "install_deps", "command": "pip install -r requirements.txt"},
        {"name": "build", "command": "python setup.py build"},
        {"name": "test", "command": "pytest"}
    ],
    target=target
)
print(f"Pipeline completed: {pipeline_result.success}")

# Create Docker build target
docker_target = create_docker_build_target(
    name="myapp",
    dockerfile="Dockerfile",
    tag="myapp:latest"
)
```

