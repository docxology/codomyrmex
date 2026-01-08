from typing import Any, Optional
import os
import re
import time

from anthropic import Anthropic
from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.logging_monitoring.logger_config import get_logger




























































"""Claude Task Master Integration Module.

"""Core functionality module

This module provides claude_task_master functionality including:
- 14 functions: execute_task, decompose_task, analyze_task...
- 5 classes: TaskPriority, TaskStatus, Task...

Usage:
    # Example usage here
"""
This module provides integration with Anthropic's Claude API for
advanced AI-powered task orchestration, code generation, and
task decomposition capabilities.

Reference: https://docs.anthropic.com/claude/docs
"""



logger = get_logger(__name__)

# Default configuration
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_TEMPERATURE = 0.3
MAX_TOKENS = 4096


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
    context: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    timeout: Optional[float] = None


@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    status: TaskStatus
    result: Any
    execution_time: float
    tokens_used: int
    error: Optional[str] = None


class ClaudeTaskMaster:
    """Claude Task Master for AI-powered task orchestration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Initialize Claude Task Master integration.

        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
            model: Model to use (defaults to claude-3-5-sonnet)

        Raises:
            ValueError: If no API key is available
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model or DEFAULT_MODEL
        self._client = None
        self._task_counter = 0

        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set - Task Master operations will fail")

    def _get_client(self):
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

    def execute_task(
        self,
        task: str,
        context: Optional[str] = None,
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
            client = self._get_client()

            # Build the system prompt
            system_prompt = self._build_task_system_prompt()

            # Build the user message
            user_message = self._build_task_message(task, context)

            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                **kwargs
            )

            execution_time = time.time() - start_time
            result_text = response.content[0].text if response.content else ""
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage else 0
            )

            logger.info(
                f"Executed task {task_id} using {self.model} "
                f"in {execution_time:.2f}s ({tokens_used} tokens)"
            )

            return {
                "task_id": task_id,
                "task": task,
                "result": result_text,
                "status": "completed",
                "model": self.model,
                "tokens_used": tokens_used,
                "execution_time": execution_time
            }

        except ImportError as e:
            logger.error(f"Anthropic import error: {e}")
            raise
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise RuntimeError(f"Task execution failed: {e}") from None
        except Exception as e:
            logger.error(f"Error executing task: {e}", exc_info=True)
            return {
                "task_id": task_id,
                "task": task,
                "result": None,
                "status": "failed",
                "error": str(e),
                "model": self.model,
                "tokens_used": 0,
                "execution_time": time.time() - start_time
            }

    def decompose_task(
        self,
        task: str,
        max_subtasks: int = 10,
        context: Optional[str] = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Decompose a complex task into subtasks.

        Args:
            task: Complex task to decompose
            max_subtasks: Maximum number of subtasks
            context: Additional context
            **kwargs: Additional arguments

        Returns:
            Dictionary containing subtasks and metadata
        """
        start_time = time.time()

        try:
            client = self._get_client()

            system_prompt = (
                "You are a task decomposition expert. Break down complex tasks "
                "into clear, actionable subtasks. Each subtask should be specific, "
                "measurable, and achievable independently where possible. "
                "Format your response as a numbered list of subtasks."
            )

            user_message = f"Decompose this task into at most {max_subtasks} subtasks:\n\n{task}"
            if context:
                user_message += f"\n\nContext: {context}"

            response = client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                **kwargs
            )

            execution_time = time.time() - start_time
            result_text = response.content[0].text if response.content else ""
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage else 0
            )

            # Parse subtasks from response
            subtasks = self._parse_subtasks(result_text)

            logger.info(
                f"Decomposed task into {len(subtasks)} subtasks "
                f"in {execution_time:.2f}s"
            )

            return {
                "original_task": task,
                "subtasks": subtasks,
                "raw_response": result_text,
                "model": self.model,
                "tokens_used": tokens_used,
                "execution_time": execution_time,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error decomposing task: {e}", exc_info=True)
            raise RuntimeError(f"Task decomposition failed: {e}") from None

    def analyze_task(
        self,
        task: str,
        context: Optional[str] = None,
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
            client = self._get_client()

            system_prompt = (
                "You are a project planning expert. Analyze the given task and provide:\n"
                "1. Complexity assessment (low/medium/high)\n"
                "2. Estimated effort\n"
                "3. Required skills or resources\n"
                "4. Potential risks or challenges\n"
                "5. Recommended approach"
            )

            user_message = f"Analyze this task:\n\n{task}"
            if context:
                user_message += f"\n\nContext: {context}"

            response = client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                **kwargs
            )

            execution_time = time.time() - start_time
            analysis = response.content[0].text if response.content else ""
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage else 0
            )

            logger.info(
                f"Analyzed task in {execution_time:.2f}s ({tokens_used} tokens)"
            )

            return {
                "task": task,
                "analysis": analysis,
                "model": self.model,
                "tokens_used": tokens_used,
                "execution_time": execution_time,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error analyzing task: {e}", exc_info=True)
            raise RuntimeError(f"Task analysis failed: {e}") from None

    def plan_workflow(
        self,
        goal: str,
        constraints: Optional[list[str]] = None,
        context: Optional[str] = None,
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
            client = self._get_client()

            system_prompt = (
                "You are a workflow planning expert. Create a detailed workflow "
                "plan with clear steps, dependencies, and milestones. "
                "Structure the plan with phases and actionable items."
            )

            user_message = f"Create a workflow plan to achieve:\n\n{goal}"
            if constraints:
                user_message += "\n\nConstraints:\n" + "\n".join(f"- {c}" for c in constraints)
            if context:
                user_message += f"\n\nContext: {context}"

            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                **kwargs
            )

            execution_time = time.time() - start_time
            plan = response.content[0].text if response.content else ""
            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens
                if response.usage else 0
            )

            logger.info(
                f"Created workflow plan in {execution_time:.2f}s ({tokens_used} tokens)"
            )

            return {
                "goal": goal,
                "constraints": constraints or [],
                "plan": plan,
                "model": self.model,
                "tokens_used": tokens_used,
                "execution_time": execution_time,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error planning workflow: {e}", exc_info=True)
            raise RuntimeError(f"Workflow planning failed: {e}") from None

    def _build_task_system_prompt(self) -> str:
        """Build system prompt for task execution."""
        return (
            "You are Claude Task Master, an AI assistant specialized in "
            "executing tasks efficiently and accurately. Provide clear, "
            "actionable results. Be thorough but concise."
        )

    def _build_task_message(self, task: str, context: Optional[str]) -> str:
        """Build task message with optional context."""
        if context:
            return f"Context: {context}\n\nTask: {task}"
        return f"Task: {task}"

    def _parse_subtasks(self, response: str) -> list[dict[str, str]]:
        """Parse subtasks from Claude's response."""

        subtasks = []
        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()
            # Match numbered items: 1. Task, 1) Task, - Task, * Task
            match = re.match(r'^(?:\d+[\.\)]\s*|[-*]\s*)(.+)$', line)
            if match:
                task_text = match.group(1).strip()
                if task_text:
                    subtasks.append({
                        "description": task_text,
                        "status": "pending"
                    })

        return subtasks

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
