"""Tests for InfrastructureAgent and CloudToolFactory.

Tests cover:
- InfrastructureAgent initialization (~5 tests)
- InfrastructureAgent execution (~10 tests)
- InfrastructureAgent tool registry (~8 tests)
- CloudToolFactory (~7 tests)

Total: ~30 tests across 4 test classes.

Note: These tests may be skipped if `codomyrmex.agents` has unresolved
import dependencies (e.g., google.genai). This is a pre-existing issue
affecting ALL agent tests in this environment.
"""

import json
from unittest.mock import MagicMock

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


# =========================================================================
# Test InfrastructureAgent Initialization
# =========================================================================

class TestInfrastructureAgentInit:
    """Tests for InfrastructureAgent constructor and from_env."""

    def test_init_with_compute_client(self):
        """Compute client sets CLOUD_INFRASTRUCTURE capability."""

        agent = InfrastructureAgent(clients={"compute": MagicMock()})
        caps = agent.get_capabilities()
        assert AgentCapabilities.CLOUD_INFRASTRUCTURE in caps
        assert AgentCapabilities.CLOUD_STORAGE not in caps

    def test_init_with_s3_adds_storage(self):
        """S3 client adds CLOUD_STORAGE capability."""
        from codomyrmex.agents.core.base import AgentCapabilities
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        agent = InfrastructureAgent(clients={"s3": MagicMock()})
        assert AgentCapabilities.CLOUD_STORAGE in agent.get_capabilities()

    def test_init_empty_clients(self):
        """Empty clients dict results in only CLOUD_INFRASTRUCTURE."""
        from codomyrmex.agents.core.base import AgentCapabilities
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        agent = InfrastructureAgent(clients={})
        caps = agent.get_capabilities()
        assert AgentCapabilities.CLOUD_INFRASTRUCTURE in caps
        assert len(caps) == 1

    def test_available_services(self):
        """available_services returns configured service names."""
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        agent = InfrastructureAgent(
            clients={"compute": MagicMock(), "network": MagicMock()}
        )
        services = agent.available_services()
        assert "compute" in services
        assert "network" in services

    def test_name_is_infrastructure_agent(self):
        """Agent name is InfrastructureAgent."""
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        agent = InfrastructureAgent()
        assert agent.name == "InfrastructureAgent"


# =========================================================================
# Test InfrastructureAgent Execution
# =========================================================================

