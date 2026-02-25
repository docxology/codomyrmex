"""ExecutionMixin functionality."""

import random
import time
from collections.abc import Iterator
from typing import Any

import anthropic

from codomyrmex.agents.core import (
    AgentRequest,
    AgentResponse,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

CLAUDE_PRICING = {
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-7-sonnet-20250219": {"input": 3.00, "output": 15.00},
}

class ExecutionMixin:
    """ExecutionMixin class."""

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute Claude API request with retry logic.

        Args:
            request: Agent request

        Returns:
            Agent response
        """
        return self._execute_with_retry(request)

    def _execute_with_retry(
        self,
        request: AgentRequest,
        attempt: int = 0,
    ) -> AgentResponse:
        """Execute request with exponential backoff retry.

        Args:
            request: Agent request
            attempt: Current attempt number

        Returns:
            Agent response
        """
        start_time = time.time()

        try:
            # Build messages with proper system message handling
            messages, system_message = self._build_messages_with_system(request)

            self.logger.debug(
                "Executing Claude API request",
                extra={
                    "agent": "claude",
                    "model": self.model,
                    "message_count": len(messages),
                    "prompt_length": len(request.prompt),
                    "has_system": bool(system_message),
                    "has_tools": bool(self._tools),
                    "attempt": attempt + 1,
                },
            )

            # Build API call kwargs
            api_kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": messages,
                "timeout": self.timeout,
            }

            # Add system message if present
            if system_message:
                api_kwargs["system"] = system_message

            # Add tools if registered
            if self._tools:
                api_kwargs["tools"] = self._tools

            # Call Claude API
            response = self.client.messages.create(**api_kwargs)

            execution_time = time.time() - start_time

            # Extract content and handle tool use
            content, tool_calls = self._extract_response_content(response)

            # Extract tokens using base class helper
            input_tokens, output_tokens = self._extract_tokens_from_response(
                response, "anthropic"
            )
            tokens_used = input_tokens + output_tokens

            # Calculate cost
            cost = self._calculate_cost(input_tokens, output_tokens)

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
                    "cost_usd": cost,
                    "tool_calls": len(tool_calls) if tool_calls else 0,
                },
            )

            metadata = {
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                },
                "stop_reason": response.stop_reason,
                "cost_usd": cost,
            }

            if tool_calls:
                metadata["tool_calls"] = tool_calls

            return self._build_agent_response(
                content=content,
                metadata=metadata,
                tokens_used=tokens_used,
                execution_time=execution_time,
            )

        except anthropic.RateLimitError as e:
            return self._handle_retryable_error(e, request, attempt, start_time)
        except anthropic.APIStatusError as e:
            if e.status_code in (500, 502, 503, 529):
                return self._handle_retryable_error(e, request, attempt, start_time)
            execution_time = time.time() - start_time
            self._handle_api_error(e, execution_time, anthropic.APIError)
        except anthropic.APIError as e:
            execution_time = time.time() - start_time
            self._handle_api_error(e, execution_time, anthropic.APIError)
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            execution_time = time.time() - start_time
            self._handle_api_error(e, execution_time)

    def _handle_retryable_error(
        self,
        error: Exception,
        request: AgentRequest,
        attempt: int,
        start_time: float,
    ) -> AgentResponse:
        """Handle retryable errors with exponential backoff.

        Args:
            error: The error that occurred
            request: Original request
            attempt: Current attempt number
            start_time: When the request started

        Returns:
            Agent response from retry, or raises if max retries exceeded
        """
        if attempt >= self.max_retries:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Max retries ({self.max_retries}) exceeded",
                extra={
                    "agent": "claude",
                    "model": self.model,
                    "error": str(error),
                    "attempts": attempt + 1,
                },
            )
            self._handle_api_error(error, execution_time, anthropic.APIError)

        # Calculate delay with jitter
        delay = min(
            self.initial_retry_delay * (self.backoff_factor**attempt),
            self.max_retry_delay,
        )
        # Add jitter (±25%)
        delay = delay * (0.75 + random.random() * 0.5)

        # Check for Retry-After header
        retry_after = getattr(error, "retry_after", None)
        if retry_after:
            delay = max(delay, float(retry_after))

        self.logger.warning(
            f"Retryable error, attempt {attempt + 1}/{self.max_retries + 1}, "
            f"retrying in {delay:.1f}s",
            extra={
                "agent": "claude",
                "model": self.model,
                "error": str(error),
                "delay": delay,
            },
        )

        time.sleep(delay)
        return self._execute_with_retry(request, attempt + 1)

    def _extract_response_content(
        self, response: Any
    ) -> tuple[str, list[dict[str, Any]]]:
        """Extract content and tool calls from response.

        Args:
            response: Claude API response

        Returns:
            Tuple of (text_content, tool_calls)
        """
        content = ""
        tool_calls = []

        if response.content:
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text
                elif block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })

        return content, tool_calls

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream Claude API response.

        Args:
            request: Agent request

        Yields:
            Chunks of response content
        """
        try:
            messages, system_message = self._build_messages_with_system(request)

            self.logger.debug(
                "Starting Claude API stream",
                extra={
                    "agent": "claude",
                    "model": self.model,
                    "message_count": len(messages),
                    "has_system": bool(system_message),
                },
            )

            # Build API call kwargs
            api_kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": messages,
                "timeout": self.timeout,
            }

            if system_message:
                api_kwargs["system"] = system_message

            if self._tools:
                api_kwargs["tools"] = self._tools

            chunk_count = 0
            with self.client.messages.stream(**api_kwargs) as stream:
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
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
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

    def _build_messages_with_system(
        self, request: AgentRequest
    ) -> tuple[list[dict[str, Any]], str | None]:
        """Build Claude messages with proper system message handling.

        Args:
            request: Agent request

        Returns:
            Tuple of (messages, system_message)
        """
        messages = []
        system_message = None

        # Extract system message from context
        if request.context:
            # Check for explicit system message
            if "system" in request.context:
                system_message = request.context["system"]
            elif "system_prompt" in request.context:
                system_message = request.context["system_prompt"]
            else:
                # Build system message from other context (excluding reserved keys)
                reserved_keys = {"messages", "tools", "session_id", "images"}
                context_items = {
                    k: v for k, v in request.context.items() if k not in reserved_keys
                }
                if context_items:
                    system_message = "\n".join(
                        f"{k}: {v}" for k, v in context_items.items()
                    )

            # Check for conversation history in context
            if "messages" in request.context:
                for msg in request.context["messages"]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", ""),
                    })

        # Add main prompt (with optional image support)
        if request.context and "images" in request.context:
            # Multi-modal message with images
            content = [{"type": "text", "text": request.prompt}]
            for image in request.context["images"]:
                if isinstance(image, dict):
                    content.append(image)
                elif isinstance(image, str):
                    # Assume base64 encoded image
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image,
                        },
                    })
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": request.prompt})

        return messages, system_message

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD based on token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        pricing = CLAUDE_PRICING.get(self.model)
        if not pricing:
            # Use default pricing for unknown models
            pricing = {"input": 3.00, "output": 15.00}

        cost = (input_tokens / 1_000_000 * pricing["input"]) + (
            output_tokens / 1_000_000 * pricing["output"]
        )
        return round(cost, 6)

