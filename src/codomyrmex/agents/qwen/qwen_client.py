"""Qwen-Coder API client for Codomyrmex agents."""

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


class QwenClient(APIAgentBase):
    """Client for Qwen-Coder models via OpenAI-compatible API.

    Supports multilingual code generation and analysis using
    Alibaba's Qwen-Coder models.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize Qwen client.

        Args:
            config: Optional configuration override
        """
        super().__init__(
            name="qwen",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
            ],
            api_key_config_key="qwen_api_key",
            model_config_key="qwen_model",
            timeout_config_key="qwen_timeout",
            max_tokens_config_key="qwen_max_tokens",
            temperature_config_key="qwen_temperature",
            client_class=openai,
            client_init_func=lambda api_key: openai.OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
            error_class=AgentError,
            config=config,
        )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute Qwen API request."""
        start_time = time.time()

        try:
            messages = self._build_messages(request)

            response = self.client.chat.completions.create(
                model=self.model or "qwen-coder-turbo",
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout,
            )

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

        except Exception as e:
            execution_time = time.time() - start_time
            self._handle_api_error(e, execution_time)

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream Qwen API response."""
        try:
            messages = self._build_messages(request)

            stream = self.client.chat.completions.create(
                model=self.model or "qwen-coder-turbo",
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content

        except Exception as e:
            self.logger.error(f"Qwen streaming error: {e}", exc_info=True)
            yield f"Error: {str(e)}"

    def _build_messages(self, request: AgentRequest) -> list[dict[str, str]]:
        """Build chat messages from agent request."""
        messages = []

        if request.context and request.context.get("system"):
            messages.append({"role": "system", "content": request.context["system"]})

        if request.context and request.context.get("history"):
            messages.extend(request.context["history"])

        messages.append({"role": "user", "content": request.prompt})
        return messages