class TestInfrastructureAgentExecute:
    """Tests for InfrastructureAgent._execute_impl."""

    def _make_agent(self, clients=None):
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent
        agent = InfrastructureAgent(clients=clients or {})
        # Disable security pipeline for focused execution tests
        agent._pipeline = None
        return agent

    def test_valid_json_dispatch(self):
        """Valid JSON dispatches to correct client method."""
        from codomyrmex.agents.core.base import AgentRequest

        mock_compute = MagicMock()
        mock_compute.list_instances.return_value = [{"id": "i-1"}]

        agent = self._make_agent(clients={"compute": mock_compute})
        request = AgentRequest(prompt=json.dumps({
            "service": "compute",
            "action": "list_instances",
        }))
        response = agent.execute(request)
        assert response.is_success()
        assert "i-1" in response.content
        mock_compute.list_instances.assert_called_once()

    def test_missing_service_key(self):
        """Missing 'service' key returns error."""
        from codomyrmex.agents.core.base import AgentRequest

        agent = self._make_agent()
        request = AgentRequest(prompt=json.dumps({"action": "list"}))
        response = agent.execute(request)
        assert not response.is_success()
        assert "service" in response.error.lower()

    def test_missing_action_key(self):
        """Missing 'action' key returns error."""
        from codomyrmex.agents.core.base import AgentRequest

        agent = self._make_agent()
        request = AgentRequest(prompt=json.dumps({"service": "compute"}))
        response = agent.execute(request)
        assert not response.is_success()
        assert "action" in response.error.lower()

    def test_unknown_service(self):
        """Unknown service returns error with available list."""
        from codomyrmex.agents.core.base import AgentRequest

        agent = self._make_agent(clients={"compute": MagicMock()})
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
        from codomyrmex.agents.core.base import AgentRequest

        mock_compute = MagicMock(spec=["list_instances"])
        agent = self._make_agent(clients={"compute": mock_compute})
        request = AgentRequest(prompt=json.dumps({
            "service": "compute",
            "action": "nonexistent_method",
        }))
        response = agent.execute(request)
        assert not response.is_success()
        assert "nonexistent_method" in response.error

    def test_invalid_json(self):
        """Invalid JSON returns error."""
        from codomyrmex.agents.core.base import AgentRequest

        agent = self._make_agent()
        request = AgentRequest(prompt="{invalid json}")
        response = agent.execute(request)
        assert not response.is_success()
        assert "json" in response.error.lower()

    def test_non_json_prompt(self):
        """Non-JSON prompt returns error."""
        from codomyrmex.agents.core.base import AgentRequest

        agent = self._make_agent()
        request = AgentRequest(prompt="just a string")
        response = agent.execute(request)
        assert not response.is_success()

    def test_parameter_forwarding(self):
        """Extra JSON keys are forwarded as kwargs to client method."""
        from codomyrmex.agents.core.base import AgentRequest

        mock_compute = MagicMock()
        mock_compute.create_instance.return_value = {"id": "new"}

        agent = self._make_agent(clients={"compute": mock_compute})
        request = AgentRequest(prompt=json.dumps({
            "service": "compute",
            "action": "create_instance",
            "name": "srv-1",
            "flavor": "small",
        }))
        response = agent.execute(request)
        assert response.is_success()
        mock_compute.create_instance.assert_called_once_with(
            name="srv-1", flavor="small"
        )

    def test_security_pipeline_blocks(self):
        """Security pipeline can block execution."""
        from codomyrmex.agents.core.base import AgentRequest
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        mock_pipeline = MagicMock()
        check_result = MagicMock()
        check_result.allowed = False
        check_result.reason = "exploit detected"
        mock_pipeline.pre_check.return_value = check_result

        agent = InfrastructureAgent(
            clients={"compute": MagicMock()},
            security_pipeline=mock_pipeline,
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
        from codomyrmex.agents.core.base import AgentRequest

        mock_compute = MagicMock()
        mock_compute.list_images.return_value = []

        agent = self._make_agent(clients={"compute": mock_compute})
        request = AgentRequest(prompt=json.dumps({
            "service": "compute",
            "action": "list_images",
        }))
        response = agent.execute(request)
        assert response.metadata.get("service") == "compute"
        assert response.metadata.get("action") == "list_images"


# =========================================================================
# Test InfrastructureAgent Tool Registry
# =========================================================================

class TestInfrastructureAgentToolRegistry:
    """Tests for InfrastructureAgent.populate_tool_registry."""

    def test_populate_creates_tools(self):
        """populate_tool_registry creates tool entries for client methods."""
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        mock_compute = MagicMock()
        # Add a public method
        mock_compute.list_instances = MagicMock(return_value=[])

        agent = InfrastructureAgent(clients={"compute": mock_compute})
        agent._pipeline = None
        registry = agent.populate_tool_registry()
        # Should have at least one tool containing "compute"
        compute_tools = [n for n in registry if "compute" in n]
        assert len(compute_tools) > 0

    def test_populate_with_external_registry(self):
        """External registry dict is populated in place."""
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        mock_compute = MagicMock()
        agent = InfrastructureAgent(clients={"compute": mock_compute})
        agent._pipeline = None
        external = {}
        result = agent.populate_tool_registry(registry=external)
        assert result is external
        assert len(external) > 0

    def test_tool_has_name_and_handler(self):
        """Each generated tool has a name and callable handler."""
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        mock_compute = MagicMock()
        mock_compute.list_instances = MagicMock()

        agent = InfrastructureAgent(clients={"compute": mock_compute})
        agent._pipeline = None
        registry = agent.populate_tool_registry()

        for name, tool in registry.items():
            assert tool.name == name
            assert callable(tool.handler)

    def test_tool_handler_delegates_to_client(self):
        """Tool handler calls the underlying client method."""
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        mock_compute = MagicMock()
        mock_compute.list_instances = MagicMock(return_value=["a"])

        agent = InfrastructureAgent(clients={"compute": mock_compute})
        agent._pipeline = None
        registry = agent.populate_tool_registry()

        # Find the list_instances tool
        tool_name = "infomaniak_compute_list_instances"
        if tool_name in registry:
            result = registry[tool_name].handler()
            mock_compute.list_instances.assert_called()

    def test_stream_yields_execute_result(self):
        """stream() yields the execute result content."""
        from codomyrmex.agents.core.base import AgentRequest
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        mock_compute = MagicMock()
        mock_compute.list_instances.return_value = []
        agent = InfrastructureAgent(clients={"compute": mock_compute})
        agent._pipeline = None

        request = AgentRequest(prompt=json.dumps({
            "service": "compute",
            "action": "list_instances",
        }))
        chunks = list(agent.stream(request))
        assert len(chunks) == 1

    def test_test_connection_succeeds(self):
        """test_connection returns True when all clients pass."""
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        mock_client = MagicMock()
        mock_client.validate_connection.return_value = True
        agent = InfrastructureAgent(clients={"compute": mock_client})
        assert agent.test_connection() is True

    def test_test_connection_fails(self):
        """test_connection returns False when a client fails."""
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent

        mock_client = MagicMock()
        mock_client.validate_connection.return_value = False
        agent = InfrastructureAgent(clients={"compute": mock_client})
        assert agent.test_connection() is False

    def test_test_connection_empty_clients(self):
        """test_connection returns False with no clients."""
        from codomyrmex.agents.infrastructure.agent import InfrastructureAgent
        agent = InfrastructureAgent(clients={})
        assert agent.test_connection() is False


# =========================================================================
# Test CloudToolFactory
# =========================================================================

class TestCloudToolFactory:
    """Tests for CloudToolFactory."""

    def test_register_client_generates_tool_names(self):
        """register_client creates correctly named tools."""
        from codomyrmex.agents.infrastructure.tool_factory import CloudToolFactory

        mock_client = MagicMock()
        mock_client.list_instances = MagicMock()
        mock_client.create_instance = MagicMock()

        registry = {}
        names = CloudToolFactory.register_client(mock_client, "compute", registry)
        assert "infomaniak_compute_list_instances" in names
        assert "infomaniak_compute_create_instance" in names

    def test_register_client_skips_private_methods(self):
        """Private methods (starting with _) are not registered."""
        from codomyrmex.agents.infrastructure.tool_factory import CloudToolFactory

        mock_client = MagicMock()
        mock_client._private_method = MagicMock()
        mock_client.public_method = MagicMock()

        registry = {}
        names = CloudToolFactory.register_client(mock_client, "svc", registry)
        private_tools = [n for n in names if "private" in n]
        assert len(private_tools) == 0

    def test_register_all_clients(self):
        """register_all_clients returns dict of service -> tool names."""
        from codomyrmex.agents.infrastructure.tool_factory import CloudToolFactory

        clients = {
            "compute": MagicMock(),
            "network": MagicMock(),
        }
        registry = {}
        result = CloudToolFactory.register_all_clients(registry, clients)
        assert "compute" in result
        assert "network" in result
        assert len(registry) > 0

    def test_security_wrapping(self):
        """Security-wrapped tool raises on blocked check."""
        from codomyrmex.agents.infrastructure.tool_factory import CloudToolFactory

        mock_pipeline = MagicMock()
        check_result = MagicMock()
        check_result.allowed = False
        check_result.reason = "blocked"
        mock_pipeline.pre_check.return_value = check_result

        mock_client = MagicMock()
        mock_client.create_instance = MagicMock()

        registry = {}
        CloudToolFactory.register_client(
            mock_client, "compute", registry, security_pipeline=mock_pipeline
        )
        tool = registry.get("infomaniak_compute_create_instance")
        if tool:
            with pytest.raises(PermissionError, match="blocked"):
                tool.handler()

    def test_tool_schema_extraction(self):
        """Tool parameters schema is extracted from method signature."""
        from codomyrmex.agents.infrastructure.tool_factory import _method_to_args_schema

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
        from codomyrmex.agents.infrastructure.tool_factory import _method_to_args_schema

        class Foo:
            def bar(self, x: str):
                pass

        schema = _method_to_args_schema(Foo().bar)
        assert "self" not in schema.get("properties", {})

    def test_is_public_method(self):
        """_is_public_method correctly identifies public callables."""
        from codomyrmex.agents.infrastructure.tool_factory import _is_public_method

        assert _is_public_method("list_instances", lambda: None) is True
        assert _is_public_method("_private", lambda: None) is False
        assert _is_public_method("NotCallable", "string") is False
