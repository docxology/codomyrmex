# Codomyrmex Agents — src/codomyrmex/containerization

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Containerization Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core Service Layer module providing container management, orchestration, and deployment capabilities for the Codomyrmex platform. This module handles Docker container lifecycle management, Kubernetes orchestration, and container security scanning.

The containerization module serves as the deployment and scaling layer, enabling consistent and reliable application deployment across different environments.

## Module Overview

### Key Capabilities
- **Container Building**: Automated Docker image building and optimization
- **Container Management**: Container lifecycle operations (start, stop, monitor)
- **Kubernetes Orchestration**: Cluster management and application deployment
- **Security Scanning**: Container vulnerability assessment and compliance
- **Registry Management**: Container registry operations and access control
- **Performance Optimization**: Container resource optimization and monitoring

### Key Features
- Multi-stage Docker builds with optimization
- Kubernetes deployment management
- Container security scanning integration
- Registry authentication and management
- Resource monitoring and alerting
- Cross-platform container support

## Function Signatures

### Docker Management Functions

```python
def build_containers(
    config: ContainerConfig,
    push: bool = False,
    registry_auth: Optional[dict[str, str]] = None,
) -> dict[str, Any]
```

Build Docker containers from configuration.

**Parameters:**
- `config` (ContainerConfig): Container build configuration
- `push` (bool): Whether to push image to registry after building. Defaults to False
- `registry_auth` (Optional[dict[str, str]]): Registry authentication credentials

**Returns:** `dict[str, Any]` - Build results with image ID, size, and status

```python
def manage_containers() -> DockerManager
```

Get Docker container manager instance.

**Returns:** `DockerManager` - Docker management interface

### Kubernetes Orchestration Functions

```python
def orchestrate_kubernetes(
    config: KubernetesConfig,
    operation: str = "deploy",
    namespace: str = "default",
) -> dict[str, Any]
```

Orchestrate Kubernetes deployments and operations.

**Parameters:**
- `config` (KubernetesConfig): Kubernetes configuration object
- `operation` (str): Operation to perform ("deploy", "update", "delete", "status"). Defaults to "deploy"
- `namespace` (str): Kubernetes namespace. Defaults to "default"

**Returns:** `dict[str, Any]` - Operation results with deployment status and resources

### Security Scanning Functions

```python
def scan_container_security(
    image_name: str,
    scan_type: str = "vulnerability",
    registry_auth: Optional[dict[str, str]] = None,
) -> dict[str, Any]
```

Scan container images for security vulnerabilities.

**Parameters:**
- `image_name` (str): Container image name or ID to scan
- `scan_type` (str): Type of security scan ("vulnerability", "compliance", "secrets"). Defaults to "vulnerability"
- `registry_auth` (Optional[dict[str, str]]): Registry authentication for private images

**Returns:** `dict[str, Any]` - Security scan results with vulnerabilities, severity levels, and recommendations

### Performance Optimization Functions

```python
def optimize_containers(
    config: ContainerConfig,
    optimization_level: str = "moderate",
) -> ContainerConfig
```

Optimize container configuration for performance.

**Parameters:**
- `config` (ContainerConfig): Container configuration to optimize
- `optimization_level` (str): Optimization level ("conservative", "moderate", "aggressive"). Defaults to "moderate"

**Returns:** `ContainerConfig` - Optimized container configuration

### Container Registry Functions

```python
def manage_container_registry(
    registry_url: str,
    operation: str = "list",
    image_name: Optional[str] = None,
    registry_auth: Optional[dict[str, str]] = None,
) -> dict[str, Any]
```

Manage container registry operations.

**Parameters:**
- `registry_url` (str): Container registry URL
- `operation` (str): Registry operation ("list", "push", "pull", "delete"). Defaults to "list"
- `image_name` (Optional[str]): Image name for operations requiring specific image
- `registry_auth` (Optional[dict[str, str]]): Registry authentication credentials

**Returns:** `dict[str, Any]` - Registry operation results

## Data Structures

### ContainerConfig
```python
class ContainerConfig:
    image_name: str
    dockerfile_path: str = "Dockerfile"
    build_context: str = "."
    build_args: dict[str, str] = None
    labels: dict[str, str] = None
    target_platforms: list[str] = None
    base_image: str = None
    ports: list[int] = None
    environment: dict[str, str] = None
    volumes: list[str] = None

    def to_dict(self) -> dict[str, Any]
    def validate(self) -> list[str]
```

