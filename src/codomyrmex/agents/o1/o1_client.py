"""OpenAI o1/o3 reasoning model client for Codomyrmex agents."""

import time
from typing import Any
from collections.abc import Iterator

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import AgentError
from codomyrmex.agents.generic.api_agent_base import APIAgentBase

try:
    import openai
except ImportError:
    openai = None


class O1Client(APIAgentBase):
    """Client for OpenAI o1/o3 reasoning models.

    Optimized for multi-step reasoning tasks that benefit from
    extended thinking capabilities.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize O1 client.

        Args:
            config: Optional configuration override
        """
        super().__init__(
            name="o1",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.MULTI_TURN,
                AgentCapabilities.EXTENDED_THINKING,
            ],
            api_key_config_key="o1_api_key",
            model_config_key="o1_model",
            timeout_config_key="o1_timeout",
            max_tokens_config_key="o1_max_tokens",
            temperature_config_key="o1_temperature",
            client_class=openai,
            client_init_func=lambda api_key: openai.OpenAI(api_key=api_key),
            error_class=AgentError,
            config=config,
        )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute O1 API request."""
        start_time = time.time()

        try:
            messages = self._build_messages(request)

            # o1 models use chat.completions with specific parameters
            create_kwargs: dict[str, Any] = {
                "model": self.model or "o1-preview",
                "messages": messages,
                "timeout": self.timeout,
            }
            # o1 models handle max_tokens differently
            if self.max_tokens:
                create_kwargs["max_completion_tokens"] = self.max_tokens

            response = self.client.chat.completions.create(**create_kwargs)

            execution_time = time.time() - start_time
            content = response.choices[0].message.content if response.choices else ""

            input_tokens, output_tokens = self._extract_tokens_from_response(
                response, "openai"
            )
            tokens_used = input_tokens + output_tokens

            return self._build_agent_response(
                content=content,
                metadata={
                    "usage": {
                        "prompt_tokens": input_tokens,
                        "completion_tokens": output_tokens,
                    },
                    "finish_reason": (
                        response.choices[0].finish_reason if response.choices else None
                    ),
                },
                tokens_used=tokens_used,
                execution_time=execution_time,
            )

        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            execution_time = time.time() - start_time
            self._handle_api_error(e, execution_time)

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream O1 API response.

        Note: o1 models may not support streaming in all configurations.
        """
        try:
            messages = self._build_messages(request)

            create_kwargs: dict[str, Any] = {
                "model": self.model or "o1-preview",
                "messages": messages,
                "timeout": self.timeout,
                "stream": True,
            }
            if self.max_tokens:
                create_kwargs["max_completion_tokens"] = self.max_tokens

            stream = self.client.chat.completions.create(**create_kwargs)

            for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content

        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error(f"O1 streaming error: {e}", exc_info=True)
            yield f"Error: {str(e)}"

    def _build_messages(self, request: AgentRequest) -> list[dict[str, str]]:
        """Build chat messages from agent request."""
        messages = []

        # o1 models handle system prompts as developer messages
        if request.context and request.context.get("system"):
            messages.append({"role": "developer", "content": request.context["system"]})

        if request.context and request.context.get("history"):
            messages.extend(request.context["history"])

        messages.append({"role": "user", "content": request.prompt})
        return messages
