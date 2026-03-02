"""Comprehensive tests for kubernetes_orchestrator.py.

Tests cover:
- KubernetesDeployment dataclass construction, defaults, field types
- KubernetesService dataclass construction, defaults, service types
- KubernetesOrchestrator initialization and simulated mode behavior
- Deployment CRUD operations (create, list, get status, scale, delete)
- Service CRUD operations (create, delete)
- Pod operations (list, get logs)
- Manifest application (dict-based and YAML file-based)
- orchestrate_kubernetes convenience function
- Edge cases: missing YAML, multi-document YAML, empty manifests

Zero-mock policy: no unittest.mock, no MagicMock, no monkeypatch.
All tests run in simulated mode (no Kubernetes cluster required).
The kubernetes SDK IS available but no kubeconfig exists, so
KubernetesOrchestrator falls back to simulated behavior for every operation.
"""

from datetime import datetime

import pytest
import yaml

from codomyrmex.containerization.kubernetes.kubernetes_orchestrator import (
    KUBERNETES_AVAILABLE,
    KubernetesDeployment,
    KubernetesOrchestrator,
    KubernetesService,
    orchestrate_kubernetes,
)
from codomyrmex.exceptions import CodomyrmexError

# ===========================================================================
# KubernetesDeployment dataclass
# ===========================================================================


@pytest.mark.unit
class TestKubernetesDeploymentDataclass:
    """Tests for KubernetesDeployment dataclass construction and defaults."""

    def test_deployment_required_fields(self):
        """Minimum required fields produce a valid dataclass instance."""
        dep = KubernetesDeployment(name="test", image="nginx:latest")
        assert dep.name == "test"
        assert dep.image == "nginx:latest"

    def test_deployment_default_namespace(self):
        """Namespace defaults to 'default' when not provided."""
        dep = KubernetesDeployment(name="app", image="img:v1")
        assert dep.namespace == "default"

    def test_deployment_default_replicas(self):
        """Replicas defaults to 1."""
        dep = KubernetesDeployment(name="app", image="img:v1")
        assert dep.replicas == 1

    def test_deployment_with_env_vars(self):
        """Environment variables dict is stored correctly."""
        env = {"DB_HOST": "postgres", "DB_PORT": "5432"}
        dep = KubernetesDeployment(
            name="api", image="api:v1", environment_variables=env
        )
        assert dep.environment_variables == env
        assert dep.environment_variables["DB_HOST"] == "postgres"

    def test_deployment_with_port(self):
        """Port and container_port fields are stored correctly."""
        dep = KubernetesDeployment(
            name="web", image="web:v1", port=8080, container_port=3000
        )
        assert dep.port == 8080
        assert dep.container_port == 3000

    def test_deployment_default_ports(self):
        """Both port and container_port default to 80."""
        dep = KubernetesDeployment(name="app", image="img:v1")
        assert dep.port == 80
        assert dep.container_port == 80

    def test_deployment_with_labels_and_annotations(self):
        """Labels and annotations dicts are stored."""
        dep = KubernetesDeployment(
            name="app",
            image="img:v1",
            labels={"tier": "backend"},
            annotations={"prometheus.io/scrape": "true"},
        )
        assert dep.labels["tier"] == "backend"
        assert dep.annotations["prometheus.io/scrape"] == "true"

    def test_deployment_created_at_is_datetime(self):
        """created_at is auto-populated as a datetime instance."""
        dep = KubernetesDeployment(name="app", image="img:v1")
        assert isinstance(dep.created_at, datetime)

    def test_deployment_mutable_defaults_are_independent(self):
        """Mutable default fields do not share state across instances."""
        a = KubernetesDeployment(name="a", image="img")
        b = KubernetesDeployment(name="b", image="img")
        a.environment_variables["KEY"] = "val"
        a.labels["x"] = "y"
        a.volumes.append({"name": "data"})
        assert b.environment_variables == {}
        assert b.labels == {}
        assert b.volumes == []

    def test_deployment_with_resources(self):
        """Resource limits and requests are stored."""
        resources = {
            "limits": {"cpu": "500m", "memory": "512Mi"},
            "requests": {"cpu": "250m", "memory": "256Mi"},
        }
        dep = KubernetesDeployment(
            name="app", image="img:v1", resources=resources
        )
        assert dep.resources["limits"]["cpu"] == "500m"
        assert dep.resources["requests"]["memory"] == "256Mi"

    def test_deployment_custom_namespace(self):
        """Custom namespace is stored correctly."""
        dep = KubernetesDeployment(
            name="app", image="img:v1", namespace="production"
        )
        assert dep.namespace == "production"

    def test_deployment_with_secrets_and_config_maps(self):
        """Secrets and config_maps lists are stored."""
        dep = KubernetesDeployment(
            name="app",
            image="img:v1",
            config_maps=["app-config"],
            secrets=["app-secret"],
        )
        assert dep.config_maps == ["app-config"]
        assert dep.secrets == ["app-secret"]


