# Containerization - API Specification

## Introduction

This API specification documents the programmatic interfaces for the Containerization module of Codomyrmex. The module provides comprehensive container management, orchestration, and deployment capabilities for the Codomyrmex ecosystem, supporting Docker container lifecycle management and Kubernetes orchestration.

## Functions

### Function: `build_containers(image_name: str, dockerfile_path: str = "Dockerfile", context_path: str = ".", build_args: Optional[Dict] = None, **kwargs) -> Dict`

- **Description**: Build Docker containers from source code with optimization and security scanning.
- **Parameters**:
    - `image_name`: Name/tag for the resulting container image.
    - `dockerfile_path`: Path to Dockerfile (default: "Dockerfile").
    - `context_path`: Build context directory (default: ".").
    - `build_args`: Optional build arguments for Dockerfile.
    - `**kwargs`: Additional build options (cache, target, labels, etc.).
- **Return Value**:
    ```python
    {
        "image_name": <str>,
        "image_id": <str>,
        "build_time": <float>,
        "size_mb": <float>,
        "layers": <int>,
        "security_scan_passed": <bool>,
        "vulnerabilities_found": <int>,
        "optimization_applied": <bool>
    }
    ```
- **Errors**: Raises `ContainerBuildError` for build failures or security issues.

### Function: `manage_containers(operation: str, container_name: str, config: Optional[Dict] = None, **kwargs) -> Dict`

- **Description**: Manage container lifecycle including creation, starting, stopping, and removal.
- **Parameters**:
    - `operation`: Operation type (create, start, stop, remove, restart, logs).
    - `container_name`: Name of the container to manage.
    - `config`: Container configuration for create operations.
    - `**kwargs`: Operation-specific parameters.
- **Return Value**:
    ```python
    {
        "operation": <str>,
        "container_name": <str>,
        "success": <bool>,
        "container_id": <str>,
        "status": <str>,
        "execution_time": <float>,
        "logs": <str>,  # For logs operation
        "error_message": <str>
    }
    ```
- **Errors**: Raises `ContainerManagementError` for operation failures.

### Function: `orchestrate_kubernetes(deployment_name: str, manifest_path: str, namespace: str = "default", **kwargs) -> KubernetesDeployment`

- **Description**: Orchestrate Kubernetes deployments, services, and configmaps.
- **Parameters**:
    - `deployment_name`: Name of the Kubernetes deployment.
    - `manifest_path`: Path to Kubernetes manifest files.
    - `namespace`: Kubernetes namespace (default: "default").
    - `**kwargs`: Deployment options (replicas, resources, labels, etc.).
- **Return Value**: KubernetesDeployment object with status tracking and management.
- **Errors**: Raises `KubernetesError` for orchestration failures.

### Function: `scan_container_security(image_name: str, scan_type: str = "full", **kwargs) -> SecurityScanResult`

- **Description**: Scan container images for security vulnerabilities and compliance issues.
- **Parameters**:
    - `image_name`: Name of container image to scan.
    - `scan_type`: Scan scope (full, quick, compliance).
    - `**kwargs`: Scanning options (severity_threshold, ignore_rules, etc.).
- **Return Value**: SecurityScanResult with vulnerabilities, compliance status, and recommendations.
- **Errors**: Raises `SecurityScanError` for scanning failures.

### Function: `manage_container_registry(operation: str, image_name: str, registry_url: Optional[str] = None, **kwargs) -> Dict`

- **Description**: Manage container registry operations including push, pull, and tagging.
- **Parameters**:
    - `operation`: Registry operation (push, pull, tag, list, delete).
    - `image_name`: Container image name.
    - `registry_url`: Registry URL (optional, uses default if not specified).
    - `**kwargs`: Operation-specific parameters (credentials, tags, etc.).
- **Return Value**:
    ```python
    {
        "operation": <str>,
        "image_name": <str>,
        "registry_url": <str>,
        "success": <bool>,
        "image_digest": <str>,
        "tags": [<list_of_tags>],
        "size_mb": <float>,
        "error_message": <str>
    }
    ```
- **Errors**: Raises `RegistryError` for registry operation failures.

### Function: `optimize_containers(image_name: str, optimization_type: str = "size", **kwargs) -> Dict`

- **Description**: Optimize container images for performance, size, or security.
- **Parameters**:
    - `image_name`: Base image to optimize.
    - `optimization_type`: Optimization focus (size, performance, security, multi).
    - `**kwargs`: Optimization parameters (target_size, layers_to_remove, etc.).
- **Return Value**:
    ```python
    {
        "original_image": <str>,
        "optimized_image": <str>,
        "optimization_type": <str>,
        "size_reduction_mb": <float>,
        "performance_improvement": <float>,
        "security_improvements": [<list_of_fixes>],
        "layers_reduced": <int>,
        "build_time": <float>
    }
    ```
