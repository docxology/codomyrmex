from typing import Any, Iterator, Optional
import time

import uuid

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
from codomyrmex.agents.exceptions import AgentError, AgentTimeoutError
from codomyrmex.logging_monitoring import get_logger











































    AgentCapabilities,
    AgentInterface,
    AgentRequest,
    AgentResponse,
)

logger = get_logger(__name__)


class BaseAgent(AgentInterface):
    """Base implementation of AgentInterface with common functionality."""

    def __init__(
        self,
        name: str,
        capabilities: list[AgentCapabilities],
        config: dict[str, Any],
    ):
        """
        Initialize base agent.

        Args:
            name: Agent name
            capabilities: List of agent capabilities
            config: Agent configuration
        """
        self.name = name
        self.capabilities = capabilities
        self.config = config
        self.logger = logger

    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute agent request.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        try:
            self._validate_request(request)
            return self._execute_impl(request)
        except Exception as e:
            self.logger.exception(f"Error executing {self.name} request")
            return AgentResponse(
                request_id=request.id,
                content="",
                error=str(e),
                metadata={"error_type": type(e).__name__},
            )

    def stream(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream agent response.

        Args:
            request: Agent request

        Yields:
            Response chunks
        """
        try:
            self._validate_request(request)
            yield from self._stream_impl(request)
        except Exception as e:
            self.logger.exception(f"Error streaming {self.name} response")
            yield f"Error: {str(e)}"

    def _validate_request(self, request: AgentRequest) -> None:
        """
        Validate agent request.

        Args:
            request: Agent request

        Raises:
            ValueError: If request is invalid
        """
        if not request.prompt:
            raise ValueError("Prompt is required")

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Implementation of execute method.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        raise NotImplementedError

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Implementation of stream method.

        Args:
            request: Agent request

        Yields:
            Response chunks
        """
        raise NotImplementedError

    def get_capabilities(self) -> list[AgentCapabilities]:
        """
        Get agent capabilities.

        Returns:
            List of agent capabilities
        """
        return self.capabilities

    def get_config_value(self, key: str, default: Any = None, config: Optional[dict[str, Any]] = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value
            config: Optional configuration override

        Returns:
            Configuration value
        """
        if config and key in config:
            return config[key]
        if self.config and key in self.config:
            return self.config[key]
        
        # Fallback to global config
        global_config = get_config()
        if hasattr(global_config, key):
            return getattr(global_config, key)
            
        return default
