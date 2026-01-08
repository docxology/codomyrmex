from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import os
import time

from dataclasses import dataclass, field
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger






#!/usr/bin/env python3
"""
Kubernetes Orchestration Module for Codomyrmex Containerization.

This module provides Kubernetes orchestration, deployment management,
and container orchestration capabilities using the official Kubernetes
Python client.
"""



logger = get_logger(__name__)

# Try to import kubernetes client
try:
    KUBERNETES_AVAILABLE = True
except ImportError:
    client = None
    config = None
    ApiException = Exception
    KUBERNETES_AVAILABLE = False
    logger.warning(
        "Kubernetes client not available. Install with: pip install kubernetes"
    )


@dataclass
class KubernetesDeployment:
    """Kubernetes deployment configuration."""
    name: str
    image: str
    namespace: str = "default"
    replicas: int = 1
    port: int = 80
    container_port: int = 80
    environment_variables: dict[str, str] = field(default_factory=dict)
    volumes: list[dict[str, Any]] = field(default_factory=list)
    volume_mounts: list[dict[str, Any]] = field(default_factory=list)
    config_maps: list[str] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    resources: dict[str, dict[str, str]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class KubernetesService:
    """Kubernetes service configuration."""
    name: str
    namespace: str = "default"
    type: str = "ClusterIP"  # ClusterIP, NodePort, LoadBalancer
    port: int = 80
    target_port: int = 80
    node_port: Optional[int] = None
    selector: dict[str, str] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)


