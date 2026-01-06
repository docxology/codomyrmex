"""Base agent implementation."""

import time
from typing import Any, Iterator, Optional

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentInterface,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.exceptions import AgentError, AgentTimeoutError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class BaseAgent(AgentInterface):
    """Base implementation of AgentInterface with common functionality."""

    def __init__(
        self,
        name: str,
        capabilities: list[AgentCapabilities],
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize base agent.

        Args:
            name: Agent name
            capabilities: List of capabilities this agent supports
            config: Agent-specific configuration
        """
        super().__init__(config)
        self.name = name
        self._capabilities = capabilities
        self.logger = get_logger(f"{__name__}.{name}")

    def get_capabilities(self) -> list[AgentCapabilities]:
        """Get list of capabilities supported by this agent."""
        return self._capabilities.copy()

    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute an agent request.

        Args:
            request: Agent request with prompt and context

        Returns:
            Agent response with content and metadata
        """
        start_time = time.time()

        # Validate request
        errors = self.validate_request(request)
        if errors:
            error_msg = "; ".join(errors)
            self.logger.error(f"Request validation failed: {error_msg}")
            return AgentResponse(
                content="",
                error=error_msg,
                execution_time=time.time() - start_time,
            )

        # Check timeout
        timeout = request.timeout or self.config.get("timeout", 30)
        if timeout <= 0:
            raise AgentTimeoutError("Invalid timeout value", timeout=timeout)

        try:
            # Execute the actual request (to be implemented by subclasses)
            response = self._execute_impl(request)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Add execution metadata
            response.execution_time = execution_time
            if response.metadata is None:
                response.metadata = {}
            response.metadata["agent_name"] = self.name
            response.metadata["execution_time"] = execution_time

            self.logger.info(
                f"Request executed successfully in {execution_time:.2f}s"
            )

            return response

        except AgentTimeoutError:
            execution_time = time.time() - start_time
            self.logger.error(f"Request timed out after {execution_time:.2f}s")
            raise
        except AgentError as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Agent error: {e}")
            return AgentResponse(
                content="",
                error=str(e),
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return AgentResponse(
                content="",
                error=f"Unexpected error: {str(e)}",
                execution_time=execution_time,
            )

    def stream(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream response from agent.

        Args:
            request: Agent request with prompt and context

        Yields:
            Chunks of response content
        """
        # Validate request
        errors = self.validate_request(request)
        if errors:
            error_msg = "; ".join(errors)
            self.logger.error(f"Request validation failed: {error_msg}")
            yield f"Error: {error_msg}"
            return

        # Check if streaming is supported
        if not self.supports_capability(AgentCapabilities.STREAMING):
            self.logger.warning("Streaming not supported, falling back to execute")
            response = self.execute(request)
            if response.is_success():
                yield response.content
            else:
                yield f"Error: {response.error}"
            return

        try:
            # Stream the actual response (to be implemented by subclasses)
            yield from self._stream_impl(request)
        except AgentError as e:
            self.logger.error(f"Agent error during streaming: {e}")
            yield f"Error: {str(e)}"
        except Exception as e:
            self.logger.error(f"Unexpected error during streaming: {e}", exc_info=True)
            yield f"Error: Unexpected error: {str(e)}"

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
        raise NotImplementedError(
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
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _stream_impl for streaming support"
        )