# ===========================================================================
# KubernetesService dataclass
# ===========================================================================


@pytest.mark.unit
class TestKubernetesServiceDataclass:
    """Tests for KubernetesService dataclass construction and defaults."""

    def test_service_required_fields(self):
        """Minimum required field (name) produces a valid instance."""
        svc = KubernetesService(name="svc")
        assert svc.name == "svc"

    def test_service_clusterip_default(self):
        """Service type defaults to ClusterIP."""
        svc = KubernetesService(name="svc")
        assert svc.type == "ClusterIP"

    def test_service_nodeport_type(self):
        """NodePort type is accepted and stored."""
        svc = KubernetesService(name="svc", type="NodePort", node_port=30080)
        assert svc.type == "NodePort"
        assert svc.node_port == 30080

    def test_service_loadbalancer_type(self):
        """LoadBalancer type is accepted and stored."""
        svc = KubernetesService(name="svc", type="LoadBalancer")
        assert svc.type == "LoadBalancer"

    def test_service_default_namespace(self):
        """Namespace defaults to 'default'."""
        svc = KubernetesService(name="svc")
        assert svc.namespace == "default"

    def test_service_default_ports(self):
        """Port and target_port default to 80."""
        svc = KubernetesService(name="svc")
        assert svc.port == 80
        assert svc.target_port == 80

    def test_service_with_selector(self):
        """Selector dict is stored."""
        svc = KubernetesService(
            name="svc", selector={"app": "web", "tier": "frontend"}
        )
        assert svc.selector["app"] == "web"
        assert svc.selector["tier"] == "frontend"

    def test_service_mutable_defaults_independent(self):
        """Mutable default fields do not share state across instances."""
        a = KubernetesService(name="a")
        b = KubernetesService(name="b")
        a.selector["app"] = "a"
        a.labels["env"] = "dev"
        assert b.selector == {}
        assert b.labels == {}


# ===========================================================================
# KubernetesOrchestrator initialization
# ===========================================================================


@pytest.mark.unit
class TestKubernetesOrchestratorInit:
    """Tests for KubernetesOrchestrator initialization and availability."""

    def test_init_without_kubeconfig(self):
        """Orchestrator initializes without crashing when no kubeconfig exists."""
        orch = KubernetesOrchestrator()
        assert orch is not None
        assert isinstance(orch, KubernetesOrchestrator)

    def test_is_available_simulated(self):
        """is_available() returns False when no K8s cluster is configured."""
        orch = KubernetesOrchestrator()
        assert orch.is_available() is False

    def test_init_with_kubeconfig_path(self):
        """Passing an explicit kubeconfig_path does not crash."""
        orch = KubernetesOrchestrator(kubeconfig_path="/nonexistent/kubeconfig")
        assert orch.is_available() is False

    def test_configured_flag_false_without_cluster(self):
        """_configured is False when no cluster is reachable."""
        orch = KubernetesOrchestrator()
        assert orch._configured is False

    def test_kubernetes_sdk_available(self):
        """Module-level KUBERNETES_AVAILABLE reflects SDK import state."""
        # In this test environment the SDK is installed
        assert isinstance(KUBERNETES_AVAILABLE, bool)

    def test_init_in_cluster_mode_without_cluster(self):
        """in_cluster=True does not crash when not running in a pod."""
        orch = KubernetesOrchestrator(in_cluster=True)
        assert orch.is_available() is False


# ===========================================================================
# Deployment operations (simulated mode)
# ===========================================================================