class KubernetesOrchestrator:
    """Kubernetes orchestration and deployment management system."""

    def __init__(
        self,
        kubeconfig_path: Optional[str] = None,
        in_cluster: bool = False
    ):
        """Initialize Kubernetes orchestrator.

        Args:
            kubeconfig_path: Path to Kubernetes configuration file
            in_cluster: Whether running inside a Kubernetes cluster
        """
        self.kubeconfig_path = kubeconfig_path
        self.in_cluster = in_cluster
        self._core_api = None
        self._apps_api = None
        self._configured = False

        self._initialize_client()

    def _initialize_client(self):
        """Initialize Kubernetes client."""
        if not KUBERNETES_AVAILABLE:
            logger.warning("Kubernetes client not available - operations will be simulated")
            return

        try:
            if self.in_cluster:
                config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes configuration")
            elif self.kubeconfig_path:
                config.load_kube_config(config_file=self.kubeconfig_path)
                logger.info(f"Loaded Kubernetes config from: {self.kubeconfig_path}")
            else:
                # Try default locations
                default_path = os.path.expanduser("~/.kube/config")
                if os.path.exists(default_path):
                    config.load_kube_config(config_file=default_path)
                    logger.info("Loaded Kubernetes config from default location")
                else:
                    logger.warning("No Kubernetes configuration found")
                    return

            self._core_api = client.CoreV1Api()
            self._apps_api = client.AppsV1Api()
            self._configured = True
            logger.info("Kubernetes client initialized successfully")

        except Exception as e:
            logger.warning(f"Failed to initialize Kubernetes client: {e}")
            self._configured = False

    def is_available(self) -> bool:
        """Check if Kubernetes is available and configured."""
        return KUBERNETES_AVAILABLE and self._configured

    def create_deployment(self, deployment: KubernetesDeployment) -> str:
        """Create a Kubernetes deployment.

        Args:
            deployment: Deployment configuration

        Returns:
            Deployment name

        Raises:
            CodomyrmexError: If deployment creation fails
        """
        if not self.is_available():
            logger.info(f"[SIMULATED] Created deployment: {deployment.name}")
            return deployment.name

        # Build container spec
        env_vars = [
            client.V1EnvVar(name=k, value=v)
            for k, v in deployment.environment_variables.items()
        ]

        resources = None
        if deployment.resources:
            resources = client.V1ResourceRequirements(
                limits=deployment.resources.get("limits"),
                requests=deployment.resources.get("requests")
            )

        container = client.V1Container(
            name=deployment.name,
            image=deployment.image,
            ports=[client.V1ContainerPort(container_port=deployment.container_port)],
            env=env_vars if env_vars else None,
            resources=resources
        )

        # Build labels
        labels = {"app": deployment.name}
        labels.update(deployment.labels)

        # Build pod template
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels=labels,
                annotations=deployment.annotations or None
            ),
            spec=client.V1PodSpec(containers=[container])
        )

        # Build deployment spec
        spec = client.V1DeploymentSpec(
            replicas=deployment.replicas,
            selector=client.V1LabelSelector(match_labels={"app": deployment.name}),
            template=template
        )

        # Build deployment
        deployment_manifest = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(
                name=deployment.name,
                namespace=deployment.namespace,
                labels=labels,
                annotations=deployment.annotations or None
            ),
            spec=spec
        )

        try:
            self._apps_api.create_namespaced_deployment(
                namespace=deployment.namespace,
                body=deployment_manifest
            )
            logger.info(f"Created Kubernetes deployment: {deployment.name}")
            return deployment.name

        except ApiException as e:
            if e.status == 409:
                logger.warning(f"Deployment already exists: {deployment.name}")
                return deployment.name
            raise CodomyrmexError(f"Failed to create deployment: {e}")

    def create_service(self, service: KubernetesService) -> str:
        """Create a Kubernetes service.

        Args:
            service: Service configuration

        Returns:
            Service name

        Raises:
            CodomyrmexError: If service creation fails
        """
        if not self.is_available():
            logger.info(f"[SIMULATED] Created service: {service.name}")
            return service.name

        # Build service port
        port = client.V1ServicePort(
            port=service.port,
            target_port=service.target_port,
            node_port=service.node_port if service.type == "NodePort" else None
        )

        # Build labels
        labels = {"app": service.name}
        labels.update(service.labels)

        # Build selector
        selector = service.selector or {"app": service.name}

        # Build service spec
        service_manifest = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(
                name=service.name,
                namespace=service.namespace,
                labels=labels
            ),
            spec=client.V1ServiceSpec(
                type=service.type,
                ports=[port],
                selector=selector
            )
        )

        try:
            self._core_api.create_namespaced_service(
                namespace=service.namespace,
                body=service_manifest
            )
            logger.info(f"Created Kubernetes service: {service.name}")
            return service.name

        except ApiException as e:
            if e.status == 409:
                logger.warning(f"Service already exists: {service.name}")
                return service.name
            raise CodomyrmexError(f"Failed to create service: {e}")

    def scale_deployment(
        self,
        deployment_name: str,
        replicas: int,
        namespace: str = "default"
    ) -> bool:
        """Scale a Kubernetes deployment.

        Args:
            deployment_name: Name of the deployment to scale
            replicas: Target number of replicas
            namespace: Kubernetes namespace

        Returns:
            True if scaled successfully
        """
        if not self.is_available():
            logger.info(f"[SIMULATED] Scaled {deployment_name} to {replicas} replicas")
            return True

        try:
            # Get current deployment
            deployment = self._apps_api.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )

            # Update replicas
            deployment.spec.replicas = replicas

            self._apps_api.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )

            logger.info(f"Scaled deployment {deployment_name} to {replicas} replicas")
            return True

        except ApiException as e:
            logger.error(f"Failed to scale deployment {deployment_name}: {e}")
            return False

    def get_deployment_status(
        self,
        deployment_name: str,
        namespace: str = "default"
    ) -> Optional[dict[str, Any]]:
        """Get deployment status.

        Args:
            deployment_name: Name of the deployment
            namespace: Kubernetes namespace

        Returns:
            Deployment status information
        """
        if not self.is_available():
            return {
                "name": deployment_name,
                "namespace": namespace,
                "status": "simulated",
                "replicas": 0,
                "available_replicas": 0,
                "ready": False
            }

        try:
            deployment = self._apps_api.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )

            status = deployment.status
            spec = deployment.spec

            return {
                "name": deployment_name,
                "namespace": namespace,
                "status": "running" if status.available_replicas else "pending",
                "replicas": spec.replicas,
                "ready_replicas": status.ready_replicas or 0,
                "available_replicas": status.available_replicas or 0,
                "updated_replicas": status.updated_replicas or 0,
                "conditions": [
                    {
                        "type": c.type,
                        "status": c.status,
                        "reason": c.reason,
                        "message": c.message
                    }
                    for c in (status.conditions or [])
                ],
                "ready": status.available_replicas == spec.replicas
            }

        except ApiException as e:
            if e.status == 404:
                return None
            logger.error(f"Failed to get deployment status: {e}")
            return None

    def list_deployments(self, namespace: str = "default") -> list[dict[str, Any]]:
        """List all deployments in a namespace.

        Args:
            namespace: Kubernetes namespace

        Returns:
            List of deployment information
        """
        if not self.is_available():
            return []

        try:
            deployments = self._apps_api.list_namespaced_deployment(namespace=namespace)

            return [
                {
                    "name": d.metadata.name,
                    "namespace": d.metadata.namespace,
                    "replicas": d.spec.replicas,
                    "available_replicas": d.status.available_replicas or 0,
                    "image": d.spec.template.spec.containers[0].image if d.spec.template.spec.containers else None,
                    "created_at": d.metadata.creation_timestamp.isoformat() if d.metadata.creation_timestamp else None
                }
                for d in deployments.items
            ]

        except ApiException as e:
            logger.error(f"Failed to list deployments: {e}")
            return []

    def delete_deployment(
        self,
        deployment_name: str,
        namespace: str = "default"
    ) -> bool:
        """Delete a Kubernetes deployment.

        Args:
            deployment_name: Name of the deployment
            namespace: Kubernetes namespace

        Returns:
            True if deleted successfully
        """
        if not self.is_available():
            logger.info(f"[SIMULATED] Deleted deployment: {deployment_name}")
            return True

        try:
            self._apps_api.delete_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            logger.info(f"Deleted deployment: {deployment_name}")
            return True

        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Deployment not found: {deployment_name}")
                return False
            logger.error(f"Failed to delete deployment: {e}")
            return False

    def delete_service(
        self,
        service_name: str,
        namespace: str = "default"
    ) -> bool:
        """Delete a Kubernetes service.

        Args:
            service_name: Name of the service
            namespace: Kubernetes namespace

        Returns:
            True if deleted successfully
        """
        if not self.is_available():
            logger.info(f"[SIMULATED] Deleted service: {service_name}")
            return True

        try:
            self._core_api.delete_namespaced_service(
                name=service_name,
                namespace=namespace
            )
            logger.info(f"Deleted service: {service_name}")
            return True

        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Service not found: {service_name}")
                return False
            logger.error(f"Failed to delete service: {e}")
            return False

    def get_pod_logs(
        self,
        pod_name: str,
        namespace: str = "default",
        container: Optional[str] = None,
        tail_lines: int = 100
    ) -> str:
        """Get logs from a pod.

        Args:
            pod_name: Name of the pod
            namespace: Kubernetes namespace
            container: Specific container name (optional)
            tail_lines: Number of lines to retrieve

        Returns:
            Pod logs as string
        """
        if not self.is_available():
            return "[SIMULATED] No logs available"

        try:
            logs = self._core_api.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container,
                tail_lines=tail_lines
            )
            return logs

        except ApiException as e:
            logger.error(f"Failed to get pod logs: {e}")
            return f"Error retrieving logs: {e}"

    def list_pods(
        self,
        namespace: str = "default",
        label_selector: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """List pods in a namespace.

        Args:
            namespace: Kubernetes namespace
            label_selector: Label selector string (e.g., "app=myapp")

        Returns:
            List of pod information
        """
        if not self.is_available():
            return []

        try:
            pods = self._core_api.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector
            )

            return [
                {
                    "name": p.metadata.name,
                    "namespace": p.metadata.namespace,
                    "status": p.status.phase,
                    "ip": p.status.pod_ip,
                    "node": p.spec.node_name,
                    "containers": [c.name for c in p.spec.containers],
                    "created_at": p.metadata.creation_timestamp.isoformat() if p.metadata.creation_timestamp else None
                }
                for p in pods.items
            ]

        except ApiException as e:
            logger.error(f"Failed to list pods: {e}")
            return []

    def apply_manifest(
        self,
        manifest: dict[str, Any],
        namespace: str = "default"
    ) -> dict[str, Any]:
        """Apply a Kubernetes manifest.

        Args:
            manifest: Kubernetes manifest as dict
            namespace: Default namespace if not specified in manifest

        Returns:
            Result of the apply operation
        """
        if not self.is_available():
            return {"status": "simulated", "kind": manifest.get("kind", "Unknown")}

        kind = manifest.get("kind", "").lower()
        metadata = manifest.get("metadata", {})
        name = metadata.get("name", "unknown")
        ns = metadata.get("namespace", namespace)

        try:
            if kind == "deployment":
                self._apps_api.create_namespaced_deployment(namespace=ns, body=manifest)
            elif kind == "service":
                self._core_api.create_namespaced_service(namespace=ns, body=manifest)
            elif kind == "configmap":
                self._core_api.create_namespaced_config_map(namespace=ns, body=manifest)
            elif kind == "secret":
                self._core_api.create_namespaced_secret(namespace=ns, body=manifest)
            else:
                return {"status": "error", "message": f"Unsupported kind: {kind}"}

            logger.info(f"Applied {kind}/{name} in namespace {ns}")
            return {"status": "created", "kind": kind, "name": name, "namespace": ns}

        except ApiException as e:
            if e.status == 409:
                return {"status": "exists", "kind": kind, "name": name, "namespace": ns}
            raise CodomyrmexError(f"Failed to apply manifest: {e}")

    def apply_yaml_file(self, yaml_path: str, namespace: str = "default") -> list[dict[str, Any]]:
        """Apply manifests from a YAML file.

        Args:
            yaml_path: Path to YAML file
            namespace: Default namespace

        Returns:
            List of apply results
        """
        results = []
        path = Path(yaml_path)

        if not path.exists():
            raise CodomyrmexError(f"YAML file not found: {yaml_path}")

        with open(path, 'r') as f:
            documents = list(yaml.safe_load_all(f))

        for doc in documents:
            if doc:  # Skip empty documents
                result = self.apply_manifest(doc, namespace)
                results.append(result)

        return results


