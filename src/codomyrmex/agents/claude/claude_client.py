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

import random
import time
from collections.abc import Callable, Iterator
from typing import Any

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import ClaudeError
from codomyrmex.agents.core.session import AgentSession, SessionManager
from codomyrmex.agents.generic.api_agent_base import APIAgentBase

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
        config: dict[str, Any] | None = None,
        session_manager: SessionManager | None = None,
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
        handler: Callable | None = None,
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

    # Session management methods

    def execute_with_session(
        self,
        request: AgentRequest,
        session: AgentSession | None = None,
        session_id: str | None = None,
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

    def create_session(self, session_id: str | None = None) -> AgentSession:
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
            raise ClaudeError("No tool handlers registered")

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

    # Claude Code methods for agentic coding workflows

    def edit_file(
        self,
        file_path: str,
        instructions: str,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Apply AI-guided edits to a file.

        Uses Claude to understand the file content and apply edits
        based on natural language instructions.

        Args:
            file_path: Absolute path to the file to edit
            instructions: Natural language description of edits to make
            language: Programming language (auto-detected if None)

        Returns:
            Dictionary containing:
                - success: Whether editing succeeded
                - original_content: Original file content
                - modified_content: Modified file content
                - diff: Unified diff of changes
                - explanation: Description of changes made
                - tokens_used: Tokens consumed
                - cost_usd: Estimated cost

        Example:
            >>> result = client.edit_file(
            ...     "/path/to/file.py",
            ...     "Add type hints to all function parameters"
            ... )
            >>> print(result["diff"])
        """
        import os

        # Read the file
        if not os.path.isfile(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "original_content": "",
                "modified_content": "",
            }

        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {e}",
                "original_content": "",
                "modified_content": "",
            }

        # Auto-detect language from extension
        if language is None:
            ext = os.path.splitext(file_path)[1].lower()
            lang_map = {
                ".py": "python", ".js": "javascript", ".ts": "typescript",
                ".java": "java", ".cpp": "cpp", ".c": "c", ".go": "go",
                ".rs": "rust", ".rb": "ruby", ".php": "php", ".swift": "swift",
                ".kt": "kotlin", ".scala": "scala", ".cs": "csharp",
            }
            language = lang_map.get(ext, "text")

        # Build the prompt
        system_prompt = f"""You are an expert {language} developer performing code edits.
Apply the requested changes to the provided code.
Return ONLY the complete modified code, no explanations.
Preserve all existing functionality unless explicitly asked to change it."""

        prompt = f"""Edit this {language} file according to the instructions.

Instructions: {instructions}

Current file content:
```{language}
{original_content}
```

Return the complete modified file content:"""

        request = AgentRequest(
            prompt=prompt,
            context={"system": system_prompt},
        )

        response = self.execute(request)

        if not response.is_success():
            return {
                "success": False,
                "error": response.error,
                "original_content": original_content,
                "modified_content": "",
            }

        # Extract code from response
        modified_content = self._extract_code_block(response.content, language)

        # Generate diff
        diff = self._generate_unified_diff(original_content, modified_content, file_path)

        return {
            "success": True,
            "original_content": original_content,
            "modified_content": modified_content,
            "diff": diff,
            "explanation": f"Applied edits: {instructions}",
            "language": language,
            "tokens_used": response.tokens_used,
            "cost_usd": response.metadata.get("cost_usd", 0.0),
        }

    def create_file(
        self,
        file_path: str,
        description: str,
        language: str = "python",
    ) -> dict[str, Any]:
        """Generate a new file from a description.

        Uses Claude to create file content based on a natural language
        description of what the file should contain.

        Args:
            file_path: Path where file should be created
            description: Description of what the file should contain
            language: Programming language

        Returns:
            Dictionary containing:
                - success: Whether creation succeeded
                - content: Generated file content
                - file_path: Path to created file
                - tokens_used: Tokens consumed
                - cost_usd: Estimated cost

        Example:
            >>> result = client.create_file(
            ...     "/path/to/utils.py",
            ...     "Utility functions for string manipulation"
            ... )
        """
        import os

        system_prompt = f"""You are an expert {language} developer.
Generate clean, well-documented, production-ready code.
Follow {language} best practices and include appropriate error handling.
Return ONLY the code, no explanations or markdown wrappers."""

        prompt = f"""Create a {language} file with the following content:

Description: {description}
Filename: {os.path.basename(file_path)}

Generate the complete file content:"""

        request = AgentRequest(
            prompt=prompt,
            context={"system": system_prompt},
        )

        response = self.execute(request)

        if not response.is_success():
            return {
                "success": False,
                "error": response.error,
                "content": "",
                "file_path": file_path,
            }

        content = self._extract_code_block(response.content, language)

        return {
            "success": True,
            "content": content,
            "file_path": file_path,
            "language": language,
            "tokens_used": response.tokens_used,
            "cost_usd": response.metadata.get("cost_usd", 0.0),
        }

    def review_code(
        self,
        code: str,
        language: str = "python",
        analysis_type: str = "general",
    ) -> dict[str, Any]:
        """Perform AI-powered code review.

        Uses Claude to analyze code for issues, bugs, security
        vulnerabilities, and improvement opportunities.

        Args:
            code: Code to review
            language: Programming language
            analysis_type: Type of analysis:
                - "general": Overall code review
                - "security": Security-focused analysis
                - "bugs": Bug and error detection
                - "performance": Performance analysis

        Returns:
            Dictionary containing:
                - success: Whether review succeeded
                - output: Full analysis text
                - issues: List of identified issues
                - recommendations: List of suggestions
                - tokens_used: Tokens consumed
                - cost_usd: Estimated cost

        Example:
            >>> result = client.review_code(
            ...     "def add(a, b): return a + b",
            ...     language="python",
            ...     analysis_type="general"
            ... )
        """
        analysis_prompts = {
            "general": "Analyze for correctness, style, and improvements.",
            "security": "Identify security vulnerabilities and risks.",
            "bugs": "Find bugs, edge cases, and potential runtime errors.",
            "performance": "Identify performance issues and optimizations.",
        }

        analysis_instruction = analysis_prompts.get(analysis_type, analysis_prompts["general"])

        system_prompt = f"""You are an expert {language} code analyst.
Provide thorough, actionable code review.
Structure your response with:
1. Summary
2. Issues (as bullet points)
3. Recommendations (as bullet points)"""

        prompt = f"""{analysis_instruction}

```{language}
{code}
```"""

        request = AgentRequest(
            prompt=prompt,
            context={"system": system_prompt},
        )

        response = self.execute(request)

        if not response.is_success():
            return {
                "success": False,
                "error": response.error,
                "output": "",
                "issues": [],
                "recommendations": [],
            }

        # Parse issues and recommendations
        issues, recommendations = self._parse_review_output(response.content)

        return {
            "success": True,
            "output": response.content,
            "issues": issues,
            "recommendations": recommendations,
            "language": language,
            "analysis_type": analysis_type,
            "tokens_used": response.tokens_used,
            "cost_usd": response.metadata.get("cost_usd", 0.0),
        }

    def scan_directory(
        self,
        path: str,
        max_depth: int = 3,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> dict[str, Any]:
        """Scan directory for project context.

        Scans a directory structure to understand the project layout,
        useful for providing context in agentic coding workflows.

        Args:
            path: Directory path to scan
            max_depth: Maximum directory depth (default: 3)
            include_patterns: Glob patterns to include (e.g., ["*.py", "*.js"])
            exclude_patterns: Glob patterns to exclude (e.g., ["node_modules", "__pycache__"])

        Returns:
            Dictionary containing:
                - success: Whether scan succeeded
                - structure: Hierarchical dict of directory
                - file_count: Total files found
                - files: List of file paths
                - summary: Directory summary

        Example:
            >>> result = client.scan_directory("/path/to/project")
            >>> print(result["structure"])
        """
        import fnmatch
        import os

        if not os.path.isdir(path):
            return {
                "success": False,
                "error": f"Directory not found: {path}",
                "structure": {},
                "file_count": 0,
                "files": [],
            }

        # Default exclusions
        default_exclude = [
            "__pycache__", "node_modules", ".git", ".venv", "venv",
            "*.pyc", "*.pyo", ".DS_Store", "*.egg-info",
        ]
        exclude = (exclude_patterns or []) + default_exclude

        def should_exclude(name: str) -> bool:
            """Execute Should Exclude operations natively."""
            return any(fnmatch.fnmatch(name, pat) for pat in exclude)

        def should_include(name: str) -> bool:
            """Execute Should Include operations natively."""
            if not include_patterns:
                return True
            return any(fnmatch.fnmatch(name, pat) for pat in include_patterns)

        def scan_dir(dir_path: str, depth: int) -> dict:
            """Execute Scan Dir operations natively."""
            if depth > max_depth:
                return {"type": "directory", "truncated": True}

            result: dict[str, Any] = {"type": "directory", "children": {}}

            try:
                for entry in os.scandir(dir_path):
                    if should_exclude(entry.name):
                        continue

                    if entry.is_dir():
                        result["children"][entry.name] = scan_dir(entry.path, depth + 1)
                    elif entry.is_file() and should_include(entry.name):
                        result["children"][entry.name] = {
                            "type": "file",
                            "size": entry.stat().st_size,
                        }
            except PermissionError:
                result["error"] = "Permission denied"

            return result

        structure = scan_dir(path, 0)

        # Collect all file paths
        files: list[str] = []

        def collect_files(node: dict, current_path: str) -> None:
            """Execute Collect Files operations natively."""
            for name, child in node.get("children", {}).items():
                child_path = os.path.join(current_path, name)
                if child.get("type") == "file":
                    files.append(child_path)
                elif child.get("type") == "directory":
                    collect_files(child, child_path)

        collect_files(structure, path)

        return {
            "success": True,
            "structure": structure,
            "file_count": len(files),
            "files": files,
            "summary": f"Scanned {len(files)} files in {path}",
        }

    def generate_diff(
        self,
        original: str,
        modified: str,
        filename: str = "file",
    ) -> dict[str, Any]:
        """Generate unified diff between code versions.

        Creates a unified diff format output showing the differences
        between original and modified code.

        Args:
            original: Original code content
            modified: Modified code content
            filename: Filename for diff header

        Returns:
            Dictionary containing:
                - diff: Unified diff string
                - additions: Number of lines added
                - deletions: Number of lines removed
                - has_changes: Whether there are any changes

        Example:
            >>> diff_result = client.generate_diff(
            ...     "def foo():\\n    pass",
            ...     "def foo():\\n    return 42"
            ... )
            >>> print(diff_result["diff"])
        """
        diff = self._generate_unified_diff(original, modified, filename)

        # Count additions and deletions
        additions = 0
        deletions = 0
        for line in diff.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

        return {
            "diff": diff,
            "additions": additions,
            "deletions": deletions,
            "has_changes": additions > 0 or deletions > 0,
        }

    def _extract_code_block(self, response: str, language: str) -> str:
        """Extract code from markdown-formatted response."""
        import re

        # Try language-specific block
        pattern = rf"```{language}\n(.*?)```"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try generic code block
        pattern = r"```\n?(.*?)```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()

        return response.strip()

    def _generate_unified_diff(
        self,
        original: str,
        modified: str,
        filename: str,
    ) -> str:
        """Generate unified diff between two strings."""
        import difflib

        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
        )

        return "".join(diff)

    def _parse_review_output(self, output: str) -> tuple[list[str], list[str]]:
        """Parse code review output for issues and recommendations."""
        issues: list[str] = []
        recommendations: list[str] = []

        lines = output.split("\n")
        current_section = None

        for line in lines:
            line_stripped = line.strip()
            lower_line = line_stripped.lower()

            if "issue" in lower_line or "problem" in lower_line or "bug" in lower_line:
                current_section = "issues"
            elif "recommend" in lower_line or "suggestion" in lower_line or "improvement" in lower_line:
                current_section = "recommendations"
            elif line_stripped.startswith(("-", "*", "•", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
                item = line_stripped.lstrip("-*•0123456789.) ").strip()
                if item and len(item) > 5:  # Filter out very short items
                    if current_section == "issues":
                        issues.append(item)
                    elif current_section == "recommendations":
                        recommendations.append(item)

        return issues, recommendations

    def run_command(
        self,
        command: str,
        cwd: str | None = None,
        timeout: int = 60,
        capture_output: bool = True,
    ) -> dict[str, Any]:
        """Execute a shell command with optional AI analysis.

        Runs the specified command and returns the output. Can optionally
        analyze the output for errors or issues.

        Args:
            command: Shell command to execute
            cwd: Working directory for command execution
            timeout: Maximum execution time in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            Dictionary containing:
                - success: Whether command executed successfully
                - return_code: Process return code
                - stdout: Standard output
                - stderr: Standard error
                - duration: Execution time in seconds

        Example:
            >>> result = client.run_command("ls -la")
            >>> print(result["stdout"])
        """
        import subprocess
        import time

        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                shell=True,  # SECURITY: Intentional — run_command is an agent shell executor
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
            )
            duration = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
                "duration": duration,
                "command": command,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "duration": timeout,
                "command": command,
            }
        except Exception as e:
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": time.time() - start_time,
                "command": command,
            }

    def get_project_structure(
        self,
        path: str,
        max_depth: int = 4,
        include_analysis: bool = False,
    ) -> dict[str, Any]:
        """Get comprehensive project structure analysis.

        Scans the project directory and optionally uses AI to analyze
        the project type, dependencies, and structure.

        Args:
            path: Root directory of the project
            max_depth: Maximum scan depth
            include_analysis: Whether to include AI-powered analysis

        Returns:
            Dictionary containing:
                - success: Whether scan succeeded
                - structure: Directory tree
                - file_count: Total files
                - language_breakdown: Files by language
                - analysis: AI analysis (if requested)

        Example:
            >>> result = client.get_project_structure("/path/to/project")
            >>> print(result["language_breakdown"])
        """
        import os
        from collections import defaultdict

        # First, do a basic scan
        scan_result = self.scan_directory(path, max_depth=max_depth)

        if not scan_result["success"]:
            return scan_result

        # Analyze language breakdown
        lang_map = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".java": "Java", ".cpp": "C++", ".c": "C", ".go": "Go",
            ".rs": "Rust", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
            ".kt": "Kotlin", ".scala": "Scala", ".cs": "C#",
            ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
            ".md": "Markdown", ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
            ".sh": "Shell", ".bash": "Shell",
        }

        language_breakdown: dict[str, int] = defaultdict(int)
        for file_path in scan_result.get("files", []):
            ext = os.path.splitext(file_path)[1].lower()
            lang = lang_map.get(ext, "Other")
            language_breakdown[lang] += 1

        result = {
            "success": True,
            "path": path,
            "structure": scan_result["structure"],
            "file_count": scan_result["file_count"],
            "files": scan_result["files"],
            "language_breakdown": dict(language_breakdown),
        }

        # Optionally add AI analysis
        if include_analysis and self.test_connection():
            system_prompt = """You are a software architect analyzing a project.
Provide a brief analysis including:
1. Project type (web app, library, CLI tool, etc.)
2. Primary language/framework
3. Notable patterns or architecture
Be concise."""

            files_summary = "\n".join(scan_result["files"][:50])
            langs = ", ".join(f"{k}: {v}" for k, v in sorted(
                language_breakdown.items(), key=lambda x: -x[1]
            )[:5])

            prompt = f"""Analyze this project structure:
Path: {path}
Files: {scan_result['file_count']}
Languages: {langs}

Sample files:
{files_summary}"""

            try:
                response = self.execute(AgentRequest(
                    prompt=prompt,
                    context={"system": system_prompt}
                ))
                if response.is_success():
                    result["analysis"] = response.content
                    result["tokens_used"] = response.tokens_used
            except Exception:
                pass  # Analysis is optional

        return result

    def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium",
    ) -> dict[str, Any]:
        """Generate a comprehensive explanation of code.

        Uses Claude to explain what the code does, how it works,
        and any notable patterns or algorithms used.

        Args:
            code: Code to explain
            language: Programming language
            detail_level: Level of detail ("brief", "medium", "detailed")

        Returns:
            Dictionary containing:
                - success: Whether explanation succeeded
                - explanation: Full explanation text
                - summary: One-line summary
                - concepts: Key concepts mentioned
                - tokens_used: Tokens consumed
                - cost_usd: Estimated cost

        Example:
            >>> result = client.explain_code("def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)")
            >>> print(result["summary"])
        """
        detail_prompts = {
            "brief": "Provide a 2-3 sentence explanation.",
            "medium": "Provide a clear explanation covering purpose, logic, and key patterns.",
            "detailed": "Provide an in-depth explanation including purpose, step-by-step logic, patterns, edge cases, and potential improvements.",
        }

        detail_instruction = detail_prompts.get(detail_level, detail_prompts["medium"])

        system_prompt = f"""You are an expert {language} developer and educator.
Explain code clearly for developers of varying skill levels.
Structure your response:
1. Summary (one line)
2. Explanation
3. Key Concepts (bullet points)"""

        prompt = f"""{detail_instruction}

```{language}
{code}
```"""

        request = AgentRequest(
            prompt=prompt,
            context={"system": system_prompt},
        )

        response = self.execute(request)

        if not response.is_success():
            return {
                "success": False,
                "error": response.error,
                "explanation": "",
                "summary": "",
                "concepts": [],
            }

        # Parse the response
        content = response.content
        summary = ""
        concepts = []

        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "summary" in line.lower() and i + 1 < len(lines):
                summary = lines[i + 1].strip().lstrip("-•* ")
                break
            elif line.strip() and not any(h in line.lower() for h in ["explanation", "concept", "##", "#"]):
                summary = line.strip()
                break

        # Extract concepts
        in_concepts = False
        for line in lines:
            if "concept" in line.lower():
                in_concepts = True
                continue
            if in_concepts and line.strip().startswith(("-", "*", "•")):
                concept = line.strip().lstrip("-*• ").strip()
                if concept:
                    concepts.append(concept)
            elif in_concepts and line.strip() and not line.strip().startswith(("-", "*", "•")):
                if line.startswith("#"):
                    in_concepts = False

        return {
            "success": True,
            "explanation": content,
            "summary": summary[:200] if summary else "See full explanation",
            "concepts": concepts[:10],
            "language": language,
            "detail_level": detail_level,
            "tokens_used": response.tokens_used,
            "cost_usd": response.metadata.get("cost_usd", 0.0),
        }

    def suggest_tests(
        self,
        code: str,
        language: str = "python",
        framework: str | None = None,
    ) -> dict[str, Any]:
        """Generate test suggestions for code.

        Uses Claude to analyze code and suggest appropriate tests,
        including edge cases and common testing patterns.

        Args:
            code: Code to generate tests for
            language: Programming language
            framework: Testing framework (e.g., "pytest", "unittest", "jest")

        Returns:
            Dictionary containing:
                - success: Whether generation succeeded
                - tests: Generated test code
                - test_cases: List of test case descriptions
                - coverage_notes: Notes about test coverage
                - tokens_used: Tokens consumed
                - cost_usd: Estimated cost

        Example:
            >>> result = client.suggest_tests("def add(a, b): return a + b")
            >>> print(result["tests"])
        """
        if framework is None:
            framework = "pytest" if language == "python" else "jest" if language in ("javascript", "typescript") else "default"

        system_prompt = f"""You are an expert {language} testing specialist.
Generate comprehensive tests using {framework}.
Include:
1. Basic functionality tests
2. Edge cases
3. Error handling tests

Return:
1. Test code (ready to run)
2. List of test cases with descriptions"""

        prompt = f"""Generate tests for this {language} code using {framework}:

```{language}
{code}
```"""

        request = AgentRequest(
            prompt=prompt,
            context={"system": system_prompt},
        )

        response = self.execute(request)

        if not response.is_success():
            return {
                "success": False,
                "error": response.error,
                "tests": "",
                "test_cases": [],
                "coverage_notes": "",
            }

        content = response.content
        tests = self._extract_code_block(content, language)

        # Extract test case descriptions
        test_cases = []
        for line in content.split("\n"):
            line_stripped = line.strip()
            if line_stripped.startswith(("-", "*", "•", "1", "2", "3", "4", "5")):
                case = line_stripped.lstrip("-*•0123456789.) ").strip()
                if case and ("test" in case.lower() or "case" in case.lower() or "should" in case.lower()):
                    test_cases.append(case)

        return {
            "success": True,
            "tests": tests,
            "test_cases": test_cases[:15],
            "coverage_notes": f"Generated {len(test_cases)} test cases for {framework}",
            "language": language,
            "framework": framework,
            "tokens_used": response.tokens_used,
            "cost_usd": response.metadata.get("cost_usd", 0.0),
        }