- **Errors**: Raises `OptimizationError` for optimization failures.

## Data Structures

### ContainerConfig
Configuration for container creation and management:
```python
{
    "image": <str>,
    "name": <str>,
    "command": [<list_of_command_args>],
    "environment": {<env_variables>},
    "ports": {<port_mappings>},
    "volumes": {<volume_mappings>},
    "networks": [<list_of_networks>],
    "resources": {
        "cpu_limit": <str>,
        "memory_limit": <str>,
        "cpu_reservation": <str>,
        "memory_reservation": <str>
    },
    "restart_policy": <str>,
    "labels": {<label_key_value_pairs>}
}
```

### KubernetesDeployment
Kubernetes deployment configuration and status:
```python
{
    "name": <str>,
    "namespace": <str>,
    "replicas": <int>,
    "image": <str>,
    "ports": [<list_of_ports>],
    "environment": {<env_variables>},
    "resources": {
        "requests": {"cpu": <str>, "memory": <str>},
        "limits": {"cpu": <str>, "memory": <str>}
    },
    "status": "pending|running|failed|succeeded",
    "pods": [<list_of_pod_statuses>],
    "services": [<list_of_service_names>],
    "created_at": <timestamp>,
    "last_updated": <timestamp>
}
```

### ContainerRegistry
Container registry connection and management:
```python
{
    "url": <str>,
    "type": "dockerhub|ecr|acr|gcr|harbor",
    "credentials": {
        "username": <str>,
        "password": <str>,  # Encrypted
        "token": <str>      # For token-based auth
    },
    "repositories": [<list_of_repositories>],
    "security_scan_enabled": <bool>,
    "retention_policy": {<retention_rules>}
}
```

### SecurityScanResult
Results of container security scanning:
```python
{
    "image_name": <str>,
    "scan_timestamp": <timestamp>,
    "scan_duration": <float>,
    "vulnerabilities": [
        {
            "cve_id": <str>,
            "severity": "critical|high|medium|low",
            "package": <str>,
            "version": <str>,
            "fixed_version": <str>,
            "description": <str>
        }
    ],
    "compliance_score": <float>,
    "critical_count": <int>,
    "high_count": <int>,
    "medium_count": <int>,
    "low_count": <int>,
    "recommendations": [<list_of_fixes>],
    "scan_tool": <str>
}
```

### ContainerMetrics
Container performance and resource metrics:
```python
{
    "container_name": <str>,
    "timestamp": <timestamp>,
    "cpu_usage_percent": <float>,
    "memory_usage_mb": <float>,
    "memory_limit_mb": <float>,
    "network_rx_mb": <float>,
    "network_tx_mb": <float>,
    "disk_read_mb": <float>,
    "disk_write_mb": <float>,
    "uptime_seconds": <float>,
    "restart_count": <int>,
    "health_status": "healthy|unhealthy|unknown",
    "performance_score": <float>
}
```

## Error Handling

All functions follow consistent error handling patterns:

- **Build Errors**: `ContainerBuildError` for Dockerfile or build context issues
- **Management Errors**: `ContainerManagementError` for lifecycle operation failures
- **Orchestration Errors**: `KubernetesError` for Kubernetes API or manifest issues
- **Security Errors**: `SecurityScanError` for scanning failures or vulnerabilities
- **Registry Errors**: `RegistryError` for authentication or network issues
- **Optimization Errors**: `OptimizationError` for image optimization failures

## Integration Patterns

### With CI/CD Automation
```python
from codomyrmex.containerization import build_containers
from codomyrmex.ci_cd_automation import create_pipeline

# Build container as part of CI/CD pipeline
pipeline = create_pipeline("container_pipeline", [
    {
        "name": "build",
        "jobs": [{
            "type": "container_build",
            "image_name": "myapp:latest",
            "dockerfile_path": "Dockerfile.prod"
        }]
    },
    {"name": "test", "jobs": [...]},
    {"name": "deploy", "jobs": [...]}
])
```

### With Security Audit
```python
from codomyrmex.containerization import scan_container_security
from codomyrmex.security_audit import generate_security_report

# Scan container security as part of audit
scan_result = scan_container_security("myapp:latest", scan_type="full")

# Generate comprehensive security report
report = generate_security_report(scan_result, format="pdf")
```

### With Build Synthesis
```python
from codomyrmex.containerization import build_containers, manage_container_registry
from codomyrmex.build_synthesis import create_build_target

# Create container build target
container_target = create_build_target(
    name="production_container",
    build_type="container",
    config={
        "image_name": "myapp:prod",
        "dockerfile_path": "Dockerfile.prod",
        "registry_push": True
    }
)

# Build and push container
build_result = build_containers(
    image_name="myapp:prod",
    dockerfile_path="Dockerfile.prod",
    push_to_registry=True
)
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
