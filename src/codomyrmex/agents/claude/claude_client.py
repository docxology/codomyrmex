"""Claude API client."""

import time
from typing import Any, Iterator, Optional

try:
    import anthropic
except ImportError:
    anthropic = None

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.exceptions import ClaudeError
from codomyrmex.agents.generic import BaseAgent
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class ClaudeClient(BaseAgent):
    """Client for interacting with Claude API."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize Claude client.

        Args:
            config: Optional configuration override
        """
        if anthropic is None:
            raise ClaudeError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        agent_config = get_config()
        super().__init__(
            name="claude",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
            ],
            config=config or {},
        )

        api_key = (
            config.get("claude_api_key")
            if config
            else agent_config.claude_api_key
        )
        if not api_key:
            raise ClaudeError("Claude API key not configured")

        self.model = (
            config.get("claude_model")
            if config
            else agent_config.claude_model
        )
        self.timeout = (
            config.get("claude_timeout")
            if config
            else agent_config.claude_timeout
        )
        self.max_tokens = (
            config.get("claude_max_tokens")
            if config
            else agent_config.claude_max_tokens
        )
        self.temperature = (
            config.get("claude_temperature")
            if config
            else agent_config.claude_temperature
        )

        self.client = anthropic.Anthropic(api_key=api_key)

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Execute Claude API request.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        start_time = time.time()

        try:
            # Convert request to Claude messages
            messages = self._build_messages(request)

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=messages,
                timeout=self.timeout,
            )

            execution_time = time.time() - start_time

            # Extract content
            content = ""
            if response.content:
                for block in response.content:
                    if hasattr(block, "text"):
                        content += block.text

            return AgentResponse(
                content=content,
                metadata={
                    "model": self.model,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                    },
                    "stop_reason": response.stop_reason,
                },
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                execution_time=execution_time,
            )

        except anthropic.APIError as e:
            execution_time = time.time() - start_time
            raise ClaudeError(
                f"Claude API error: {str(e)}",
                api_error=str(e),
                status_code=getattr(e, "status_code", None),
            ) from e
        except Exception as e:
            execution_time = time.time() - start_time
            raise ClaudeError(
                f"Unexpected error: {str(e)}",
                api_error=str(e),
            ) from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """
        Stream Claude API response.

        Args:
            request: Agent request

        Yields:
            Chunks of response content
        """
        try:
            messages = self._build_messages(request)

            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=messages,
                timeout=self.timeout,
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except anthropic.APIError as e:
            yield f"Error: Claude API error: {str(e)}"
        except Exception as e:
            yield f"Error: {str(e)}"

    def _build_messages(self, request: AgentRequest) -> list[dict[str, str]]:
        """
        Build Claude messages from request.

        Args:
            request: Agent request

        Returns:
            List of message dictionaries
        """
        messages = []

        # Add context as system message if provided
        if request.context:
            system_message = "\n".join(
                f"{k}: {v}" for k, v in request.context.items()
            )
            messages.append({"role": "user", "content": system_message})

        # Add main prompt
        messages.append({"role": "user", "content": request.prompt})

        return messages

