from typing import Any, Iterator, Optional
import time

import uuid

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
from codomyrmex.agents.exceptions import AgentError, AgentTimeoutError
from codomyrmex.logging_monitoring import get_logger






"""Base agent implementation."""


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
        self._request_count = 0
        self._total_execution_time = 0.0

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
        request_id = str(uuid.uuid4())[:8]
        self._request_count += 1

        # Log request with structured context
        self.logger.debug(
            f"Executing request {request_id}",
            extra={
                "request_id": request_id,
                "agent": self.name,
                "prompt_length": len(request.prompt),
                "has_context": bool(request.context),
                "capabilities": [c.value for c in request.capabilities],
            },
        )

        # Validate request
        errors = self.validate_request(request)
        if errors:
            error_msg = "; ".join(errors)
            self.logger.warning(
                f"Request {request_id} validation failed: {error_msg}",
                extra={"request_id": request_id, "agent": self.name, "errors": errors},
            )
            return AgentResponse(
                content="",
                error=error_msg,
                execution_time=time.time() - start_time,
                metadata={"request_id": request_id, "agent": self.name},
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
            self._total_execution_time += execution_time

            # Add execution metadata
            response.execution_time = execution_time
            if response.metadata is None:
                response.metadata = {}
            response.metadata["agent_name"] = self.name
            response.metadata["execution_time"] = execution_time
            response.metadata["request_id"] = request_id

            # Log success with performance metrics
            self.logger.info(
                f"Request {request_id} executed successfully",
                extra={
                    "request_id": request_id,
                    "agent": self.name,
                    "execution_time": execution_time,
                    "content_length": len(response.content),
                    "tokens_used": response.tokens_used,
                    "success": True,
                },
            )

            return response

        except AgentTimeoutError:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Request {request_id} timed out after {execution_time:.2f}s",
                extra={
                    "request_id": request_id,
                    "agent": self.name,
                    "timeout": timeout,
                    "execution_time": execution_time,
                },
            )
            raise
        except AgentError as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Request {request_id} agent error: {e}",
                extra={
                    "request_id": request_id,
                    "agent": self.name,
                    "error": str(e),
                    "execution_time": execution_time,
                },
            )
            return AgentResponse(
                content="",
                error=str(e),
                execution_time=execution_time,
                metadata={"request_id": request_id, "agent": self.name},
            )
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Request {request_id} unexpected error: {e}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "agent": self.name,
                    "error": str(e),
                    "execution_time": execution_time,
                },
            )
            return AgentResponse(
                content="",
                error=f"Unexpected error: {str(e)}",
                execution_time=execution_time,
                metadata={"request_id": request_id, "agent": self.name},
            )

    def stream(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream response from agent.

        Args:
            request: Agent request with prompt and context

        Yields:
            Chunks of response content
        """
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        chunk_count = 0

        self.logger.debug(
            f"Starting stream request {request_id}",
            extra={
                "request_id": request_id,
                "agent": self.name,
                "prompt_length": len(request.prompt),
            },
        )

        # Validate request
        errors = self.validate_request(request)
        if errors:
            error_msg = "; ".join(errors)
            self.logger.warning(
                f"Stream request {request_id} validation failed: {error_msg}",
                extra={"request_id": request_id, "agent": self.name, "errors": errors},
            )
            yield f"Error: {error_msg}"
            return

        # Check if streaming is supported
        if not self.supports_capability(AgentCapabilities.STREAMING):
            self.logger.warning(
                f"Streaming not supported for request {request_id}, falling back to execute",
                extra={"request_id": request_id, "agent": self.name},
            )
            response = self.execute(request)
            if response.is_success():
                yield response.content
            else:
                yield f"Error: {response.error}"
            return

        try:
            # Stream the actual response (to be implemented by subclasses)
            for chunk in self._stream_impl(request):
                chunk_count += 1
                yield chunk

            execution_time = time.time() - start_time
            self.logger.info(
                f"Stream request {request_id} completed",
                extra={
                    "request_id": request_id,
                    "agent": self.name,
                    "execution_time": execution_time,
                    "chunk_count": chunk_count,
                },
            )
        except AgentError as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Stream request {request_id} agent error: {e}",
                extra={
                    "request_id": request_id,
                    "agent": self.name,
                    "error": str(e),
                    "execution_time": execution_time,
                },
            )
            yield f"Error: {str(e)}"
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Stream request {request_id} unexpected error: {e}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "agent": self.name,
                    "error": str(e),
                    "execution_time": execution_time,
                },
            )
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

    def get_config_value(
        self, key: str, default: Any = None, config: Optional[dict[str, Any]] = None
    ) -> Any:
        """
        Get configuration value with fallback chain.

        Checks in order: provided config dict → instance config → AgentConfig global → default value.

        Args:
            key: Configuration key
            default: Default value if not found
            config: Optional config dict to check first

        Returns:
            Configuration value or default
        """

        # Check provided config dict first
        if config and key in config:
            return config[key]
        
        # Check instance config
        if key in self.config:
            return self.config[key]
        
        # Check AgentConfig global
        try:
            agent_config = get_config()
            if hasattr(agent_config, key):
                return getattr(agent_config, key)
        except Exception:
            # If AgentConfig access fails, continue to default
            pass
        
        return default

    def get_metrics(self) -> dict[str, Any]:
        """
        Get agent performance metrics.

        Returns:
            Dictionary with metrics (request_count, total_execution_time, avg_execution_time)
        """
        avg_time = (
            self._total_execution_time / self._request_count
            if self._request_count > 0
            else 0.0
        )
        return {
            "request_count": self._request_count,
            "total_execution_time": self._total_execution_time,
            "avg_execution_time": avg_time,
            "agent_name": self.name,
        }

    def reset_metrics(self) -> None:
        """Reset performance metrics."""
        self._request_count = 0
        self._total_execution_time = 0.0
        self.logger.debug(f"Metrics reset for agent {self.name}")

