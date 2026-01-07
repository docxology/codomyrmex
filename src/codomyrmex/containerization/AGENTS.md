# Codomyrmex Agents — src/codomyrmex/containerization

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Container management including Docker image building, container orchestration, Kubernetes integration, container registry management, image optimization, security scanning, and performance optimization. Provides comprehensive container lifecycle management.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `build_generator.py` – Dockerfile and build configuration generation
- `container_registry.py` – Container registry management
- `docker_manager.py` – Docker container and image management
- `image_optimizer.py` – Image optimization
- `kubernetes_orchestrator.py` – Kubernetes orchestration
- `performance_optimizer.py` – Performance optimization
- `security_scanner.py` – Security scanning

## Key Classes and Functions

### DockerManager (`docker_manager.py`)
- `DockerManager()` – Docker container and image management
- `build_image(dockerfile: str, tag: str, **kwargs) -> str` – Build Docker image
- `run_container(image: str, **kwargs) -> str` – Run Docker container
- `stop_container(container_id: str) -> bool` – Stop container
- `get_container_status(container_id: str) -> ContainerStatus` – Get container status

### ContainerRegistry (`container_registry.py`)
- `ContainerRegistry()` – Container registry management
- `push_image(image: str, registry: str, tag: str) -> bool` – Push image to registry
- `pull_image(image: str, registry: str, tag: str) -> bool` – Pull image from registry
- `list_images(registry: str) -> list[str]` – List images in registry

### KubernetesOrchestrator (`kubernetes_orchestrator.py`)
- `KubernetesOrchestrator()` – Kubernetes orchestration
- `deploy_to_kubernetes(config: dict) -> DeploymentResult` – Deploy to Kubernetes
- `scale_deployment(name: str, replicas: int) -> bool` – Scale deployment
- `get_deployment_status(name: str) -> DeploymentStatus` – Get deployment status

### ImageOptimizer (`image_optimizer.py`)
- `ImageOptimizer()` – Image optimization
- `optimize_image(image: str, **kwargs) -> str` – Optimize Docker image
- `analyze_image_size(image: str) -> ImageAnalysis` – Analyze image size

### SecurityScanner (`security_scanner.py`)
- `SecurityScanner()` – Security scanning
- `scan_image(image: str) -> SecurityScanResult` – Scan image for vulnerabilities
- `check_compliance(image: str, policy: dict) -> ComplianceResult` – Check compliance

### BuildGenerator (`build_generator.py`)
- `BuildGenerator()` – Dockerfile and build configuration generation
- `generate_dockerfile(config: dict) -> str` – Generate Dockerfile
- `generate_docker_compose(config: dict) -> str` – Generate docker-compose.yml

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation