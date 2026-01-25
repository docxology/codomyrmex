"""Claude API client for Codomyrmex agents.

Provides a robust, feature-rich client for interacting with Anthropic's Claude API
with support for:
- System messages and multi-turn conversations
- Streaming responses
- Tool/function calling
- Retry logic with exponential backoff
- Session management integration
- Cost estimation
"""

from typing import Any, Callable, Iterator, Optional
import random
import time

from codomyrmex.agents.core.config import get_config
from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import ClaudeError
from codomyrmex.agents.core.session import AgentSession, SessionManager
from codomyrmex.agents.generic.api_agent_base import APIAgentBase
from codomyrmex.logging_monitoring import get_logger

try:
    import anthropic
except ImportError:
    anthropic = None


# Cost per 1M tokens (as of 2024) - update as pricing changes
CLAUDE_PRICING = {
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku-20241022": {"input": 1.00, "output": 5.00},
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
}


class ClaudeClient(APIAgentBase):
    """Client for interacting with Claude API.

    A comprehensive client that wraps the Anthropic API with:
    - Proper system message support
    - Retry logic with exponential backoff for transient failures
    - Tool/function calling capabilities
    - Session management for multi-turn conversations
    - Cost estimation based on token usage
    - Streaming support with metadata tracking
    """

    # Default retry configuration
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_INITIAL_DELAY = 1.0
    DEFAULT_MAX_DELAY = 60.0
    DEFAULT_BACKOFF_FACTOR = 2.0

    def __init__(
        self,
        config: Optional[dict[str, Any]] = None,
        session_manager: Optional[SessionManager] = None,
    ):
        """Initialize Claude client.

        Args:
            config: Optional configuration override. Supported keys:
                - claude_api_key: API key (or from ANTHROPIC_API_KEY env)
                - claude_model: Model to use (default: claude-3-5-sonnet-20241022)
                - claude_timeout: Request timeout in seconds
                - claude_max_tokens: Maximum output tokens
                - claude_temperature: Sampling temperature
                - max_retries: Maximum retry attempts for transient failures
                - initial_retry_delay: Initial delay between retries
            session_manager: Optional session manager for multi-turn conversations
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
                AgentCapabilities.TOOL_USE,
                AgentCapabilities.VISION,
                AgentCapabilities.CACHING,
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

        # Retry configuration
        self.max_retries = (config or {}).get("max_retries", self.DEFAULT_MAX_RETRIES)
        self.initial_retry_delay = (config or {}).get(
            "initial_retry_delay", self.DEFAULT_INITIAL_DELAY
        )
        self.max_retry_delay = (config or {}).get(
            "max_retry_delay", self.DEFAULT_MAX_DELAY
        )
        self.backoff_factor = (config or {}).get(
            "backoff_factor", self.DEFAULT_BACKOFF_FACTOR
        )

        # Session management
        self.session_manager = session_manager

        # Registered tools for function calling
        self._tools: list[dict[str, Any]] = []

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Optional[Callable] = None,
    ) -> None:
        """Register a tool for function calling.

        Args:
            name: Tool name (must be unique)
            description: Description of what the tool does
            input_schema: JSON Schema for tool input parameters
            handler: Optional callable to handle tool invocations
        """
        tool_def = {
            "name": name,
            "description": description,
            "input_schema": input_schema,
        }

        # Remove existing tool with same name
        self._tools = [t for t in self._tools if t["name"] != name]
        self._tools.append(tool_def)

        if handler:
            if not hasattr(self, "_tool_handlers"):
                self._tool_handlers: dict[str, Callable] = {}
            self._tool_handlers[name] = handler

        self.logger.debug(f"Registered tool: {name}")

    def get_registered_tools(self) -> list[dict[str, Any]]:
        """Get list of registered tools."""
        return self._tools.copy()

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
        except Exception as e:
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
        """Build Claude messages from request (legacy method).

        Args:
            request: Agent request

        Returns:
            List of message dictionaries
        """
        messages, _ = self._build_messages_with_system(request)
        return messages

    def _build_messages_with_system(
        self, request: AgentRequest
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
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

    # Session management methods

    def execute_with_session(
        self,
        request: AgentRequest,
        session: Optional[AgentSession] = None,
        session_id: Optional[str] = None,
    ) -> AgentResponse:
        """Execute request with session context for multi-turn conversations.

        Args:
            request: Agent request
            session: Existing session to use
            session_id: Session ID to retrieve from manager

        Returns:
            Agent response
        """
        # Get or create session
        if session is None and session_id and self.session_manager:
            session = self.session_manager.get_session(session_id)
        if session is None and self.session_manager:
            session = self.session_manager.create_session("claude")

        if session:
            # Add conversation history to context
            history = session.get_context()
            if "messages" not in (request.context or {}):
                if request.context is None:
                    request.context = {}
                request.context["messages"] = history

            # Add user message to session
            session.add_user_message(request.prompt)

        # Execute request
        response = self.execute(request)

        if session and response.is_success():
            # Add assistant response to session
            session.add_assistant_message(
                response.content,
                metadata={
                    "tokens_used": response.tokens_used,
                    "execution_time": response.execution_time,
                },
            )

        return response

    def create_session(self, session_id: Optional[str] = None) -> AgentSession:
        """Create a new conversation session.

        Args:
            session_id: Optional specific session ID

        Returns:
            New AgentSession
        """
        if self.session_manager:
            return self.session_manager.create_session("claude", session_id)
        return AgentSession(agent_name="claude")

    # Tool execution

    def execute_tool_call(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
    ) -> Any:
        """Execute a tool call using registered handler.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result

        Raises:
            ClaudeError: If tool not found or execution fails
        """
        if not hasattr(self, "_tool_handlers"):
            raise ClaudeError(f"No tool handlers registered")

        handler = self._tool_handlers.get(tool_name)
        if not handler:
            raise ClaudeError(f"No handler registered for tool: {tool_name}")

        try:
            return handler(**tool_input)
        except Exception as e:
            self.logger.error(f"Tool execution failed: {tool_name}", exc_info=True)
            raise ClaudeError(
                f"Tool execution failed: {e}",
                api_error=str(e),
            ) from e

    def execute_with_tools(
        self,
        request: AgentRequest,
        auto_execute: bool = True,
        max_tool_rounds: int = 10,
    ) -> AgentResponse:
        """Execute request with automatic tool execution.

        This method handles the tool use loop, automatically executing
        tool calls and continuing the conversation until Claude provides
        a final response.

        Args:
            request: Agent request
            auto_execute: Whether to automatically execute tool calls
            max_tool_rounds: Maximum number of tool execution rounds

        Returns:
            Final agent response
        """
        messages, system_message = self._build_messages_with_system(request)
        all_tool_calls = []

        for round_num in range(max_tool_rounds):
            # Build API call
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

            response = self.client.messages.create(**api_kwargs)

            # Check if we need to execute tools
            if response.stop_reason != "tool_use":
                # Final response
                content, _ = self._extract_response_content(response)
                input_tokens, output_tokens = self._extract_tokens_from_response(
                    response, "anthropic"
                )
                return AgentResponse(
                    content=content,
                    metadata={
                        "usage": {
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                        },
                        "stop_reason": response.stop_reason,
                        "tool_calls": all_tool_calls,
                        "tool_rounds": round_num + 1,
                    },
                    tokens_used=input_tokens + output_tokens,
                )

            # Extract and execute tool calls
            _, tool_calls = self._extract_response_content(response)

            if not tool_calls or not auto_execute:
                content, _ = self._extract_response_content(response)
                return AgentResponse(
                    content=content,
                    metadata={"tool_calls": tool_calls, "requires_tool_execution": True},
                )

            # Add assistant response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Execute tools and add results
            tool_results = []
            for tool_call in tool_calls:
                all_tool_calls.append(tool_call)
                try:
                    result = self.execute_tool_call(
                        tool_call["name"], tool_call["input"]
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call["id"],
                        "content": str(result),
                    })
                except Exception as e:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call["id"],
                        "content": f"Error: {str(e)}",
                        "is_error": True,
                    })

            messages.append({"role": "user", "content": tool_results})

        # Max rounds exceeded
        raise ClaudeError(
            f"Maximum tool execution rounds ({max_tool_rounds}) exceeded"
        )
