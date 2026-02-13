"""Tests for APIAgentBase class.

Zero-Mock compliant — uses simple stub classes instead of unittest.mock.
"""

import pytest

try:
    from codomyrmex.agents.core import AgentCapabilities, AgentRequest, AgentResponse
    from codomyrmex.agents.core.config import (
        AgentConfig,
    )
    from codomyrmex.agents.core.exceptions import AgentConfigurationError, AgentError
    from codomyrmex.agents.generic import APIAgentBase
    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# Lightweight stubs replacing unittest.mock.Mock
# ---------------------------------------------------------------------------

class StubClient:
    """A simple stub API client (replaces Mock)."""
    pass


def _stub_client_init(api_key):
    """Factory that creates a StubClient, replaces lambda k: Mock()."""
    return StubClient()


class _SimpleNamespace:
    """Minimal attribute container (replaces Mock with attribute assignment)."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


# ---------------------------------------------------------------------------
# Concrete test subclass of APIAgentBase
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAPIAgentBase(APIAgentBase):
    """Test implementation of APIAgentBase."""

    def __init__(
        self,
        config=None,
        agent_config=None,
        client_class="SENTINEL",
        client_init_func=None,
        error_class=None,
    ):
        """Initialize test agent."""
        # Use sentinel to allow passing None
        if client_class == "SENTINEL":
            client_class = StubClient
        if client_init_func is None:
            client_init_func = _stub_client_init
        if error_class is None:
            error_class = AgentError

        super().__init__(
            name="test_agent",
            capabilities=[AgentCapabilities.CODE_GENERATION],
            api_key_config_key="test_api_key",
            model_config_key="test_model",
            timeout_config_key="test_timeout",
            max_tokens_config_key="test_max_tokens",
            temperature_config_key="test_temperature",
            client_class=client_class,
            client_init_func=client_init_func,
            error_class=error_class,
            config=config,
            agent_config=agent_config,
        )

    def _execute_impl(self, request):
        """Test implementation."""
        return AgentResponse(content="test response")

    def _stream_impl(self, request):
        """Test streaming implementation."""
        yield "test"
        yield " response"


@pytest.mark.unit
class TestAPIAgentBaseInitialization:
    """Test APIAgentBase initialization."""

    def test_init_with_config_dict(self):
        """Test initialization with config dict."""
        config = {
            "test_api_key": "key123",
            "test_model": "model-v1",
            "test_timeout": 30,
            "test_max_tokens": 2000,
            "test_temperature": 0.5,
        }
        agent = TestAPIAgentBase(config=config)
        assert agent.model == "model-v1"
        assert agent.timeout == 30
        assert agent.max_tokens == 2000
        assert agent.temperature == 0.5

    def test_init_with_agent_config(self):
        """Test initialization with AgentConfig."""
        agent_config = AgentConfig()
        agent_config.test_api_key = "key456"
        agent_config.test_model = "model-v2"
        agent_config.test_timeout = 60
        agent_config.test_max_tokens = 4000
        agent_config.test_temperature = 0.7

        agent = TestAPIAgentBase(agent_config=agent_config)
        assert agent.model == "model-v2"
        assert agent.timeout == 60
        assert agent.max_tokens == 4000
        assert agent.temperature == 0.7

    def test_init_missing_api_key(self):
        """Test initialization fails without API key."""
        with pytest.raises(AgentConfigurationError) as exc_info:
            TestAPIAgentBase(config={})
        assert "API key not configured" in str(exc_info.value)

    def test_init_missing_client_library(self):
        """Test initialization fails when client library is None."""
        with pytest.raises(AgentError) as exc_info:
            TestAPIAgentBase(client_class=None)
        assert "client library not installed" in str(exc_info.value)

    def test_init_client_initialization_error(self):
        """Test initialization handles client initialization errors."""
        def failing_init(api_key):
            raise ValueError("Client init failed")

        with pytest.raises(AgentError) as exc_info:
            TestAPIAgentBase(
                config={"test_api_key": "key"},
                client_init_func=failing_init,
            )
        assert "Failed to initialize" in str(exc_info.value)


@pytest.mark.unit
class TestAPIAgentBaseConfigExtraction:
    """Test configuration extraction methods."""

    def test_extract_config_value_from_dict(self):
        """Test extracting config value from provided dict."""
        config = {"test_key": "value_from_dict"}
        agent = TestAPIAgentBase(config={"test_api_key": "key", **config})
        value = agent._extract_config_value("test_key", config=config)
        assert value == "value_from_dict"

    def test_extract_config_value_from_instance_config(self):
        """Test extracting config value from instance config."""
        agent = TestAPIAgentBase(config={"test_api_key": "key", "test_key": "value_from_instance"})
        value = agent._extract_config_value("test_key")
        assert value == "value_from_instance"

    def test_extract_config_value_from_agent_config(self):
        """Test extracting config value from AgentConfig."""
        agent_config = AgentConfig()
        agent_config.test_key = "value_from_agent_config"
        agent = TestAPIAgentBase(
            config={"test_api_key": "key"},
            agent_config=agent_config,
        )
        value = agent._extract_config_value("test_key", agent_config=agent_config)
        assert value == "value_from_agent_config"

    def test_extract_config_value_default(self):
        """Test extracting config value falls back to default."""
        agent = TestAPIAgentBase(config={"test_api_key": "key"})
        value = agent._extract_config_value("test_key", default="default_value")
        assert value == "default_value"


@pytest.mark.unit
class TestAPIAgentBaseErrorHandling:
    """Test error handling methods."""

    def test_handle_api_error_with_api_error_class(self):
        """Test handling API errors with specific error class."""
        agent = TestAPIAgentBase(config={"test_api_key": "key"})
        api_error = _SimpleNamespace(status_code=429)

        with pytest.raises(AgentError) as exc_info:
            agent._handle_api_error(api_error, 1.0, type(api_error))
        assert "API error" in str(exc_info.value)

    def test_handle_api_error_generic(self):
        """Test handling generic errors."""
        agent = TestAPIAgentBase(config={"test_api_key": "key"})
        generic_error = ValueError("Generic error")

        with pytest.raises(AgentError) as exc_info:
            agent._handle_api_error(generic_error, 1.0)
        assert "Unexpected error" in str(exc_info.value)


@pytest.mark.unit
class TestAPIAgentBaseTokenExtraction:
    """Test token extraction methods."""

    def test_extract_tokens_anthropic(self):
        """Test extracting tokens from Anthropic response."""
        agent = TestAPIAgentBase(config={"test_api_key": "key"})
        response = _SimpleNamespace(
            usage=_SimpleNamespace(input_tokens=10, output_tokens=20)
        )

        input_tokens, output_tokens = agent._extract_tokens_from_response(response, "anthropic")
        assert input_tokens == 10
        assert output_tokens == 20

    def test_extract_tokens_openai(self):
        """Test extracting tokens from OpenAI response."""
        agent = TestAPIAgentBase(config={"test_api_key": "key"})
        response = _SimpleNamespace(
            usage=_SimpleNamespace(prompt_tokens=15, completion_tokens=25)
        )

        input_tokens, output_tokens = agent._extract_tokens_from_response(response, "openai")
        assert input_tokens == 15
        assert output_tokens == 25

    def test_extract_tokens_unknown_provider(self):
        """Test extracting tokens from unknown provider returns zeros."""
        agent = TestAPIAgentBase(config={"test_api_key": "key"})
        response = _SimpleNamespace()

        input_tokens, output_tokens = agent._extract_tokens_from_response(response, "unknown")
        assert input_tokens == 0
        assert output_tokens == 0


@pytest.mark.unit
class TestAPIAgentBaseResponseBuilding:
    """Test response building methods."""

    def test_build_agent_response(self):
        """Test building agent response."""
        agent = TestAPIAgentBase(config={"test_api_key": "key"})
        response = agent._build_agent_response(
            content="test content",
            metadata={"key": "value"},
            tokens_used=100,
            execution_time=1.5,
        )

        assert response.content == "test content"
        assert response.metadata["model"] == agent.model
        assert response.metadata["key"] == "value"
        assert response.tokens_used == 100
        assert response.execution_time == 1.5


@pytest.mark.unit
class TestAPIAgentBaseExecution:
    """Test execution methods."""

    def test_execute_impl_not_implemented(self):
        """Test that _execute_impl raises NotImplementedError if not overridden."""
        class IncompleteAgent(APIAgentBase):
            def __init__(self):
                super().__init__(
                    name="incomplete",
                    capabilities=[],
                    api_key_config_key="test_api_key",
                    model_config_key="test_model",
                    timeout_config_key="test_timeout",
                    max_tokens_config_key="test_max_tokens",
                    temperature_config_key="test_temperature",
                    client_class=StubClient,
                    client_init_func=_stub_client_init,
                    error_class=AgentError,
                    config={"test_api_key": "key"},
                )

        agent = IncompleteAgent()
        request = AgentRequest(prompt="test")

        with pytest.raises(NotImplementedError):
            agent._execute_impl(request)

    def test_stream_impl_not_implemented(self):
        """Test that _stream_impl raises NotImplementedError if not overridden."""
        class IncompleteAgent(APIAgentBase):
            def __init__(self):
                super().__init__(
                    name="incomplete",
                    capabilities=[],
                    api_key_config_key="test_api_key",
                    model_config_key="test_model",
                    timeout_config_key="test_timeout",
                    max_tokens_config_key="test_max_tokens",
                    temperature_config_key="test_temperature",
                    client_class=StubClient,
                    client_init_func=_stub_client_init,
                    error_class=AgentError,
                    config={"test_api_key": "key"},
                )
            def _execute_impl(self, request):
                return AgentResponse(content="test")

        agent = IncompleteAgent()
        request = AgentRequest(prompt="test")

        with pytest.raises(NotImplementedError):
            list(agent._stream_impl(request))
