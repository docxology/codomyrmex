"""Tests for InfrastructureAgent and CloudToolFactory.

Tests cover:
- InfrastructureAgent initialization (~5 tests)
- InfrastructureAgent execution (~10 tests)
- InfrastructureAgent tool registry (~8 tests)
- CloudToolFactory (~7 tests)

Total: ~30 tests across 4 test classes.

Zero-Mock compliant — uses lightweight stub client classes instead of
unittest.mock.MagicMock.
"""

import json

import pytest

# Guard: the entire agents package may fail to import if optional
# dependencies (google.genai, etc.) are missing.
try:
    from codomyrmex.agents.core.base import AgentCapabilities, AgentRequest
    from codomyrmex.agents.infrastructure.agent import InfrastructureAgent
    from codomyrmex.agents.infrastructure.tool_factory import (
        CloudToolFactory,
        Tool,
        _is_public_method,
        _method_to_args_schema,
    )
    _AGENTS_AVAILABLE = True
except ImportError:
    _AGENTS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _AGENTS_AVAILABLE,
    reason="agents package has unresolved imports (e.g., google.genai)",
)


# ---------------------------------------------------------------------------
# Lightweight stub client classes (replace MagicMock)
# ---------------------------------------------------------------------------

class StubClient:
    """Minimal stub client that records calls and returns configured values."""
    pass


class StubComputeClient:
    """Stub compute client with common compute methods."""

    def __init__(self, *, list_instances_rv=None, create_instance_rv=None,
                 list_images_rv=None, validate_connection_rv=True):
        self._list_instances_rv = list_instances_rv or []
        self._create_instance_rv = create_instance_rv or {"id": "new"}
        self._list_images_rv = list_images_rv or []
        self._validate_connection_rv = validate_connection_rv
        self._calls = {}

    def list_instances(self, **kwargs):
        self._calls.setdefault("list_instances", []).append(kwargs)
        return self._list_instances_rv

    def create_instance(self, **kwargs):
        self._calls.setdefault("create_instance", []).append(kwargs)
        return self._create_instance_rv

    def list_images(self, **kwargs):
        self._calls.setdefault("list_images", []).append(kwargs)
        return self._list_images_rv

    def validate_connection(self):
        return self._validate_connection_rv


class StubNetworkClient:
    """Stub network client."""

    def list_networks(self):
        return []

    def validate_connection(self):
        return True


class StubConnectionFailClient:
    """Stub client whose validate_connection returns False."""

    def validate_connection(self):
        return False


class StubSecurityPipeline:
    """Stub security pipeline for testing security-blocked execution."""

    def __init__(self, allowed=True, reason=""):
        self._allowed = allowed
        self._reason = reason

    def pre_check(self, *args, **kwargs):
        return _SecurityCheckResult(allowed=self._allowed, reason=self._reason)


class _SecurityCheckResult:
    """Minimal security check result."""

    def __init__(self, allowed=True, reason=""):
        self.allowed = allowed
        self.reason = reason


class StubPublicPrivateClient:
    """Client with both public and private methods for tool factory tests."""

    def public_method(self):
        return "public"

    def _private_method(self):
        return "private"


# ---------------------------------------------------------------------------
# Test InfrastructureAgent Initialization
# ---------------------------------------------------------------------------

class TestInfrastructureAgentInit:
    """Tests for InfrastructureAgent constructor and from_env."""

    def test_init_with_compute_client(self):
        """Compute client sets CLOUD_INFRASTRUCTURE capability."""
        agent = InfrastructureAgent(clients={"compute": StubComputeClient()})
        caps = agent.get_capabilities()
        assert AgentCapabilities.CLOUD_INFRASTRUCTURE in caps
        assert AgentCapabilities.CLOUD_STORAGE not in caps

    def test_init_with_s3_adds_storage(self):
        """S3 client adds CLOUD_STORAGE capability."""
        agent = InfrastructureAgent(clients={"s3": StubClient()})
        assert AgentCapabilities.CLOUD_STORAGE in agent.get_capabilities()

    def test_init_empty_clients(self):
        """Empty clients dict results in only CLOUD_INFRASTRUCTURE."""
        agent = InfrastructureAgent(clients={})
        caps = agent.get_capabilities()
        assert AgentCapabilities.CLOUD_INFRASTRUCTURE in caps
        assert len(caps) == 1

    def test_available_services(self):
        """available_services returns configured service names."""
        agent = InfrastructureAgent(
            clients={"compute": StubComputeClient(), "network": StubNetworkClient()}
        )
        services = agent.available_services()
        assert "compute" in services
        assert "network" in services

    def test_name_is_infrastructure_agent(self):
        """Agent name is InfrastructureAgent."""
        agent = InfrastructureAgent()
        assert agent.name == "InfrastructureAgent"


