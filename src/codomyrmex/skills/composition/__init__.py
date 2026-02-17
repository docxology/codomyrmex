"""
Skill Composition submodule.

Provides patterns for composing skills: chaining, parallel execution, and conditional branching.
"""

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class ComposedSkill:
    """A skill created by composing other skills."""

    def __init__(self, name: str, skills: list, mode: str = "chain"):
        """
        Initialize ComposedSkill.

        Args:
            name: Name for this composed skill
            skills: List of skills to compose
            mode: Composition mode ('chain' or 'parallel')
        """
        self.name = name
        self.skills = skills
        self.mode = mode

    def execute(self, **kwargs) -> Any:
        """Execute the composed skill."""
        if self.mode == "chain":
            result = self.skills[0].execute(**kwargs) if self.skills else None
            for skill in self.skills[1:]:
                result = skill.execute(input=result)
            return result
        elif self.mode == "parallel":
            results = {}
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(s.execute, **kwargs): getattr(
                        getattr(s, 'metadata', None), 'name', str(i)
                    )
                    for i, s in enumerate(self.skills)
                }
                for future in as_completed(futures):
                    name = futures[future]
                    results[name] = future.result()
            return results
        else:
            raise ValueError(f"Unknown composition mode: {self.mode}")


class ConditionalSkill:
    """A skill that branches based on a condition."""

    def __init__(self, condition: Callable[..., bool], if_skill, else_skill=None):
        """
        Initialize ConditionalSkill.

        Args:
            condition: Callable that returns True/False
            if_skill: Skill to execute if condition is True
            else_skill: Skill to execute if condition is False (optional)
        """
        self.condition = condition
        self.if_skill = if_skill
        self.else_skill = else_skill

    def execute(self, **kwargs) -> Any:
        """Execute the appropriate branch based on condition."""
        if self.condition(**kwargs):
            return self.if_skill.execute(**kwargs)
        elif self.else_skill is not None:
            return self.else_skill.execute(**kwargs)
        return None


class SkillComposer:
    """Composes skills into pipelines and workflows."""

    def chain(self, *skills) -> ComposedSkill:
        """
        Create a sequential skill chain.

        Each skill receives the output of the previous skill as input.

        Args:
            *skills: Skills to chain together

        Returns:
            A ComposedSkill that executes skills sequentially
        """
        names = [
            getattr(getattr(s, 'metadata', None), 'name', f'skill_{i}')
            for i, s in enumerate(skills)
        ]
        return ComposedSkill(
            name=f"chain({', '.join(names)})",
            skills=list(skills),
            mode="chain",
        )

    def parallel(self, *skills) -> ComposedSkill:
        """
        Create a parallel skill group.

        All skills execute concurrently with the same input.

        Args:
            *skills: Skills to execute in parallel

        Returns:
            A ComposedSkill that executes skills concurrently
        """
        names = [
            getattr(getattr(s, 'metadata', None), 'name', f'skill_{i}')
            for i, s in enumerate(skills)
        ]
        return ComposedSkill(
            name=f"parallel({', '.join(names)})",
            skills=list(skills),
            mode="parallel",
        )

    def conditional(self, condition: Callable[..., bool], if_skill, else_skill=None) -> ConditionalSkill:
        """
        Create a conditional skill that branches based on a condition.

        Args:
            condition: Callable that takes **kwargs and returns True/False
            if_skill: Skill to execute if condition is True
            else_skill: Skill to execute if condition is False (optional)

        Returns:
            A ConditionalSkill
        """
        return ConditionalSkill(condition, if_skill, else_skill)


__all__ = ["SkillComposer", "ComposedSkill", "ConditionalSkill"]