def orchestrate_kubernetes(
    deployment_config: dict[str, Any],
    kubeconfig_path: Optional[str] = None
) -> dict[str, Any]:
    """Orchestrate Kubernetes deployment.

    Args:
        deployment_config: Deployment configuration
        kubeconfig_path: Path to Kubernetes configuration

    Returns:
        Orchestration result
    """
    orchestrator = KubernetesOrchestrator(kubeconfig_path=kubeconfig_path)

    # Create deployment from config
    deployment = KubernetesDeployment(
        name=deployment_config.get("name", "default-deployment"),
        namespace=deployment_config.get("namespace", "default"),
        image=deployment_config.get("image", "nginx:latest"),
        replicas=deployment_config.get("replicas", 1),
        port=deployment_config.get("port", 80),
        container_port=deployment_config.get("container_port", 80),
        environment_variables=deployment_config.get("environment_variables", {}),
        labels=deployment_config.get("labels", {}),
        resources=deployment_config.get("resources", {})
    )

    deployment_name = orchestrator.create_deployment(deployment)

    # Optionally create service
    if deployment_config.get("create_service", False):
        service = KubernetesService(
            name=deployment_config.get("service_name", deployment.name),
            namespace=deployment.namespace,
            type=deployment_config.get("service_type", "ClusterIP"),
            port=deployment.port,
            target_port=deployment.container_port,
            selector={"app": deployment.name}
        )
        orchestrator.create_service(service)

    return {
        "deployment_name": deployment_name,
        "status": "created",
        "namespace": deployment.namespace,
        "available": orchestrator.is_available(),
        "message": f"Kubernetes deployment {deployment.name} created successfully"
    }
