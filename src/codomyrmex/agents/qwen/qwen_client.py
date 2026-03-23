"""Qwen API client for Codomyrmex agents.

Supports:
- Chat completion (single-turn and multi-turn)
- Streaming responses
- Tool/function calling with OpenAI-compatible tool schema
- Qwen-Coder, Qwen-Max, Qwen-Plus, and all DashScope models
- Self-hosted Qwen via configurable base_url
"""

import json
import os
import time
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import openai

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
    if not TYPE_CHECKING:
        pass

# --- Model Registry ---

QWEN_MODELS: dict[str, dict[str, Any]] = {
    # Flagship reasoning
    "qwen3-max": {"context": 131072, "category": "flagship"},
    "qwen3-plus": {"context": 131072, "category": "flagship"},
    "qwen3-mini": {"context": 131072, "category": "lightweight"},
    # Code-specialized
    "qwen-coder-turbo": {"context": 131072, "category": "code"},
    "qwen-coder-plus": {"context": 131072, "category": "code"},
    "qwen2.5-coder-32b-instruct": {"context": 32768, "category": "code"},
    "qwen2.5-coder-14b-instruct": {"context": 32768, "category": "code"},
    "qwen2.5-coder-7b-instruct": {"context": 32768, "category": "code"},
    # General
    "qwen-turbo": {"context": 131072, "category": "general"},
    "qwen-plus": {"context": 131072, "category": "general"},
    "qwen-max": {"context": 131072, "category": "general"},
    # Long-context
    "qwen-long": {"context": 1000000, "category": "long"},
    # Vision
    "qwen-vl-max": {"context": 32768, "category": "vision"},
    "qwen-vl-plus": {"context": 32768, "category": "vision"},
}

DEFAULT_MODEL = "qwen-coder-turbo"
DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


