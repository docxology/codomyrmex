"""Base class for API-based agents with common API patterns."""

from collections.abc import Callable, Iterator
from typing import Any

from codomyrmex.agents.core import AgentRequest, AgentResponse, BaseAgent
from codomyrmex.agents.core.config import AgentConfig, get_config
from codomyrmex.agents.core.exceptions import AgentConfigurationError, AgentError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class APIAgentBase(BaseAgent):
    """Base class for API-based agents with common API patterns."""

    def __init__(
        self,
        name: str,
        capabilities: list,
        api_key_config_key: str,
        model_config_key: str,
        timeout_config_key: str,
        max_tokens_config_key: str,
        temperature_config_key: str,
        client_class: type,
        client_init_func: Callable[[str], Any],
        error_class: type[AgentError],
        config: dict[str, Any] | None = None,
        agent_config: AgentConfig | None = None,
    ):
        """
        Initialize API agent base.

        Args:
            name: Agent name
            capabilities: List of capabilities this agent supports
            api_key_config_key: Config key for API key (e.g., "claude_api_key")
            model_config_key: Config key for model (e.g., "claude_model")
            timeout_config_key: Config key for timeout (e.g., "claude_timeout")
            max_tokens_config_key: Config key for max tokens
            temperature_config_key: Config key for temperature
            client_class: API client class (for import checking)
            client_init_func: Function to initialize client (e.g., lambda k: Anthropic(api_key=k))
            error_class: Agent-specific error class
            config: Optional configuration override
            agent_config: Optional AgentConfig instance (uses get_config() if None)
        """
        super().__init__(name=name, capabilities=capabilities, config=config or {})

        # Store config keys for later use
        self._api_key_config_key = api_key_config_key
        self._model_config_key = model_config_key
        self._timeout_config_key = timeout_config_key
        self._max_tokens_config_key = max_tokens_config_key
        self._temperature_config_key = temperature_config_key
        self._error_class = error_class

        # Get agent config
        if agent_config is None:
            agent_config = get_config()

        if client_class is None:
            raise error_class(
                f"{name} client library not installed. "
                f"Install required package to use this agent."
            )

        # Extract configuration values using standardized method
        api_key = self._extract_config_value(
            api_key_config_key, config=config, agent_config=agent_config
        )
        if not api_key:
            raise AgentConfigurationError(
                f"{name} API key not configured",
                config_key=api_key_config_key,
            )

        self.model = self._extract_config_value(
            model_config_key, config=config, agent_config=agent_config
        )
        self.timeout = self._extract_config_value(
            timeout_config_key, config=config, agent_config=agent_config
        )
        self.max_tokens = self._extract_config_value(
            max_tokens_config_key, config=config, agent_config=agent_config
        )
        self.temperature = self._extract_config_value(
            temperature_config_key, config=config, agent_config=agent_config
        )

        try:
            self.client = client_init_func(api_key)
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            raise error_class(f"Failed to initialize {name} client: {e!s}") from e

    def _extract_config_value(
        self,
        key: str,
        default: Any = None,
        config: dict[str, Any] | None = None,
        agent_config: AgentConfig | None = None,
    ) -> Any:
        """
        Extract configuration value with fallback chain.

        Checks in order: provided config dict → instance config → AgentConfig → default.

        Args:
            key: Configuration key
            default: Default value if not found
            config: Optional config dict to check first
            agent_config: Optional AgentConfig instance

        Returns:
            Configuration value or default
        """
        # Check provided config dict first
        if config and key in config:
            return config[key]

        # Check instance config
        if key in self.config:
            return self.config[key]

        # Check AgentConfig
        if agent_config and hasattr(agent_config, key):
            value = getattr(agent_config, key)
            if value is not None:
                return value

        return default

    def setup(self) -> None:
        """
        Setup Agent configuration.

        Prompts user for API key if not configured.
        """
        if not self.config.get(self._api_key_config_key):
            import getpass

            self.logger.info("Configuring %s — API key not found in config", self.name)
            api_key = getpass.getpass(
                f"Enter {self._api_key_config_key} (or env var name): "
            )
            if api_key:
                # In a real app we might save this to a config file
                # For now we just check if it looks like an ENV var or a key
                if api_key.isupper() and "_" in api_key:
                    self.logger.info("User provided env var name: %s", api_key)
                else:
                    self.logger.info("User provided raw API key")
            else:
                self.logger.warning("No API key provided during setup")

    def test_connection(self) -> bool:
        """
        Test API connection.

        Checks if API key is present and (optionally) makes a dummy call.
        """
        api_key = self.api_key
        if not api_key:
            self.logger.warning(
                "Connection test failed for %s: No API key found", self.name
            )
            return False

        # We could try a simple generation here if we want to be thorough
        # For now, presence of key is a basic check
        self.logger.info("Connection test passed for %s (Key present)", self.name)
        return True

    def _handle_api_error(
        self,
        error: Exception,
        execution_time: float,
        api_error_class: type | Any | None = None,
    ) -> None:
        """
        Handle API errors with standardized error conversion.

        Args:
            error: The API error exception
            execution_time: Execution time before error
            api_error_class: Optional API error class to check for (e.g., anthropic.APIError)

        Raises:
            Agent-specific error class
        """
        status_code = getattr(error, "status_code", None)
        api_error_str = str(error)

        # Handle SDK-specific status codes/error details if available
        if not status_code:
            # Check for common SDK error attributes
            for attr in ["status", "code", "http_status"]:
                val = getattr(error, attr, None)
                if isinstance(val, int):
                    status_code = val
                    break

        self.logger.error(
            "%s API error", self.name,
            extra={
                "agent": self.name,
                "model": getattr(self, "model", None),
                "error": api_error_str,
                "status_code": status_code,
                "execution_time": execution_time,
            },
        )

        # Re-raise as agent-specific error if it's a known API error class
        if api_error_class and isinstance(error, api_error_class):
            raise self._error_class(
                f"{self.name} API error: {api_error_str}",
                api_error=api_error_str,
                status_code=status_code,
            ) from error

        # Fallback for SDKs that might not use the provided api_error_class consistently
        # but are clearly API-related errors.
        if "api" in error.__class__.__name__.lower() or "error" in error.__class__.__name__.lower():
            raise self._error_class(
                f"{self.name} API error: {api_error_str}",
                api_error=api_error_str,
                status_code=status_code,
            ) from error

        # Generic fallback
        raise self._error_class(
            f"Unexpected error in {self.name}: {api_error_str}",
            api_error=api_error_str,
        ) from error

    def _extract_tokens_from_response(
        self, response: Any, provider: str
    ) -> tuple[int, int]:
        """
        Extract token counts from API response.

        Args:
            response: API response object
            provider: Provider name ("anthropic", "openai", etc.)

        Returns:
            Tuple of (input_tokens, output_tokens)
        """
        if provider == "anthropic":
            # Claude API structure
            if hasattr(response, "usage"):
                return (
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                )
        elif provider == "openai":
            # OpenAI API structure
            if hasattr(response, "usage"):
                return (
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens,
                )

        # Default: return zeros if structure unknown
        return (0, 0)

    def _build_agent_response(
        self,
        content: str,
        metadata: dict[str, Any],
        tokens_used: int | None = None,
        execution_time: float | None = None,
    ) -> AgentResponse:
        """
        Build standardized AgentResponse from API response data.

        Args:
            content: Response content
            metadata: Response metadata
            tokens_used: Total tokens used
            execution_time: Execution time

        Returns:
            AgentResponse
        """
        response_metadata = {
            "model": getattr(self, "model", None),
            **metadata,
        }

        return AgentResponse(
            content=content,
            metadata=response_metadata,
            tokens_used=tokens_used,
            execution_time=execution_time,
        )

    def _build_messages(self, request: AgentRequest) -> list[dict[str, str]]:
        """Build chat messages from agent request."""
        messages = []

        if request.context and request.context.get("system"):
            messages.append({"role": "system", "content": request.context["system"]})

        if request.context and request.context.get("history"):
            messages.extend(request.context["history"])

        messages.append({"role": "user", "content": request.prompt})
        return messages

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Implementation-specific execution logic.

        This method should be overridden by subclasses.

        Args:
            request: Agent request

        Returns:
            Agent response

        Raises:
            NotImplementedError: If not overridden by subclass
        """
        raise NotImplementedError(  # ABC: intentional
            f"{self.__class__.__name__} must implement _execute_impl"
        )

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Implementation-specific streaming logic.

        This method should be overridden by subclasses that support streaming.

        Args:
            request: Agent request

        Yields:
            Chunks of response content

        Raises:
            NotImplementedError: If not overridden by subclass
        """
        raise NotImplementedError(  # ABC: intentional
            f"{self.__class__.__name__} must implement _stream_impl for streaming support"
        )
