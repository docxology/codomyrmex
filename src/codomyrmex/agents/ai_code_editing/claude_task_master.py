"""Claude Task Master Integration Module.

This module provides integration with Anthropic's Claude API for
advanced AI-powered task orchestration, code generation, and
task decomposition capabilities.

Features:
- Task execution with automatic retry logic
- Task decomposition into subtasks
- Task analysis for complexity and requirements
- Workflow planning with constraints
- Cost estimation and tracking
- Streaming support for long-running tasks

Reference: https://docs.anthropic.com/claude/docs
"""

import os
import random
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from collections.abc import Iterator

from anthropic import Anthropic

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

# Default configuration - using latest models
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_TEMPERATURE = 0.3
MAX_TOKENS = 4096

# Cost per 1M tokens (update as pricing changes)
TASK_MASTER_PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku-20241022": {"input": 1.00, "output": 5.00},
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
}


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task definition for Claude Task Master."""
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    context: str | None = None
    dependencies: list[str] = field(default_factory=list)
    timeout: float | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    status: TaskStatus
    result: Any
    execution_time: float
    tokens_used: int
    cost_usd: float = 0.0
    error: str | None = None
    retries: int = 0


class ClaudeTaskMaster:
    """Claude Task Master for AI-powered task orchestration.

    A comprehensive task orchestration system that uses Claude for:
    - Executing complex tasks with automatic retries
    - Decomposing tasks into manageable subtasks
    - Analyzing task requirements and complexity
    - Planning multi-step workflows

    Example:
        ```python
        master = ClaudeTaskMaster()

        # Execute a task
        result = master.execute_task(
            "Generate a Python function for binary search",
            context="The function should work with sorted lists"
        )

        # Decompose a complex task
        subtasks = master.decompose_task(
            "Build a REST API for user management"
        )
        ```
    """

    # Retry configuration
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_INITIAL_DELAY = 1.0
    DEFAULT_BACKOFF_FACTOR = 2.0

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        """Initialize Claude Task Master integration.

        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
            model: Model to use (defaults to claude-sonnet-4-20250514)
            max_retries: Maximum retry attempts for failed requests

        Raises:
            ValueError: If no API key is available
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model or DEFAULT_MODEL
        self.max_retries = max_retries
        self._client: Anthropic | None = None
        self._task_counter = 0
        self._total_cost = 0.0
        self._total_tokens = 0

        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set - Task Master operations will fail")

    def _get_client(self) -> Anthropic:
        """Lazily initialize Anthropic client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")

            try:
                self._client = Anthropic(api_key=self.api_key)
            except ImportError as e:
                raise ImportError(
                    "Anthropic package not installed. Install with: pip install anthropic"
                ) from e
        return self._client

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD based on token usage."""
        pricing = TASK_MASTER_PRICING.get(self.model, {"input": 3.00, "output": 15.00})
        cost = (input_tokens / 1_000_000 * pricing["input"]) + (
            output_tokens / 1_000_000 * pricing["output"]
        )
        return round(cost, 6)

    def _execute_with_retry(
        self,
        messages: list[dict],
        system: str,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any
    ) -> tuple[Any, int]:
        """Execute API call with retry logic.

        Args:
            messages: Messages to send
            system: System prompt
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            **kwargs: Additional API arguments

        Returns:
            Tuple of (response, retry_count)
        """
        client = self._get_client()

        for attempt in range(self.max_retries + 1):
            try:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=messages,
                    **kwargs
                )
                return response, attempt
            except Exception as e:
                error_str = str(e).lower()
                is_retryable = (
                    "rate_limit" in error_str or
                    "overloaded" in error_str or
                    "503" in error_str or
                    "529" in error_str or
                    "timeout" in error_str
                )

                if not is_retryable or attempt >= self.max_retries:
                    raise

                delay = self.DEFAULT_INITIAL_DELAY * (self.DEFAULT_BACKOFF_FACTOR ** attempt)
                delay *= (0.75 + random.random() * 0.5)  # Add jitter

                logger.warning(
                    f"Retryable error, attempt {attempt + 1}/{self.max_retries + 1}, "
                    f"retrying in {delay:.1f}s: {e}"
                )
                time.sleep(delay)

        raise RuntimeError("Max retries exceeded")

    def execute_task(
        self,
        task: str,
        context: str | None = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any
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
                **kwargs
            )

            execution_time = time.time() - start_time
            result_text = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0
            tokens_used = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Track totals
            self._total_tokens += tokens_used
            self._total_cost += cost

            logger.info(
                f"Executed task {task_id} using {self.model} "
                f"in {execution_time:.2f}s ({tokens_used} tokens, ${cost:.6f})"
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
            logger.error(f"Anthropic import error: {e}")
            raise
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise RuntimeError(f"Task execution failed: {e}") from None
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing task: {e}", exc_info=True)
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
        self,
        task: str,
        context: str | None = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        **kwargs: Any
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
                **kwargs
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"Error: {str(e)}"

    def decompose_task(
        self,
        task: str,
        max_subtasks: int = 10,
        context: str | None = None,
        include_dependencies: bool = False,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Decompose a complex task into subtasks.

        Args:
            task: Complex task to decompose
            max_subtasks: Maximum number of subtasks
            context: Additional context
            include_dependencies: Whether to include dependency analysis
            **kwargs: Additional arguments

        Returns:
            Dictionary containing subtasks and metadata
        """
        start_time = time.time()

        try:
            system_prompt = (
                "You are a task decomposition expert. Break down complex tasks "
                "into clear, actionable subtasks. Each subtask should be specific, "
                "measurable, and achievable independently where possible."
            )

            if include_dependencies:
                system_prompt += (
                    "\n\nFor each subtask, also identify any dependencies on other subtasks. "
                    "Format dependencies as: [Depends on: subtask numbers]"
                )

            system_prompt += "\n\nFormat your response as a numbered list of subtasks."

            user_message = f"Decompose this task into at most {max_subtasks} subtasks:\n\n{task}"
            if context:
                user_message += f"\n\nContext: {context}"

            response, retries = self._execute_with_retry(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                max_tokens=2048,
                temperature=0.2,
                **kwargs
            )

            execution_time = time.time() - start_time
            result_text = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0
            tokens_used = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Track totals
            self._total_tokens += tokens_used
            self._total_cost += cost

            subtasks = self._parse_subtasks(result_text, include_dependencies)

            logger.info(
                f"Decomposed task into {len(subtasks)} subtasks "
                f"in {execution_time:.2f}s (${cost:.6f})"
            )

            return {
                "original_task": task,
                "subtasks": subtasks,
                "raw_response": result_text,
                "model": self.model,
                "tokens_used": tokens_used,
                "cost_usd": cost,
                "execution_time": execution_time,
                "status": "success",
                "retries": retries,
            }

        except Exception as e:
            logger.error(f"Error decomposing task: {e}", exc_info=True)
            raise RuntimeError(f"Task decomposition failed: {e}") from None

    def analyze_task(
        self,
        task: str,
        context: str | None = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Analyze a task for complexity, requirements, and approach.

        Args:
            task: Task to analyze
            context: Additional context
            **kwargs: Additional arguments

        Returns:
            Dictionary containing task analysis
        """
        start_time = time.time()

        try:
            system_prompt = (
                "You are a project planning expert. Analyze the given task and provide:\n"
                "1. Complexity assessment (low/medium/high)\n"
                "2. Estimated effort (hours/days)\n"
                "3. Required skills or resources\n"
                "4. Potential risks or challenges\n"
                "5. Recommended approach\n"
                "6. Success criteria"
            )

            user_message = f"Analyze this task:\n\n{task}"
            if context:
                user_message += f"\n\nContext: {context}"

            response, retries = self._execute_with_retry(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                max_tokens=2048,
                temperature=0.2,
                **kwargs
            )

            execution_time = time.time() - start_time
            analysis = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0
            tokens_used = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Track totals
            self._total_tokens += tokens_used
            self._total_cost += cost

            # Parse structured analysis
            parsed = self._parse_analysis(analysis)

            logger.info(
                f"Analyzed task in {execution_time:.2f}s ({tokens_used} tokens, ${cost:.6f})"
            )

            return {
                "task": task,
                "analysis": analysis,
                "parsed": parsed,
                "model": self.model,
                "tokens_used": tokens_used,
                "cost_usd": cost,
                "execution_time": execution_time,
                "status": "success",
                "retries": retries,
            }

        except Exception as e:
            logger.error(f"Error analyzing task: {e}", exc_info=True)
            raise RuntimeError(f"Task analysis failed: {e}") from None

    def plan_workflow(
        self,
        goal: str,
        constraints: list[str] | None = None,
        context: str | None = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Create a workflow plan to achieve a goal.

        Args:
            goal: The goal to achieve
            constraints: List of constraints
            context: Additional context
            **kwargs: Additional arguments

        Returns:
            Dictionary containing workflow plan
        """
        start_time = time.time()

        try:
            system_prompt = (
                "You are a workflow planning expert. Create a detailed workflow "
                "plan with clear phases, steps, dependencies, and milestones. "
                "Structure the plan with:\n"
                "1. Overview\n"
                "2. Prerequisites\n"
                "3. Phases with steps\n"
                "4. Milestones and checkpoints\n"
                "5. Risk mitigation strategies"
            )

            user_message = f"Create a workflow plan to achieve:\n\n{goal}"
            if constraints:
                user_message += "\n\nConstraints:\n" + "\n".join(f"- {c}" for c in constraints)
            if context:
                user_message += f"\n\nContext: {context}"

            response, retries = self._execute_with_retry(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                max_tokens=4096,
                temperature=0.3,
                **kwargs
            )

            execution_time = time.time() - start_time
            plan = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0
            tokens_used = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Track totals
            self._total_tokens += tokens_used
            self._total_cost += cost

            logger.info(
                f"Created workflow plan in {execution_time:.2f}s ({tokens_used} tokens, ${cost:.6f})"
            )

            return {
                "goal": goal,
                "constraints": constraints or [],
                "plan": plan,
                "model": self.model,
                "tokens_used": tokens_used,
                "cost_usd": cost,
                "execution_time": execution_time,
                "status": "success",
                "retries": retries,
            }

        except Exception as e:
            logger.error(f"Error planning workflow: {e}", exc_info=True)
            raise RuntimeError(f"Workflow planning failed: {e}") from None

    def generate_code(
        self,
        description: str,
        language: str = "python",
        context: str | None = None,
        **kwargs: Any
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
                user_message += f"\n\nContext/existing code:\n```{language}\n{context}\n```"

            response, retries = self._execute_with_retry(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                max_tokens=4096,
                temperature=0.2,
                **kwargs
            )

            execution_time = time.time() - start_time
            result_text = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0
            tokens_used = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Track totals
            self._total_tokens += tokens_used
            self._total_cost += cost

            # Extract code from response
            code = self._extract_code(result_text, language)

            logger.info(
                f"Generated {language} code in {execution_time:.2f}s (${cost:.6f})"
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

        except Exception as e:
            logger.error(f"Error generating code: {e}", exc_info=True)
            raise RuntimeError(f"Code generation failed: {e}") from None

    def get_usage_stats(self) -> dict[str, Any]:
        """Get cumulative usage statistics.

        Returns:
            Dictionary with total tokens, cost, and task count
        """
        return {
            "total_tasks": self._task_counter,
            "total_tokens": self._total_tokens,
            "total_cost_usd": round(self._total_cost, 6),
            "model": self.model,
        }

    def reset_usage_stats(self) -> None:
        """Reset cumulative usage statistics."""
        self._task_counter = 0
        self._total_tokens = 0
        self._total_cost = 0.0

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

    def _parse_subtasks(
        self,
        response: str,
        include_dependencies: bool = False
    ) -> list[dict[str, Any]]:
        """Parse subtasks from Claude's response."""
        subtasks = []
        lines = response.strip().split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            # Match numbered items: 1. Task, 1) Task, - Task, * Task
            match = re.match(r'^(?:(\d+)[\.\)]\s*|[-*]\s*)(.+)$', line)
            if match:
                number = match.group(1)
                task_text = match.group(2).strip()
                if task_text:
                    subtask: dict[str, Any] = {
                        "id": int(number) if number else i + 1,
                        "description": task_text,
                        "status": "pending",
                    }

                    if include_dependencies:
                        dep_match = re.search(r'\[Depends on:\s*([^\]]+)\]', task_text, re.IGNORECASE)
                        if dep_match:
                            deps = [d.strip() for d in dep_match.group(1).split(',')]
                            subtask["dependencies"] = deps
                            subtask["description"] = re.sub(
                                r'\s*\[Depends on:[^\]]+\]', '', task_text
                            ).strip()

                    subtasks.append(subtask)

        return subtasks

    def _parse_analysis(self, analysis: str) -> dict[str, Any]:
        """Parse structured analysis output."""
        parsed: dict[str, Any] = {
            "complexity": None,
            "effort": None,
            "skills": [],
            "risks": [],
            "approach": None,
        }

        lines = analysis.lower()

        # Extract complexity
        if "high" in lines and "complexity" in lines:
            parsed["complexity"] = "high"
        elif "medium" in lines and "complexity" in lines:
            parsed["complexity"] = "medium"
        elif "low" in lines and "complexity" in lines:
            parsed["complexity"] = "low"

        return parsed

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

    def is_available(self) -> bool:
        """Check if Claude Task Master is available and configured."""
        if not self.api_key:
            return False

        try:
            self._get_client()
            return True
        except (ImportError, ValueError):
            return False


# Module-level convenience functions

def execute_task(task: str, **kwargs: Any) -> dict[str, Any]:
    """Execute a task using Claude (module-level convenience function)."""
    master = ClaudeTaskMaster()
    return master.execute_task(task, **kwargs)


def decompose_task(task: str, **kwargs: Any) -> dict[str, Any]:
    """Decompose a task into subtasks."""
    master = ClaudeTaskMaster()
    return master.decompose_task(task, **kwargs)


def analyze_task(task: str, **kwargs: Any) -> dict[str, Any]:
    """Analyze a task."""
    master = ClaudeTaskMaster()
    return master.analyze_task(task, **kwargs)


def plan_workflow(goal: str, **kwargs: Any) -> dict[str, Any]:
    """Create a workflow plan."""
    master = ClaudeTaskMaster()
    return master.plan_workflow(goal, **kwargs)


def generate_code(description: str, language: str = "python", **kwargs: Any) -> dict[str, Any]:
    """Generate code from description."""
    master = ClaudeTaskMaster()
    return master.generate_code(description, language, **kwargs)
