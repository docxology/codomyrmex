"""
Skill Execution submodule.

Provides runtime execution of skills with error handling, timeouts, and chaining.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from typing import Any

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class SkillExecutionError(Exception):
    """Raised when skill execution fails."""
    pass


class SkillExecutor:
    """Executes skills with error handling, timeouts, and chaining."""

    def __init__(self, max_workers: int = 4):
        """
        Initialize SkillExecutor.

        Args:
            max_workers: Maximum number of concurrent workers for parallel execution
        """
        self.max_workers = max_workers
        self._execution_log: list[dict[str, Any]] = []

    def execute(self, skill, **kwargs) -> Any:
        """
        Execute a skill with error handling and logging.

        Args:
            skill: A Skill instance (must have an `execute` method)
            **kwargs: Parameters to pass to the skill

        Returns:
            The skill's return value

        Raises:
            SkillExecutionError: If execution fails
        """
        skill_name = getattr(getattr(skill, 'metadata', None), 'name', str(skill))
        logger.info(f"Executing skill: {skill_name}")
        start_time = time.monotonic()

        try:
            errors = skill.validate_params(**kwargs) if hasattr(skill, 'validate_params') else []
            if errors:
                raise SkillExecutionError(f"Parameter validation failed: {', '.join(errors)}")

            result = skill.execute(**kwargs)
            elapsed = time.monotonic() - start_time

            self._execution_log.append({
                "skill": skill_name,
                "status": "success",
                "elapsed": elapsed,
            })
            logger.info(f"Skill {skill_name} completed in {elapsed:.3f}s")
            return result

        except SkillExecutionError:
            raise
        except Exception as e:
            elapsed = time.monotonic() - start_time
            self._execution_log.append({
                "skill": skill_name,
                "status": "error",
                "elapsed": elapsed,
                "error": str(e),
            })
            raise SkillExecutionError(f"Skill {skill_name} failed: {e}") from e

    def execute_with_timeout(self, skill, timeout: float, **kwargs) -> Any:
        """
        Execute a skill with a timeout.

        Args:
            skill: A Skill instance
            timeout: Maximum execution time in seconds
            **kwargs: Parameters to pass to the skill

        Returns:
            The skill's return value

        Raises:
            SkillExecutionError: If execution fails or times out
        """
        skill_name = getattr(getattr(skill, 'metadata', None), 'name', str(skill))

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.execute, skill, **kwargs)
            try:
                return future.result(timeout=timeout)
            except FuturesTimeoutError as err:
                raise SkillExecutionError(
                    f"Skill {skill_name} timed out after {timeout}s"
                ) from err

    def execute_chain(self, skills: list, **kwargs) -> Any:
        """
        Execute a chain of skills sequentially, passing each result to the next.

        The first skill receives **kwargs. Subsequent skills receive the previous
        result as the `input` keyword argument.

        Args:
            skills: List of Skill instances to execute in order
            **kwargs: Initial parameters for the first skill

        Returns:
            The result of the last skill in the chain

        Raises:
            SkillExecutionError: If any skill in the chain fails
        """
        if not skills:
            raise SkillExecutionError("Cannot execute empty skill chain")

        result = self.execute(skills[0], **kwargs)

        for skill in skills[1:]:
            result = self.execute(skill, input=result)

        return result

    def get_execution_log(self) -> list[dict[str, Any]]:
        """Get the execution log."""
        return list(self._execution_log)

    def clear_log(self) -> None:
        """Clear the execution log."""
        self._execution_log.clear()


__all__ = ["SkillExecutor", "SkillExecutionError"]