@pytest.mark.unit
class TestKubernetesOrchestratorDeployments:
    """Tests for deployment CRUD operations in simulated mode."""

    def setup_method(self):
        self.orch = KubernetesOrchestrator()

    def test_create_deployment_returns_string(self):
        """create_deployment returns the deployment name as a string."""
        dep = KubernetesDeployment(name="test-dep", image="nginx:latest")
        result = self.orch.create_deployment(dep)
        assert isinstance(result, str)

    def test_create_deployment_has_name(self):
        """Returned string matches the deployment name."""
        dep = KubernetesDeployment(name="my-app", image="myapp:v1")
        result = self.orch.create_deployment(dep)
        assert result == "my-app"

    def test_create_deployment_with_env_vars(self):
        """Deployment with environment variables succeeds in simulated mode."""
        dep = KubernetesDeployment(
            name="env-app",
            image="app:v1",
            environment_variables={"KEY": "value", "PORT": "8080"},
        )
        result = self.orch.create_deployment(dep)
        assert result == "env-app"

    def test_list_deployments_returns_list(self):
        """list_deployments returns an empty list in simulated mode."""
        result = self.orch.list_deployments()
        assert isinstance(result, list)
        assert result == []

    def test_list_deployments_with_namespace(self):
        """list_deployments with explicit namespace returns list."""
        result = self.orch.list_deployments(namespace="production")
        assert isinstance(result, list)

    def test_delete_deployment_returns_bool(self):
        """delete_deployment returns True in simulated mode."""
        result = self.orch.delete_deployment("test-deployment")
        assert result is True

    def test_delete_deployment_with_namespace(self):
        """delete_deployment with explicit namespace returns True."""
        result = self.orch.delete_deployment("app", namespace="staging")
        assert result is True

    def test_get_deployment_status_returns_dict(self):
        """get_deployment_status returns a dict with status fields."""
        result = self.orch.get_deployment_status("test")
        assert isinstance(result, dict)
        assert "status" in result

    def test_get_deployment_status_has_name(self):
        """Returned dict contains the queried deployment name."""
        result = self.orch.get_deployment_status("my-deploy")
        assert result["name"] == "my-deploy"

    def test_get_deployment_status_has_namespace(self):
        """Returned dict contains the queried namespace."""
        result = self.orch.get_deployment_status(
            "test", namespace="staging"
        )
        assert result["namespace"] == "staging"

    def test_get_deployment_status_simulated_values(self):
        """Simulated status has expected field values."""
        result = self.orch.get_deployment_status("test")
        assert result["status"] == "simulated"
        assert result["replicas"] == 0
        assert result["available_replicas"] == 0
        assert result["ready"] is False

    def test_scale_deployment_returns_true(self):
        """scale_deployment returns True in simulated mode."""
        result = self.orch.scale_deployment("test", replicas=3)
        assert result is True

    def test_scale_deployment_with_namespace(self):
        """scale_deployment with explicit namespace returns True."""
        result = self.orch.scale_deployment(
            "test", replicas=5, namespace="production"
        )
        assert result is True


# ===========================================================================
# Service operations (simulated mode)
# ===========================================================================


@pytest.mark.unit
class TestKubernetesOrchestratorServices:
    """Tests for service CRUD operations in simulated mode."""

    def setup_method(self):
        self.orch = KubernetesOrchestrator()

    def test_create_service_returns_string(self):
        """create_service returns the service name as a string."""
        svc = KubernetesService(name="test-svc")
        result = self.orch.create_service(svc)
        assert isinstance(result, str)

    def test_create_service_has_name(self):
        """Returned string matches the service name."""
        svc = KubernetesService(name="my-service")
        result = self.orch.create_service(svc)
        assert result == "my-service"

    def test_create_service_nodeport(self):
        """Creating a NodePort service succeeds in simulated mode."""
        svc = KubernetesService(
            name="nodeport-svc",
            type="NodePort",
            port=80,
            target_port=8080,
            node_port=30080,
        )
        result = self.orch.create_service(svc)
        assert result == "nodeport-svc"

    def test_delete_service_returns_bool(self):
        """delete_service returns True in simulated mode."""
        result = self.orch.delete_service("test-service")
        assert result is True

    def test_delete_service_with_namespace(self):
        """delete_service with explicit namespace returns True."""
        result = self.orch.delete_service("svc", namespace="staging")
        assert result is True


