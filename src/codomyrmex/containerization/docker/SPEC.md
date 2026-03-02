# Docker -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides Docker container lifecycle management, multi-stage Dockerfile generation, and image optimization analysis. Three primary classes: `DockerManager` for runtime operations via docker-py, `BuildGenerator` for Dockerfile and build script generation, and `ImageOptimizer` for image analysis and size reduction recommendations.

## Architecture

Three-class design across three files. `DockerManager` wraps `docker.from_env()` (or a custom `docker_host` URL) for image build, push, container run/stop/remove, and listing. `BuildGenerator` produces `MultiStageBuild` configurations with language-specific templates (Python, Node, Java, Go, generic). `ImageOptimizer` inspects local images via docker-py and generates `OptimizationSuggestion` objects.

## Key Classes and Methods

### DockerManager (`docker_manager.py`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `docker_host: str or None` | -- | Initialize client via `docker.from_env()` or custom host |
| `build_image` | `config: ContainerConfig, push: bool, registry_auth` | `dict` | Build image; optionally push after build |
| `push_image` | `image_name: str, auth_config: dict` | `dict` | Push image to registry with auth |
| `run_container` | `config: ContainerConfig, detach: bool` | `dict` | Run container with env, ports, volumes, networks, restart policy |
| `list_containers` | `show_all: bool` | `list[dict]` | List containers (id, name, image, status, ports) |
| `stop_container` | `container_id: str` | `dict` | Stop a running container |
| `remove_container` | `container_id: str, force: bool` | `dict` | Remove container; force removes running ones |

### ContainerConfig (`docker_manager.py`)

Dataclass configuring image builds and container runs.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `image_name` | `str` | -- | Image name |
| `tag` | `str` | `"latest"` | Image tag |
| `dockerfile_path` | `str or None` | `None` | Custom Dockerfile path |
| `build_context` | `str` | `"."` | Build context directory |
| `build_args` | `dict[str, str]` | `{}` | Docker build arguments |
| `environment` | `dict[str, str]` | `{}` | Environment variables |
| `ports` | `dict[str, str]` | `{}` | Port mappings |
| `volumes` | `dict[str, str]` | `{}` | Volume mounts |
| `networks` | `list[str]` | `[]` | Network names (first used for `run_container`) |
| `restart_policy` | `str` | `"no"` | Restart policy name |
| `labels` | `dict[str, str]` | `{}` | Container labels |

### BuildGenerator (`build_generator.py`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_multi_stage_build` | `config: dict` | `MultiStageBuild` | Create multi-stage build from config; dispatches by `build_type` |
| `generate_dockerfile` | `config: dict` | `str` | Generate complete Dockerfile string |
| `generate_build_script` | `config: dict` | `BuildScript` | Generate shell build script |

#### Supporting Dataclasses

- **`BuildStage`**: `name, base_image, commands, copy_commands, labels, environment, working_directory, user` with `to_dockerfile()`.
- **`MultiStageBuild`**: `stages: list[BuildStage], final_stage, metadata` with `to_dockerfile()` producing a complete multi-stage Dockerfile.
- **`BuildScript`**: `name, dockerfile_path, context_path, build_args, tags, push_targets, dependencies` with `to_shell_script()`.

### ImageOptimizer (`image_optimizer.py`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze_image` | `image_name: str` | `ImageAnalysis` | Inspect image layers, ports, env, commands; compute optimization score |
| `optimize_image` | `config: dict` | `dict` | Apply optimization recommendations to config |

#### Supporting Dataclasses

- **`ImageAnalysis`**: `image_name, size_bytes, layers, base_image, exposed_ports, volumes, environment_vars, commands, potential_optimizations, optimization_score` with `to_dict()`.
- **`OptimizationSuggestion`**: `category, description, impact, effort, dockerfile_changes, size_reduction_mb` with `to_dict()`.

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `docker` (docker-py >= 6.0.0), `logging`

## Constraints

- `DockerManager._initialize_client` calls `client.ping()` to verify connectivity; sets `self.client = None` on failure.
- `run_container` uses only the first network from `config.networks`.
- `build_image` always sets `rm=True` and `pull=True` for builds.
- `BuildGenerator.create_multi_stage_build` dispatches by `build_type` key: `python`, `node`, `java`, `go`, or generic.
- `ImageOptimizer` requires docker-py at runtime; logs a warning and disables features if unavailable.
- `ImageAnalysis.to_dict()` converts `size_bytes` to MB for display.

## Error Handling

- `DockerManager` methods catch `Exception`, log via `logger.error`, and return `{"success": False, "error": str(e)}`.
- `ImageOptimizer.analyze_image` raises `ValueError` for `ImageNotFound` and re-raises other exceptions.
- `BuildGenerator` methods delegate to internal template methods that may raise on invalid config.
