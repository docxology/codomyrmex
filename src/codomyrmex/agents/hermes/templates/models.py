"""Prompt template data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PromptTemplate:
    """A reusable prompt template for the Hermes agent.

    Attributes:
        name: Unique template name.
        system_prompt: System message for the LLM.
        user_template: User message template with ``{variable}`` placeholders.
        variables: list of variable names used in the template.
        metadata: Optional metadata.
    """

    name: str
    system_prompt: str = ""
    user_template: str = ""
    variables: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self, **kwargs: str) -> str:
        """Render the user template with variable substitutions.

        Args:
            **kwargs: Variable values to substitute.

        Returns:
            The rendered prompt string.

        Raises:
            KeyError: If a required variable is missing.
        """
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            msg = f"Missing template variables: {missing}"
            raise KeyError(msg)

        return self.user_template.format(**kwargs)

    def render_safe(self, **kwargs: str) -> str:
        """Render the template, replacing missing variables with placeholders.

        Args:
            **kwargs: Variable values to substitute.

        Returns:
            The rendered prompt string with ``{var}`` for missing values.
        """
        safe_kwargs = {v: kwargs.get(v, f"{{{v}}}") for v in self.variables}
        return self.user_template.format(**safe_kwargs)


__all__ = ["PromptTemplate"]