class QwenClient(APIAgentBase):
    """Client for Qwen models via OpenAI-compatible API (DashScope).

    Supports all Qwen model variants including Qwen3-Max, Qwen-Coder,
    Qwen-VL, and self-hosted deployments. Provides chat completion,
    streaming, and tool/function calling.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize Qwen client.

        Args:
            config: Optional configuration override. Keys:
                - qwen_api_key: DashScope API key (or DASHSCOPE_API_KEY env)
                - qwen_model: Model name (default: qwen-coder-turbo)
                - qwen_base_url: API base URL (default: DashScope)
                - qwen_timeout: Request timeout in seconds
                - qwen_max_tokens: Max response tokens
                - qwen_temperature: Sampling temperature
        """
        self._base_url = (config or {}).get(
            "qwen_base_url",
            os.getenv("QWEN_BASE_URL", DEFAULT_BASE_URL),
        )

        api_key_env = os.getenv("DASHSCOPE_API_KEY", os.getenv("QWEN_API_KEY", ""))

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
                api_key=api_key or api_key_env,
                base_url=self._base_url,
                max_retries=(config or {}).get("max_retries", 3),
            ),
            error_class=AgentError,
            config=config,
        )

        # Retry configuration
        self.max_retries = (config or {}).get("max_retries", 3)
        self.initial_retry_delay = (config or {}).get("initial_retry_delay", 1.0)
        self.max_retry_delay = (config or {}).get("max_retry_delay", 60.0)
        self.backoff_factor = (config or {}).get("backoff_factor", 2.0)

    # --- Core chat completion ---

    def _execute_impl(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        """Execute Qwen API request with optional tool calling."""
        start_time = time.time()

        try:
            messages = self._build_messages(request)
            model = self.model or DEFAULT_MODEL

            kwargs: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "timeout": self.timeout,
            }

            # Add tools if request has them
            tools = self._extract_tools(request)
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)

            execution_time = time.time() - start_time
            choice = response.choices[0] if response.choices else None
            content = choice.message.content if choice else ""

            # Handle tool calls
            tool_calls_data = []
            if choice and choice.message.tool_calls:
                for tc in choice.message.tool_calls:
                    tool_calls_data.append(
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                    )

            input_tokens, output_tokens = self._extract_tokens_from_response(
                response, "openai"
            )
            tokens_used = input_tokens + output_tokens

            return self._build_agent_response(
                content=content or "",
                metadata={
                    "model": model,
                    "usage": {
                        "prompt_tokens": input_tokens,
                        "completion_tokens": output_tokens,
                    },
                    "finish_reason": (choice.finish_reason if choice else None),
                    "tool_calls": tool_calls_data or None,
                },
                tokens_used=tokens_used,
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            # For Qwen (using OpenAI SDK), we pass openai.APIError to the handler
            return self._handle_api_error_response(
                e, execution_time, request.id, getattr(openai, "APIError", None)
            )

    def _handle_api_error_response(
        self,
        error: Exception,
        execution_time: float,
        request_id: str | None = None,
        api_error_class: Any | None = None,
    ) -> AgentResponse:
        """Handle API error and return AgentResponse."""
        try:
            self._handle_api_error(error, execution_time, api_error_class)
        except Exception as e:
            return AgentResponse(
                content="",
                error=str(e),
                metadata={"error_type": type(e).__name__},
                request_id=request_id,
                execution_time=execution_time,
            )
        # Should not be reached as _handle_api_error raises
        return AgentResponse(content="", error=str(error), request_id=request_id)

    # --- Streaming ---

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream Qwen API response."""
        try:
            messages = self._build_messages(request)
            model = self.model or DEFAULT_MODEL

            stream = self.client.chat.completions.create(
                model=model,
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

        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Qwen streaming error: %s", e, exc_info=True)
            yield f"Error: {e!s}"

    # --- Tool calling ---

    def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        *,
        model: str | None = None,
        max_iterations: int = 5,
        tool_executor: Any | None = None,
    ) -> list[dict[str, Any]]:
        """Run a multi-turn tool-calling loop.

        Args:
            messages: Initial conversation messages.
            tools: OpenAI-format tool definitions.
            model: Model override (default: configured model).
            max_iterations: Max tool-call rounds.
            tool_executor: Callable(name, args) -> str that runs the tool.

        Returns:
            Full message history including tool calls and results.
        """
        model = model or self.model or DEFAULT_MODEL
        conversation = list(messages)

        for _ in range(max_iterations):
            response = self.client.chat.completions.create(
                model=model,
                messages=conversation,
                tools=tools,
                tool_choice="auto",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            choice = response.choices[0]
            assistant_msg = choice.message

            # Append assistant response
            msg_dict: dict[str, Any] = {
                "role": "assistant",
                "content": assistant_msg.content or "",
            }
            if assistant_msg.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_msg.tool_calls
                ]
            conversation.append(msg_dict)

            # If no tool calls, we're done
            if not assistant_msg.tool_calls:
                break

            # Execute each tool call
            for tc in assistant_msg.tool_calls:
                fn_name = tc.function.name
                fn_args_str = tc.function.arguments
                try:
                    fn_args = json.loads(fn_args_str)
                except json.JSONDecodeError:
                    fn_args = {}

                if tool_executor:
                    result = str(tool_executor(fn_name, fn_args))
                else:
                    result = f"Tool '{fn_name}' executed (no executor configured)"

                conversation.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    }
                )

        return conversation

    # --- Utility ---

    @staticmethod
    def list_models() -> dict[str, dict[str, Any]]:
        """Return the Qwen model registry."""
        return dict(QWEN_MODELS)

    @staticmethod
    def get_code_models() -> list[str]:
        """Return code-specialized model names."""
        return [k for k, v in QWEN_MODELS.items() if v["category"] == "code"]

    def _extract_tools(self, request: AgentRequest) -> list[dict[str, Any]] | None:
        """Extract tool definitions from request metadata."""
        if hasattr(request, "metadata") and request.metadata:
            return request.metadata.get("tools")
        return None
