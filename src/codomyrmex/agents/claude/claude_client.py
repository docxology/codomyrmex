from typing import Any, Iterator, Optional
import time

import anthropic

from codomyrmex.agents.config import get_config
from codomyrmex.agents.core import (
from codomyrmex.agents.exceptions import ClaudeError
from codomyrmex.agents.generic import APIAgentBase




























"""Claude API client."""


try:
except ImportError:
    anthropic = None

    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)


class ClaudeClient(APIAgentBase):
    """Client for interacting with Claude API."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize Claude client.

        Args:
            config: Optional configuration override
        """
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
            api_key_config_key="claude_api_key",
            model_config_key="claude_model",
            timeout_config_key="claude_timeout",
            max_tokens_config_key="claude_max_tokens",
            temperature_config_key="claude_temperature",
            client_class=anthropic,
            client_init_func=lambda api_key: anthropic.Anthropic(api_key=api_key),
            error_class=ClaudeError,
            config=config,
        )

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

            self.logger.debug(
                "Executing Claude API request",
                extra={
                    "agent": "claude",
                    "model": self.model,
                    "message_count": len(messages),
                    "prompt_length": len(request.prompt),
                },
            )

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

            # Extract tokens using base class helper
            input_tokens, output_tokens = self._extract_tokens_from_response(
                response, "anthropic"
            )
            tokens_used = input_tokens + output_tokens

            self.logger.info(
                "Claude API request completed",
                extra={
                    "agent": "claude",
                    "model": self.model,
                    "execution_time": execution_time,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": tokens_used,
                    "content_length": len(content),
                    "stop_reason": response.stop_reason,
                },
            )

            return self._build_agent_response(
                content=content,
                metadata={
                    "usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                    },
                    "stop_reason": response.stop_reason,
                },
                tokens_used=tokens_used,
                execution_time=execution_time,
            )

        except anthropic.APIError as e:
            execution_time = time.time() - start_time
            self._handle_api_error(e, execution_time, anthropic.APIError)
        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_api_error(e, execution_time)

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

            self.logger.debug(
                "Starting Claude API stream",
                extra={
                    "agent": "claude",
                    "model": self.model,
                    "message_count": len(messages),
                },
            )

            chunk_count = 0
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=messages,
                timeout=self.timeout,
            ) as stream:
                for text in stream.text_stream:
                    chunk_count += 1
                    yield text

            self.logger.debug(
                "Claude API stream completed",
                extra={
                    "agent": "claude",
                    "model": self.model,
                    "chunk_count": chunk_count,
                },
            )

        except anthropic.APIError as e:
            self.logger.error(
                "Claude API streaming error",
                exc_info=True,
                extra={
                    "agent": "claude",
                    "model": self.model,
                    "error": str(e),
                },
            )
            yield f"Error: Claude API error: {str(e)}"
        except Exception as e:
            self.logger.error(
                "Unexpected error in Claude API stream",
                exc_info=True,
                extra={
                    "agent": "claude",
                    "model": self.model,
                    "error": str(e),
                },
            )
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

