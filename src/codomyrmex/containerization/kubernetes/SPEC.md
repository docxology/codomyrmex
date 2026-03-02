# Kubernetes -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides Kubernetes deployment and service management via the official `kubernetes` Python client. Supports deployment CRUD, service creation, replica scaling, deployment status introspection, and namespace-scoped listing. Operates in real mode when a cluster is reachable, or simulation mode when the Kubernetes client is unavailable.

## Architecture

Single-class design. `KubernetesOrchestrator` initializes both `CoreV1Api` and `AppsV1Api` from the Kubernetes client library. Supports three initialization paths: in-cluster config (`load_incluster_config`), explicit kubeconfig path, or default `~/.kube/config`. When the client is unavailable, all operations log simulated results and return safe defaults.

## Key Classes and Methods

### KubernetesOrchestrator

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `kubeconfig_path: str or None, in_cluster: bool` | -- | Initialize client; tries in-cluster, explicit path, or `~/.kube/config` |
| `is_available` | (none) | `bool` | Check if Kubernetes is configured and reachable |
| `create_deployment` | `deployment: KubernetesDeployment` | `str` | Create namespaced deployment; returns deployment name |
| `create_service` | `service: KubernetesService` | `str` | Create namespaced service; returns service name |
| `scale_deployment` | `deployment_name, replicas: int, namespace` | `bool` | Patch deployment replica count |
| `get_deployment_status` | `deployment_name, namespace` | `dict or None` | Status with replicas, conditions, readiness |
| `list_deployments` | `namespace: str` | `list[dict]` | All deployments in namespace (name, replicas, image, created_at) |
| `delete_deployment` | `deployment_name, namespace` | `bool` | Delete namespaced deployment |

### KubernetesDeployment (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | -- | Deployment name |
| `image` | `str` | -- | Container image |
| `namespace` | `str` | `"default"` | Kubernetes namespace |
| `replicas` | `int` | `1` | Desired replica count |
| `port` | `int` | `80` | Service port |
| `container_port` | `int` | `80` | Container port |
| `environment_variables` | `dict[str, str]` | `{}` | Environment variables |
| `volumes` | `list[dict]` | `[]` | Volume specifications |
| `volume_mounts` | `list[dict]` | `[]` | Volume mount specifications |
| `config_maps` | `list[str]` | `[]` | ConfigMap references |
| `secrets` | `list[str]` | `[]` | Secret references |
| `labels` | `dict[str, str]` | `{}` | Pod labels |
| `annotations` | `dict[str, str]` | `{}` | Pod annotations |
| `resources` | `dict` | `{}` | Resource requests and limits |

### KubernetesService (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | -- | Service name |
| `namespace` | `str` | `"default"` | Kubernetes namespace |
| `type` | `str` | `"ClusterIP"` | Service type: ClusterIP, NodePort, or LoadBalancer |
| `port` | `int` | `80` | Service port |
| `target_port` | `int` | `80` | Target container port |
| `node_port` | `int or None` | `None` | NodePort (only for type=NodePort) |
| `selector` | `dict[str, str]` | `{}` | Pod selector; defaults to `{"app": name}` |
| `labels` | `dict[str, str]` | `{}` | Service labels |

## Dependencies

- **Internal**: `codomyrmex.exceptions.CodomyrmexError`, `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `kubernetes` (>= 25.0.0), `yaml`, `logging`

## Constraints

- `create_deployment` and `create_service` return the resource name on HTTP 409 (already exists) rather than raising.
- `node_port` is only set on the service port spec when `service.type == "NodePort"`.
- `get_deployment_status` returns `None` for HTTP 404 (not found).
- All label sets include `{"app": name}` merged with user-provided labels.
- When `is_available()` returns `False`, all CRUD operations log `[SIMULATED]` and return safe defaults.
- `scale_deployment` reads the current deployment, patches `spec.replicas`, and writes back.

## Error Handling

- `_initialize_client` catches all exceptions and sets `_configured = False` on failure.
- CRUD methods raise `CodomyrmexError` for non-409 `ApiException` failures.
- `get_deployment_status` and `list_deployments` catch `ApiException` and return `None` or `[]`.
