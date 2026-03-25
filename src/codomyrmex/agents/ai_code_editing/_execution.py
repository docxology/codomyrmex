import logging
import re
import time
from collections.abc import Iterator
from typing import Any, Protocol

logger = logging.getLogger(__name__)

# Constants matched from master
MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.3


class _ClaudeTaskExecutionHost(Protocol):
    """Host contract for :class:`ClaudeTaskExecutionMixin`.

    The mixin implements prompts and response parsing; the concrete host
    (e.g. ``ClaudeTaskMaster``) supplies the Anthropic client, retry wrapper,
    pricing, and cumulative usage counters.
    """

    model: str
    _task_counter: int
    _total_tokens: int
    _total_cost: float

    def _get_client(self) -> Any: ...

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float: ...

    def _execute_with_retry(
        self,
        messages: list[dict[str, Any]],
        system: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any,
    ) -> tuple[Any, int]: ...


class ClaudeTaskExecutionMixin:
    """Mixin for Claude task master execution and code generation logic."""

    def execute_task(
        self: _ClaudeTaskExecutionHost,
        task: str,
        context: str | None = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute a task using Claude.

        Args:
            task: Task description to execute
            context: Additional context for the task
            max_tokens: Maximum tokens for response
            temperature: Sampling temperature
            **kwargs: Additional arguments for the API

        Returns:
            Dictionary containing task result and metadata

        Raises:
            RuntimeError: If task execution fails
        """
        start_time = time.time()
        self._task_counter += 1
        task_id = f"task_{self._task_counter}_{int(time.time())}"

        try:
            system_prompt = self._build_task_system_prompt()
            user_message = self._build_task_message(task, context)

            response, retries = self._execute_with_retry(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            execution_time = time.time() - start_time
            result_text = response.content[0].text if response.content else ""
            input_tokens = (
                response.usage.input_tokens
                if hasattr(response, "usage") and response.usage
                else 0
            )
            output_tokens = (
                response.usage.output_tokens
                if hasattr(response, "usage") and response.usage
                else 0
            )
            tokens_used = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Track totals
            self._total_tokens += tokens_used
            self._total_cost += cost

            logger.info(
                "Executed task %s using %s in %.2fs (%s tokens, $%.6f)",
                task_id,
                self.model,
                execution_time,
                tokens_used,
                cost,
            )

            return {
                "task_id": task_id,
                "task": task,
                "result": result_text,
                "status": "completed",
                "model": self.model,
                "tokens_used": tokens_used,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
                "execution_time": execution_time,
                "retries": retries,
            }

        except ImportError as e:
            logger.error("Anthropic import error: %s", e)
            raise
        except ValueError as e:
            logger.error("Configuration error: %s", e)
            raise RuntimeError(f"Task execution failed: {e}") from None
        except (RuntimeError, AttributeError, OSError, TypeError) as e:
            execution_time = time.time() - start_time
            logger.error("Error executing task: %s", e, exc_info=True)
            return {
                "task_id": task_id,
                "task": task,
                "result": None,
                "status": "failed",
                "error": str(e),
                "model": self.model,
                "tokens_used": 0,
                "cost_usd": 0.0,
                "execution_time": execution_time,
                "retries": 0,
            }

    def execute_task_stream(
        self: _ClaudeTaskExecutionHost,
        task: str,
        context: str | None = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Execute a task with streaming response.

        Args:
            task: Task description
            context: Additional context
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            **kwargs: Additional API arguments

        Yields:
            Chunks of the response text
        """
        try:
            client = self._get_client()
            system_prompt = self._build_task_system_prompt()
            user_message = self._build_task_message(task, context)

            with client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                **kwargs,
            ) as stream:
                yield from stream.text_stream

        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Streaming error: %s", e, exc_info=True)
            yield f"Error: {e!s}"

    def generate_code(
        self: _ClaudeTaskExecutionHost,
        description: str,
        language: str = "python",
        context: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate code based on a description.

        Args:
            description: Description of the code to generate
            language: Programming language
            context: Additional context (e.g., existing code)
            **kwargs: Additional arguments

        Returns:
            Dictionary containing generated code and metadata
        """
        start_time = time.time()

        try:
            system_prompt = (
                f"You are an expert {language} developer. Generate clean, efficient, "
                f"well-documented code following {language} best practices. "
                "Include appropriate error handling and comments."
            )

            user_message = f"Generate {language} code for:\n\n{description}"
            if context:
                user_message += (
                    f"\n\nContext/existing code:\n```{language}\n{context}\n```"
                )

            response, retries = self._execute_with_retry(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                max_tokens=4096,
                temperature=0.2,
                **kwargs,
            )

            execution_time = time.time() - start_time
            result_text = response.content[0].text if response.content else ""
            input_tokens = (
                response.usage.input_tokens
                if hasattr(response, "usage") and response.usage
                else 0
            )
            output_tokens = (
                response.usage.output_tokens
                if hasattr(response, "usage") and response.usage
                else 0
            )
            tokens_used = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Track totals
            self._total_tokens += tokens_used
            self._total_cost += cost

            # Extract code from response
            code = self._extract_code(result_text, language)

            logger.info(
                "Generated %s code in %.2fs ($%.6f)", language, execution_time, cost
            )

            return {
                "description": description,
                "language": language,
                "code": code,
                "raw_response": result_text,
                "model": self.model,
                "tokens_used": tokens_used,
                "cost_usd": cost,
                "execution_time": execution_time,
                "status": "success",
                "retries": retries,
            }

        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Error generating code: %s", e, exc_info=True)
            raise RuntimeError(f"Code generation failed: {e}") from None

    def _build_task_system_prompt(self) -> str:
        """Build system prompt for task execution."""
        return (
            "You are Claude Task Master, an AI assistant specialized in "
            "executing tasks efficiently and accurately. Provide clear, "
            "actionable results. Be thorough but concise. Structure your "
            "response for easy parsing when appropriate."
        )

    def _build_task_message(self, task: str, context: str | None) -> str:
        """Build task message with optional context."""
        if context:
            return f"Context: {context}\n\nTask: {task}"
        return f"Task: {task}"

    def _extract_code(self, response: str, language: str) -> str:
        """Extract code from markdown-formatted response."""
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
