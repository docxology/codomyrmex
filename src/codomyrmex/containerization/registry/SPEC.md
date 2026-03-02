# Registry -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides container registry management supporting Docker Hub, private registries, and OCI-compliant registries. Uses docker-py for image push/pull/build operations and `requests` for direct registry API calls. Supports credential-based authentication with both Bearer token and Basic auth schemes.

## Architecture

Single-class design. `ContainerRegistry` initializes a docker-py client (`docker.from_env()`) and an HTTP `requests.Session` for registry API calls. Credentials are managed via the `RegistryCredentials` dataclass which provides `get_auth_header()` for Bearer or Basic auth. When Docker is unavailable, operations return simulated results.

## Key Classes and Methods

### ContainerRegistry

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `registry_url: str, credentials: RegistryCredentials or None` | -- | Initialize Docker client and HTTP session |
| `is_available` | (none) | `bool` | Check if Docker client is initialized |
| `push_image` | `image_name, image_tag, local_image` | `dict` | Tag and push image; returns digest and size |
| `pull_image` | `image_name, image_tag` | `dict` | Pull image; returns image_id, size_mb, duration |
| `build_and_push` | `dockerfile_path, image_name, image_tag, build_args, no_cache` | `dict` | Build from Dockerfile and push in one operation |
| `list_images` | `repository: str or None` | `list[dict]` | List local images, optionally filtered by repository |
| `list_registry_images` | `repository, limit: int` | `list[dict]` | List images from registry API directly |

### ContainerImage (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | -- | Image name |
| `tag` | `str` | -- | Image tag |
| `registry_url` | `str` | -- | Registry URL |
| `size_mb` | `float` | -- | Image size in MB |
| `created_at` | `datetime` | -- | Creation timestamp |
| `digest` | `str or None` | `None` | Image digest |
| `layers` | `list[str]` | `[]` | Layer identifiers |
| `labels` | `dict[str, str]` | `{}` | Image labels |
| `vulnerabilities` | `list[dict]` | `[]` | Known vulnerabilities |

### RegistryCredentials (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `username` | `str` | -- | Registry username |
| `password` | `str` | -- | Registry password |
| `registry_url` | `str` | -- | Registry URL |
| `token` | `str or None` | `None` | Pre-obtained Bearer token |

Method `get_auth_header()` returns `"Bearer {token}"` if `token` is set, otherwise `"Basic {base64(username:password)}"`.

## Dependencies

- **Internal**: `codomyrmex.exceptions.CodomyrmexError`, `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `docker` (docker-py), `requests`, `base64`, `logging`

## Constraints

- `_get_full_image_name` treats `docker.io`, `registry.hub.docker.com`, and empty string as Docker Hub (no prefix).
- `push_image` logs in via `_docker_client.login()` before pushing when credentials are provided.
- `build_and_push` determines build context from `dockerfile_path`: if it is a file, uses parent directory as context and filename as Dockerfile; if directory, uses `"Dockerfile"` as default.
- `pull_image` computes `size_mb` by summing layer sizes from `image.history()`.
- `list_registry_images` requires `requests` to be available and a configured HTTP session.
- When Docker is unavailable, operations return `{"status": "simulated", ...}` instead of raising.

## Error Handling

- `_initialize_clients` catches `DockerException` for Docker client and silently skips if `requests` is unavailable.
- `push_image`, `pull_image`, and `build_and_push` raise `CodomyrmexError` on Docker failures.
- `pull_image` raises `CodomyrmexError` for `ImageNotFound`.
- `list_images` catches `DockerException` and returns `[]`.