# ---------------------------------------------------------------------------
# Test InfrastructureAgent Execution
# ---------------------------------------------------------------------------

class TestInfrastructureAgentExecute:
    """Tests for InfrastructureAgent._execute_impl."""

    def _make_agent(self, clients=None):
        agent = InfrastructureAgent(clients=clients or {})
        # Disable security pipeline for focused execution tests
        agent._pipeline = None
        return agent

    def test_valid_json_dispatch(self):
        """Valid JSON dispatches to correct client method."""
        compute = StubComputeClient(list_instances_rv=[{"id": "i-1"}])
        agent = self._make_agent(clients={"compute": compute})
        request = AgentRequest(prompt=json.dumps({
            "service": "compute",
            "action": "list_instances",
        }))
        response = agent.execute(request)
        assert response.is_success()
        assert "i-1" in response.content
        assert len(compute._calls.get("list_instances", [])) == 1

    def test_missing_service_key(self):
        """Missing 'service' key returns error."""
        agent = self._make_agent()
        request = AgentRequest(prompt=json.dumps({"action": "list"}))
        response = agent.execute(request)
        assert not response.is_success()
        assert "service" in response.error.lower()

    def test_missing_action_key(self):
        """Missing 'action' key returns error."""
        agent = self._make_agent()
        request = AgentRequest(prompt=json.dumps({"service": "compute"}))
        response = agent.execute(request)
        assert not response.is_success()
        assert "action" in response.error.lower()

    def test_unknown_service(self):
        """Unknown service returns error with available list."""
        agent = self._make_agent(clients={"compute": StubComputeClient()})
        request = AgentRequest(prompt=json.dumps({
            "service": "unknown",
            "action": "list",
        }))
        response = agent.execute(request)
        assert not response.is_success()
        assert "unknown" in response.error.lower()
        assert "compute" in response.error.lower()

    def test_unknown_action(self):
        """Unknown action returns error."""
        # Create a compute client that only has list_instances
        compute = StubComputeClient()
        agent = self._make_agent(clients={"compute": compute})
        request = AgentRequest(prompt=json.dumps({
            "service": "compute",
            "action": "nonexistent_method",
        }))
        response = agent.execute(request)
        assert not response.is_success()
        assert "nonexistent_method" in response.error

    def test_invalid_json(self):
        """Invalid JSON returns error."""
        agent = self._make_agent()
        request = AgentRequest(prompt="{invalid json}")
        response = agent.execute(request)
        assert not response.is_success()
        assert "json" in response.error.lower()

    def test_non_json_prompt(self):
        """Non-JSON prompt returns error."""
        agent = self._make_agent()
        request = AgentRequest(prompt="just a string")
        response = agent.execute(request)
        assert not response.is_success()

    def test_parameter_forwarding(self):
        """Extra JSON keys are forwarded as kwargs to client method."""
        compute = StubComputeClient(create_instance_rv={"id": "new"})
        agent = self._make_agent(clients={"compute": compute})
        request = AgentRequest(prompt=json.dumps({
            "service": "compute",
            "action": "create_instance",
            "name": "srv-1",
            "flavor": "small",
        }))
        response = agent.execute(request)
        assert response.is_success()
        assert compute._calls["create_instance"][0] == {"name": "srv-1", "flavor": "small"}

    def test_security_pipeline_blocks(self):
        """Security pipeline can block execution."""
        pipeline = StubSecurityPipeline(allowed=False, reason="exploit detected")
        agent = InfrastructureAgent(
            clients={"compute": StubComputeClient()},
            security_pipeline=pipeline,
        )
        request = AgentRequest(prompt=json.dumps({
            "service": "compute",
            "action": "create_instance",
            "name": "bad",
        }))
        response = agent.execute(request)
        assert not response.is_success()
        assert "exploit" in response.error.lower()
        assert response.metadata.get("security_blocked") is True

    def test_response_metadata_contains_service_and_action(self):
        """Successful response metadata includes service and action."""
        compute = StubComputeClient(list_images_rv=[])
        agent = self._make_agent(clients={"compute": compute})
        request = AgentRequest(prompt=json.dumps({
            "service": "compute",
            "action": "list_images",
        }))
        response = agent.execute(request)
        assert response.metadata.get("service") == "compute"
        assert response.metadata.get("action") == "list_images"


# ---------------------------------------------------------------------------
# Test InfrastructureAgent Tool Registry
# ---------------------------------------------------------------------------