# ===========================================================================
# Pod operations (simulated mode)
# ===========================================================================


@pytest.mark.unit
class TestKubernetesOrchestratorPods:
    """Tests for pod operations in simulated mode."""

    def setup_method(self):
        self.orch = KubernetesOrchestrator()

    def test_list_pods_returns_list(self):
        """list_pods returns an empty list in simulated mode."""
        result = self.orch.list_pods()
        assert isinstance(result, list)
        assert result == []

    def test_list_pods_with_selector(self):
        """list_pods with label_selector returns list."""
        result = self.orch.list_pods(label_selector="app=test")
        assert isinstance(result, list)

    def test_list_pods_with_namespace(self):
        """list_pods with explicit namespace returns list."""
        result = self.orch.list_pods(namespace="kube-system")
        assert isinstance(result, list)

    def test_get_pod_logs_returns_string(self):
        """get_pod_logs returns a string in simulated mode."""
        result = self.orch.get_pod_logs("pod-name")
        assert isinstance(result, str)

    def test_get_pod_logs_simulated_content(self):
        """Simulated logs contain SIMULATED indicator."""
        result = self.orch.get_pod_logs("pod-name")
        assert "SIMULATED" in result

    def test_get_pod_logs_tail(self):
        """get_pod_logs with tail_lines parameter returns string."""
        result = self.orch.get_pod_logs("pod-name", tail_lines=10)
        assert isinstance(result, str)

    def test_get_pod_logs_with_container(self):
        """get_pod_logs with container parameter returns string."""
        result = self.orch.get_pod_logs("pod-name", container="sidecar")
        assert isinstance(result, str)


# ===========================================================================
# Manifest operations (simulated mode)
# ===========================================================================


@pytest.mark.unit
class TestKubernetesOrchestratorManifests:
    """Tests for manifest application in simulated mode."""

    def setup_method(self):
        self.orch = KubernetesOrchestrator()

    def test_apply_manifest_deployment(self):
        """Applying a Deployment manifest returns a simulated result dict."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "test"},
            "spec": {},
        }
        result = self.orch.apply_manifest(manifest)
        assert isinstance(result, dict)
        assert result["status"] == "simulated"
        assert result["kind"] == "Deployment"

    def test_apply_manifest_service(self):
        """Applying a Service manifest returns a simulated result dict."""
        manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "test-svc"},
            "spec": {},
        }
        result = self.orch.apply_manifest(manifest)
        assert isinstance(result, dict)
        assert result["status"] == "simulated"
        assert result["kind"] == "Service"

    def test_apply_manifest_unknown_kind(self):
        """Applying a manifest with unknown kind returns simulated result."""
        manifest = {
            "kind": "CustomResource",
            "metadata": {"name": "cr"},
        }
        result = self.orch.apply_manifest(manifest)
        assert isinstance(result, dict)
        assert result["status"] == "simulated"

    def test_apply_yaml_file(self, tmp_path):
        """Applying a real YAML file returns a list of results."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "yaml-test"},
            "spec": {},
        }
        yaml_file = tmp_path / "deployment.yaml"
        yaml_file.write_text(yaml.dump(manifest))

        results = self.orch.apply_yaml_file(str(yaml_file))
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["status"] == "simulated"
        assert results[0]["kind"] == "Deployment"

    def test_apply_yaml_file_multi_document(self, tmp_path):
        """Applying a multi-document YAML returns multiple results."""
        doc1 = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "dep1"},
            "spec": {},
        }
        doc2 = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "svc1"},
            "spec": {},
        }
        yaml_file = tmp_path / "multi.yaml"
        yaml_file.write_text(
            yaml.dump(doc1) + "---\n" + yaml.dump(doc2)
        )

        results = self.orch.apply_yaml_file(str(yaml_file))
        assert isinstance(results, list)
        assert len(results) == 2

    def test_apply_yaml_file_nonexistent_raises(self):
        """Applying a nonexistent YAML file raises CodomyrmexError."""
        with pytest.raises(CodomyrmexError, match="YAML file not found"):
            self.orch.apply_yaml_file("/nonexistent/path/deploy.yaml")

    def test_apply_yaml_file_empty_documents_skipped(self, tmp_path):
        """Empty YAML documents (null) in multi-doc files are skipped."""
        yaml_file = tmp_path / "sparse.yaml"
        yaml_file.write_text(
            "---\n"
            + yaml.dump({"kind": "Deployment", "metadata": {"name": "d"}})
            + "---\n"
            + "# empty document\n"
            + "---\n"
        )
        results = self.orch.apply_yaml_file(str(yaml_file))
        # Only non-null documents should produce results
        assert isinstance(results, list)
        assert len(results) >= 1


# ===========================================================================
# orchestrate_kubernetes convenience function
# ===========================================================================


@pytest.mark.unit
class TestOrchestrateKubernetesFunction:
    """Tests for the orchestrate_kubernetes module-level convenience function."""

    def test_orchestrate_returns_dict(self):
        """orchestrate_kubernetes returns a result dict."""
        result = orchestrate_kubernetes({"name": "test", "image": "nginx"})
        assert isinstance(result, dict)

    def test_orchestrate_has_deployment_name(self):
        """Result contains the deployment_name field."""
        result = orchestrate_kubernetes({"name": "my-app", "image": "nginx"})
        assert result["deployment_name"] == "my-app"

    def test_orchestrate_has_status(self):
        """Result contains the status field set to 'created'."""
        result = orchestrate_kubernetes({"name": "app", "image": "nginx"})
        assert result["status"] == "created"

    def test_orchestrate_has_namespace(self):
        """Result contains the namespace field."""
        result = orchestrate_kubernetes({"name": "app", "image": "nginx"})
        assert result["namespace"] == "default"

    def test_orchestrate_custom_namespace(self):
        """Custom namespace is reflected in the result."""
        result = orchestrate_kubernetes(
            {"name": "app", "image": "nginx", "namespace": "staging"}
        )
        assert result["namespace"] == "staging"

    def test_orchestrate_available_field(self):
        """Result contains the available field (False in simulated mode)."""
        result = orchestrate_kubernetes({"name": "app", "image": "nginx"})
        assert "available" in result
        assert result["available"] is False

    def test_orchestrate_message_field(self):
        """Result contains a human-readable message."""
        result = orchestrate_kubernetes({"name": "app", "image": "nginx"})
        assert "message" in result
        assert "app" in result["message"]

    def test_orchestrate_with_defaults(self):
        """Config with no name/image uses defaults."""
        result = orchestrate_kubernetes({})
        assert result["deployment_name"] == "default-deployment"

    def test_orchestrate_with_replicas(self):
        """replicas parameter is accepted without error."""
        result = orchestrate_kubernetes(
            {"name": "scaled", "image": "nginx", "replicas": 3}
        )
        assert result["deployment_name"] == "scaled"

    def test_orchestrate_with_env_vars(self):
        """environment_variables are accepted without error."""
        result = orchestrate_kubernetes(
            {
                "name": "env-app",
                "image": "nginx",
                "environment_variables": {"KEY": "val"},
            }
        )
        assert result["deployment_name"] == "env-app"

    def test_orchestrate_with_service_creation(self):
        """create_service=True triggers service creation without error."""
        result = orchestrate_kubernetes(
            {
                "name": "svc-app",
                "image": "nginx",
                "create_service": True,
                "service_type": "ClusterIP",
            }
        )
        assert result["deployment_name"] == "svc-app"
        assert result["status"] == "created"

    def test_orchestrate_with_kubeconfig_path(self):
        """Explicit kubeconfig_path parameter is accepted."""
        result = orchestrate_kubernetes(
            {"name": "app", "image": "nginx"},
            kubeconfig_path="/nonexistent/config",
        )
        assert result["deployment_name"] == "app"

    def test_orchestrate_with_labels(self):
        """labels parameter is accepted without error."""
        result = orchestrate_kubernetes(
            {
                "name": "labeled",
                "image": "nginx",
                "labels": {"env": "dev", "team": "platform"},
            }
        )
        assert result["deployment_name"] == "labeled"

    def test_orchestrate_with_resources(self):
        """resources parameter is accepted without error."""
        result = orchestrate_kubernetes(
            {
                "name": "resource-app",
                "image": "nginx",
                "resources": {
                    "limits": {"cpu": "500m", "memory": "512Mi"},
                    "requests": {"cpu": "250m", "memory": "256Mi"},
                },
            }
        )
        assert result["deployment_name"] == "resource-app"
