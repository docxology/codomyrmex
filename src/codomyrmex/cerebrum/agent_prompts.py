"""Dynamic prompt selection for agent reasoning.

Selects and renders the most appropriate prompt template based on
the current task context, using the ``TemplateRegistry`` for prompt
management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.prompt_engineering.templates import (
    PromptTemplate,
    TemplateRegistry,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# ── Built-in agent prompt templates ──────────────────────────────

_BUILTIN_TEMPLATES: list[dict[str, Any]] = [
    {
        "name": "code_review",
        "template_str": (
            "Review the following {language} code for quality issues:\n\n"
            "```{language}\n{code}\n```\n\n"
            "Focus on: {focus_areas}\n"
            "Provide specific, actionable feedback."
        ),
        "metadata": {"category": "review", "priority": 1},
    },
    {
        "name": "anti_pattern_analysis",
        "template_str": (
            "Analyze this code for anti-patterns and code smells:\n\n"
            "```{language}\n{code}\n```\n\n"
            "Report: pattern name, severity, location, and fix."
        ),
        "metadata": {"category": "analysis", "priority": 2},
    },
    {
        "name": "refactoring_plan",
        "template_str": (
            "Create a refactoring plan for:\n\n"
            "```{language}\n{code}\n```\n\n"
            "Current issues: {issues}\n"
            "Constraints: {constraints}\n"
            "Generate step-by-step plan with risk assessment."
        ),
        "metadata": {"category": "planning", "priority": 2},
    },
    {
        "name": "drift_report",
        "template_str": (
            "Analyze the concept drift between versions:\n\n"
            "Shifted concepts: {shifted}\n"
            "New concepts: {new_concepts}\n"
            "Lost concepts: {lost}\n\n"
            "Drift magnitude: {magnitude}\n\n"
            "Provide impact assessment and migration guidance."
        ),
        "metadata": {"category": "analysis", "priority": 3},
    },
    {
        "name": "reasoning_chain",
        "template_str": (
            "Problem: {problem}\n\n"
            "Think step by step:\n"
            "1. What are the key observations?\n"
            "2. What hypotheses can we form?\n"
            "3. What evidence supports/refutes each?\n"
            "4. What is the most likely conclusion?\n\n"
            "Context: {context}"
        ),
        "metadata": {"category": "reasoning", "priority": 1},
    },
]


@dataclass
class PromptSelection:
    """Result of dynamic prompt selection.

    Attributes:
        template: The selected prompt template.
        rendered: The rendered prompt string.
        score: Relevance score (0-1).
        reason: Why this template was selected.
    """

    template: PromptTemplate
    rendered: str
    score: float = 1.0
    reason: str = ""


class AgentPromptSelector:
    """Select and render prompts dynamically based on task context.

    Maintains a registry of prompt templates and selects the best
    match based on category and keyword relevance.

    Usage::

        selector = AgentPromptSelector()
        selection = selector.select(
            task="review",
            variables={"language": "python", "code": "...", "focus_areas": "security"},
        )
        print(selection.rendered)
    """

    def __init__(
        self,
        registry: TemplateRegistry | None = None,
        load_builtins: bool = True,
    ) -> None:
        """Initialize the selector.

        Args:
            registry: Optional external registry. Creates one if not provided.
            load_builtins: Whether to load built-in agent templates.
        """
        self._registry = registry or TemplateRegistry()
        if load_builtins:
            self._load_builtins()

    def _load_builtins(self) -> None:
        """Load built-in prompt templates."""
        for tpl_data in _BUILTIN_TEMPLATES:
            tpl = PromptTemplate.from_dict(tpl_data)
            try:
                self._registry.add(tpl)
            except ValueError:
                pass  # Already exists

    @property
    def registry(self) -> TemplateRegistry:
        """Access the underlying template registry."""
        return self._registry

    def select(
        self,
        task: str,
        variables: dict[str, Any] | None = None,
        category: str | None = None,
    ) -> PromptSelection:
        """Select the best prompt template for a task.

        Searches the registry by task keywords and optional category
        filter. Returns the highest-scoring match, rendered with
        provided variables.

        Args:
            task: Task description or keyword.
            variables: Template variable values.
            category: Optional category filter.

        Returns:
            ``PromptSelection`` with selected and rendered template.
        """
        vars_ = variables or {}
        # Normalize query to match underscore-separated template names
        normalized_task = task.replace(" ", "_")
        candidates = self._registry.search(task)
        # Also search with underscore variant
        if not candidates:
            candidates = self._registry.search(normalized_task)

        if category:
            candidates = [
                t for t in candidates
                if t.metadata.get("category") == category
            ]

        if not candidates:
            # Fallback: use reasoning_chain for any unmatched task
            try:
                fallback = self._registry.get("reasoning_chain")
                candidates = [fallback]
            except KeyError:
                # Nothing available — return a bare prompt
                return PromptSelection(
                    template=PromptTemplate(name="_bare", template_str=task),
                    rendered=task,
                    score=0.0,
                    reason="No matching templates found",
                )

        # Score by keyword overlap + priority
        best = candidates[0]
        best_score = 0.0

        task_words = set(task.lower().split())
        for tpl in candidates:
            name_words = set(tpl.name.replace("_", " ").split())
            overlap = len(task_words & name_words)
            priority = tpl.metadata.get("priority", 5)
            score = overlap / max(len(task_words), 1) + (1.0 / priority)
            if score > best_score:
                best_score = score
                best = tpl

        # Render with available variables (ignore missing with defaults)
        try:
            rendered = best.render(**vars_)
        except (KeyError, IndexError):
            rendered = best.template_str

        selection = PromptSelection(
            template=best,
            rendered=rendered,
            score=min(best_score, 1.0),
            reason=f"Matched '{best.name}' by keyword relevance",
        )

        logger.info(
            "Prompt selected",
            extra={
                "template": best.name,
                "score": round(selection.score, 3),
                "task": task[:50],
            },
        )

        return selection

    def list_templates(self) -> list[str]:
        """List available template names."""
        return self._registry.list()


__all__ = [
    "AgentPromptSelector",
    "PromptSelection",
]