Container configuration for building and deployment.

### KubernetesConfig
```python
class KubernetesConfig:
    deployment_name: str
    image_name: str
    replicas: int = 1
    ports: list[dict[str, Any]] = None
    environment: dict[str, str] = None
    volumes: list[dict[str, Any]] = None
    resources: dict[str, Any] = None
    health_checks: dict[str, Any] = None
    service_account: str = None

    def to_yaml(self) -> str
    def validate(self) -> list[str]
```

Kubernetes deployment configuration.

### DockerManager
```python
class DockerManager:
    def __init__(self, docker_host: str = None, tls_config: dict = None)

    def build_image(self, config: ContainerConfig, **kwargs) -> dict[str, Any]
    def push_image(self, image_name: str, registry_auth: dict = None) -> bool
    def pull_image(self, image_name: str, registry_auth: dict = None) -> bool
    def run_container(self, image_name: str, **kwargs) -> str
    def stop_container(self, container_id: str) -> bool
    def list_containers(self, filters: dict = None) -> list[dict[str, Any]]
    def get_container_logs(self, container_id: str) -> str
    def remove_container(self, container_id: str) -> bool
    def get_container_stats(self, container_id: str) -> dict[str, Any]
```

Docker container management interface.

### KubernetesOrchestrator
```python
class KubernetesOrchestrator:
    def __init__(self, kubeconfig_path: str = None, context: str = None)

    def deploy(self, config: KubernetesConfig) -> dict[str, Any]
    def update(self, config: KubernetesConfig) -> dict[str, Any]
    def delete(self, deployment_name: str, namespace: str = "default") -> bool
    def get_status(self, deployment_name: str, namespace: str = "default") -> dict[str, Any]
    def scale(self, deployment_name: str, replicas: int, namespace: str = "default") -> bool
    def get_logs(self, pod_name: str, namespace: str = "default") -> str
    def list_pods(self, namespace: str = "default") -> list[dict[str, Any]]
```

Kubernetes cluster orchestration interface.

### ContainerRegistry
```python
class ContainerRegistry:
    def __init__(self, registry_url: str, auth_config: dict = None)

    def list_images(self, repository: str = None) -> list[dict[str, Any]]
    def push_image(self, image_name: str, local_image: str) -> bool
    def pull_image(self, image_name: str, local_name: str = None) -> bool
    def delete_image(self, image_name: str) -> bool
    def get_image_manifest(self, image_name: str) -> dict[str, Any]
    def check_image_exists(self, image_name: str) -> bool
```

Container registry management interface.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `docker_manager.py` – Docker container lifecycle management
- `kubernetes_orchestrator.py` – Kubernetes cluster orchestration
- `container_registry.py` – Container registry operations
- `security_scanner.py` – Container security scanning
- `performance_optimizer.py` – Container performance optimization

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `SECURITY.md` – Security considerations for containerization


### Additional Files
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  
- `build_generator.py` – Build Generator Py
- `image_optimizer.py` – Image Optimizer Py

## Operating Contracts

### Universal Containerization Protocols

All container operations within the Codomyrmex platform must:

1. **Security First** - Container images scanned for vulnerabilities before deployment
2. **Resource Aware** - Containers configured with appropriate resource limits
3. **Reproducible** - Container builds produce consistent results
4. **Observable** - Container logging and monitoring integrated
5. **Scalable** - Container configurations support horizontal scaling

### Module-Specific Guidelines

#### Docker Management
- Use multi-stage builds for smaller final images
- Include security scanning in build pipelines
- Configure appropriate resource limits
- Implement health checks for containerized applications

#### Kubernetes Orchestration
- Use appropriate resource requests and limits
- Implement proper health checks and readiness probes
- Configure appropriate service accounts and RBAC
- Use namespaces for environment separation

#### Security Scanning
- Scan images before deployment to production
- Address critical and high-severity vulnerabilities
- Maintain vulnerability databases and signatures
- Generate security reports for compliance

#### Registry Management
- Use authenticated access to registries
- Implement image signing for integrity verification
- Configure appropriate access controls
- Monitor registry usage and storage

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation