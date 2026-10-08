# Containerization - API Specification

## Introduction

This API specification documents the programmatic interfaces for the Containerization module of Codomyrmex. The module provides comprehensive container management, orchestration, and deployment capabilities for the Codomyrmex ecosystem, supporting Docker container lifecycle management and Kubernetes orchestration.

## Functions

All functions below are importable from `codomyrmex.containerization`. Each one is exported only when its backing dependency imports (`HAS_DOCKER_MANAGER`, `HAS_REGISTRY`, `HAS_K8S`, `HAS_SCANNER` and `HAS_OPTIMIZER` report which ones are available); `orchestrate_kubernetes` needs the `kubernetes` Python client.

### Function: `build_containers(config: ContainerConfig, push: bool = False, registry_auth: dict[str, str] | None = None) -> dict[str, Any]`

- **Description**: Build a Docker image from a `ContainerConfig` with a new `DockerManager` (`DockerManager.build_image()`), optionally pushing it afterwards.
- **Parameters**:
    - `config`: Container configuration; `image_name`, `tag`, `dockerfile_path`, `build_context` and `build_args` drive the build.
    - `push`: Push the image after building. The push only happens when `registry_auth` is also given.
    - `registry_auth`: Registry credentials passed to `DockerManager.push_image()`.
- **Return Value**:

    ```python
    {
        "success": True,
        "image_id": <str>,
        "image_tags": [<str>],
        "build_logs": [<str>],
        "build_time": <ISO-8601 timestamp>,
        "push_result": {<push details>}  # only when pushed
    }
    ```

- **Errors**: Does not raise for build failures: returns `{"success": False, "error": <message>}`, including when the Docker daemon is unreachable.

### Function: `manage_containers() -> DockerManager`

- **Description**: Create a `DockerManager` connected to the default Docker daemon. Use its methods for lifecycle operations: `run_container()`, `list_containers()`, `stop_container()`, `remove_container()`, `get_container_logs()`, `get_container_stats()`, `create_network()`, `list_images()`, `remove_image()`, `push_image()` and `get_docker_info()`. Call `close()` when done.
- **Parameters**: None. Construct `DockerManager(docker_host=...)` directly to target another daemon.
- **Return Value**: A `DockerManager`; its `client` is `None` when the daemon is not reachable.

### Function: `orchestrate_kubernetes(deployment_config: dict[str, Any], kubeconfig_path: str | None = None) -> dict[str, Any]`

- **Description**: Create a Kubernetes deployment (and optionally a service) from a configuration mapping with a `KubernetesOrchestrator`.
- **Parameters**:
    - `deployment_config`: Mapping with `name`, `namespace` (default `"default"`), `image`, `replicas`, `port`, `container_port`, `environment_variables`, `labels` and `resources`. Set `create_service` to also create a service (`service_name`, `service_type`, default `"ClusterIP"`).
    - `kubeconfig_path`: Path to a kubeconfig file (default: `~/.kube/config` when it exists).
- **Return Value**:

    ```python
    {
        "deployment_name": <str>,
        "status": "created",
        "namespace": <str>,
        "available": <bool>,
        "message": <str>
    }
    ```

### Function: `scan_container_security(image: str, scanner: ContainerSecurityScanner | None = None, **kwargs) -> SecurityScanResult`

- **Description**: Scan a container image for vulnerabilities with the Trivy CLI.
- **Parameters**:
    - `image`: Image name and tag to scan.
    - `scanner`: Pre-configured `ContainerSecurityScanner` (default: a new one).
    - `**kwargs`: Passed to `ContainerSecurityScanner.scan_image()`; `severity_filter` (list of severities such as `["critical", "high"]`) limits what Trivy reports.
- **Return Value**: A `SecurityScanResult`. `passed` is False when any critical or high vulnerability is found, or with `error` set when Trivy fails.
- **Errors**: Raises `NotImplementedError` when the Trivy CLI is not installed.

### Function: `manage_container_registry(operation: str, registry_url: str, credentials: dict[str, str] | None = None, **kwargs: Any) -> Any`

- **Description**: Run one registry operation through a `ContainerRegistry`.
- **Parameters**:
    - `operation`: One of `"push"`, `"pull"`, `"build_and_push"`, `"list"`, `"list_registry"`, `"delete"`, `"info"`, `"tag"` or `"manifest"`.
    - `registry_url`: Registry URL, for example `docker.io` or `ghcr.io`.
    - `credentials`: Optional mapping with `username`, `password` and `token`.
    - `**kwargs`: Operation arguments, forwarded to the matching `ContainerRegistry` method: `image_name`, `image_tag`, `local_image` (push); `dockerfile_path`, `build_args`, `no_cache` (build_and_push); `repository`, `limit` (list, list_registry); `local_only` (delete); `source_image`, `target_name`, `target_tag` (tag).
- **Return Value**: The result of the underlying `ContainerRegistry` method (for example `push_image()`, `pull_image()` or `list_images()`).
- **Errors**: Raises `CodomyrmexError` for an unknown operation.

### Function: `optimize_containers(container_ids: list[str], optimizer: ContainerOptimizer | None = None) -> dict[str, dict[str, Any]]`

- **Description**: Produce resource recommendations for running containers by inspecting them with `docker inspect` (`ContainerOptimizer.optimize_resources()`).
- **Parameters**:
    - `container_ids`: Container IDs or names to analyze.
    - `optimizer`: Pre-configured `ContainerOptimizer` (default: a new one).
- **Return Value**: Mapping of each container ID to its recommendations (`container_id`, `status`, `cpu_shares`, `memory_limit`, plus `cpu_note`/`memory_note` when no limit is set).
- **Errors**: Raises `NotImplementedError` when the Docker CLI is not installed or `docker inspect` fails for a container.

## Data Structures

### ContainerConfig

Dataclass used by `build_containers()` and `DockerManager`:

`ContainerConfig(image_name, tag="latest", dockerfile_path=None, build_context=".", build_args={}, environment={}, ports={}, volumes={}, networks=[], restart_policy="no", labels={})`. `get_full_image_name()` returns `"<image_name>:<tag>"`.

### KubernetesDeployment

Dataclass in `codomyrmex.containerization.kubernetes.kubernetes_orchestrator`:

`KubernetesDeployment(name, image, namespace="default", replicas=1, port=80, container_port=80, environment_variables={}, volumes=[], volume_mounts=[], config_maps=[], secrets=[], labels={}, annotations={}, resources={}, created_at=<now>)`.

### ContainerRegistry

`ContainerRegistry(registry_url, credentials=None)`, where `credentials` is a `RegistryCredentials(username, password, registry_url, token=None)`. Methods include `push_image()`, `pull_image()`, `build_and_push()`, `list_images()`, `list_registry_images()`, `delete_image()`, `get_image_info()`, `tag_image()` and `inspect_manifest()`.

### SecurityScanResult

`SecurityScanResult(image, scan_time, vulnerabilities=[], passed=True, error=None, metadata={})`. Each `Vulnerability` has `id`, `severity` (`VulnerabilitySeverity`), `title`, `description`, `package`, `version`, `fixed_version` and `cve_ids`. The `critical_count` and `high_count` properties and `summary()` (counts by severity) summarize the findings.

### ContainerMetrics

`ContainerMetrics(container_id, cpu_percent=0.0, memory_usage_mb=0.0, memory_limit_mb=0.0, network_io_mb=0.0, disk_io_mb=0.0, timestamp=<now>)`, with a `memory_percent` property and `to_dict()`.

## Error Handling

The module's exceptions are exported from `codomyrmex.containerization` and inherit from `codomyrmex.exceptions.ContainerError`:

- `ContainerError(message, container_id=None, container_name=None)`: container lifecycle failures
- `ImageBuildError(message, image_name=None, image_tag=None, dockerfile_path=None, build_step=None)`: image build failures
- `RegistryError(message, registry_url=None, image_reference=None)`: registry authentication or transfer failures
- `KubernetesError(message, resource_type=None, resource_name=None, namespace=None)`: Kubernetes API or manifest failures
- `NetworkError(message, network_name=None, network_id=None, driver=None)` and `VolumeError(message, volume_name=None, mount_point=None, driver=None)`: Docker network and volume failures

`build_containers()` reports build failures in its result instead of raising; the scanner and optimizer raise `NotImplementedError` when their CLI tools are missing.

## Integration Patterns

### With CI/CD Automation

```python
from codomyrmex.ci_cd_automation import create_pipeline

# A pipeline whose build stage builds the container image
pipeline = create_pipeline({
    "name": "container_pipeline",
    "stages": [
        {"name": "build", "jobs": [{"name": "image", "commands": ["docker build -t myapp:latest ."]}]},
        {"name": "test", "jobs": [{"name": "test", "commands": ["uv run pytest"]}]},
    ],
})
```

### With Security Audit

```python
from codomyrmex.containerization import scan_container_security

# Requires the Trivy CLI
scan_result = scan_container_security("myapp:latest", severity_filter=["critical", "high"])
if not scan_result.passed:
    print(scan_result.summary())
```

### With Build Synthesis

```python
from codomyrmex.ci_cd_automation.build import create_build_manifest
from codomyrmex.containerization import ContainerConfig, build_containers

# Create container build target
container_config = ContainerConfig(
    image_name="myapp",
    tag="prod",
    dockerfile_path="Dockerfile.prod",
)
manifest = create_build_manifest({
    "name": "production_container",
    "image": container_config.get_full_image_name(),
})

# Build the image; pass push=True together with registry_auth to push it
build_result = build_containers(container_config)
```

## Security Considerations

- **Image Security**: All images are scanned for vulnerabilities before deployment
- **Registry Access**: Secure authentication and access control for registries
- **Runtime Security**: Container isolation and resource limits prevent compromise
- **Secret Management**: Environment variables and secrets are encrypted
- **Network Security**: Container networking is isolated and monitored
- **Compliance**: Container configurations meet security standards and policies

## Performance Characteristics

- **Build Optimization**: Multi-stage builds and layer caching for efficiency
- **Resource Management**: Intelligent CPU and memory allocation
- **Scalability**: Support for concurrent container operations
- **Monitoring Overhead**: Minimal performance impact from health monitoring
- **Registry Performance**: Efficient image transfer with compression and caching

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