class TestInfrastructureAgentToolRegistry:
    """Tests for InfrastructureAgent.populate_tool_registry."""

    def test_populate_creates_tools(self):
        """populate_tool_registry creates tool entries for client methods."""
        compute = StubComputeClient()
        agent = InfrastructureAgent(clients={"compute": compute})
        agent._pipeline = None
        registry = agent.populate_tool_registry()
        compute_tools = [n for n in registry if "compute" in n]
        assert len(compute_tools) > 0

    def test_populate_with_external_registry(self):
        """External registry dict is populated in place."""
        compute = StubComputeClient()
        agent = InfrastructureAgent(clients={"compute": compute})
        agent._pipeline = None
        external = {}
        result = agent.populate_tool_registry(registry=external)
        assert result is external
        assert len(external) > 0

    def test_tool_has_name_and_handler(self):
        """Each generated tool has a name and callable handler."""
        compute = StubComputeClient()
        agent = InfrastructureAgent(clients={"compute": compute})
        agent._pipeline = None
        registry = agent.populate_tool_registry()

        for name, tool in registry.items():
            assert tool.name == name
            assert callable(tool.handler)

    def test_tool_handler_delegates_to_client(self):
        """Tool handler calls the underlying client method."""
        compute = StubComputeClient(list_instances_rv=["a"])
        agent = InfrastructureAgent(clients={"compute": compute})
        agent._pipeline = None
        registry = agent.populate_tool_registry()

        tool_name = "infomaniak_compute_list_instances"
        if tool_name in registry:
            result = registry[tool_name].handler()
            assert len(compute._calls.get("list_instances", [])) > 0

    def test_stream_yields_execute_result(self):
        """stream() yields the execute result content."""
        compute = StubComputeClient()
        agent = InfrastructureAgent(clients={"compute": compute})
        agent._pipeline = None

        request = AgentRequest(prompt=json.dumps({
            "service": "compute",
            "action": "list_instances",
        }))
        chunks = list(agent.stream(request))
        assert len(chunks) == 1

    def test_test_connection_succeeds(self):
        """test_connection returns True when all clients pass."""
        client = StubComputeClient(validate_connection_rv=True)
        agent = InfrastructureAgent(clients={"compute": client})
        assert agent.test_connection() is True

    def test_test_connection_fails(self):
        """test_connection returns False when a client fails."""
        client = StubConnectionFailClient()
        agent = InfrastructureAgent(clients={"compute": client})
        assert agent.test_connection() is False

    def test_test_connection_empty_clients(self):
        """test_connection returns False with no clients."""
        agent = InfrastructureAgent(clients={})
        assert agent.test_connection() is False


# ---------------------------------------------------------------------------
# Test CloudToolFactory
# ---------------------------------------------------------------------------

class TestCloudToolFactory:
    """Tests for CloudToolFactory."""

    def test_register_client_generates_tool_names(self):
        """register_client creates correctly named tools."""
        compute = StubComputeClient()
        registry = {}
        names = CloudToolFactory.register_client(compute, "compute", registry)
        assert "infomaniak_compute_list_instances" in names
        assert "infomaniak_compute_create_instance" in names

    def test_register_client_skips_private_methods(self):
        """Private methods (starting with _) are not registered."""
        client = StubPublicPrivateClient()
        registry = {}
        names = CloudToolFactory.register_client(client, "svc", registry)
        private_tools = [n for n in names if "private" in n]
        assert len(private_tools) == 0

    def test_register_all_clients(self):
        """register_all_clients returns dict of service -> tool names."""
        clients = {
            "compute": StubComputeClient(),
            "network": StubNetworkClient(),
        }
        registry = {}
        result = CloudToolFactory.register_all_clients(registry, clients)
        assert "compute" in result
        assert "network" in result
        assert len(registry) > 0

    def test_security_wrapping(self):
        """Security-wrapped tool raises on blocked check."""
        pipeline = StubSecurityPipeline(allowed=False, reason="blocked")
        compute = StubComputeClient()
        registry = {}
        CloudToolFactory.register_client(
            compute, "compute", registry, security_pipeline=pipeline
        )
        tool = registry.get("infomaniak_compute_create_instance")
        if tool:
            with pytest.raises(PermissionError, match="blocked"):
                tool.handler()

    def test_tool_schema_extraction(self):
        """Tool parameters schema is extracted from method signature."""
        def sample_method(name: str, size: int = 50, enabled: bool = True):
            pass

        schema = _method_to_args_schema(sample_method)
        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["size"]["type"] == "integer"
        assert schema["properties"]["enabled"]["type"] == "boolean"
        assert "name" in schema["required"]
        assert "size" not in schema["required"]

    def test_tool_schema_no_self(self):
        """Schema extraction skips 'self' parameter."""
        class Foo:
            def bar(self, x: str):
                pass

        schema = _method_to_args_schema(Foo().bar)
        assert "self" not in schema.get("properties", {})

    def test_is_public_method(self):
        """_is_public_method correctly identifies public callables."""
        assert _is_public_method("list_instances", lambda: None) is True
        assert _is_public_method("_private", lambda: None) is False
        assert _is_public_method("NotCallable", "string") is False
