"""
Prompt Template Management

Provides PromptTemplate dataclass and TemplateRegistry for managing,
storing, and rendering prompt templates with variable substitution.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

try:
    from codomyrmex.validation.schemas import Config, Result, ResultStatus
except ImportError:
    Config = None
    Result = None
    ResultStatus = None


@dataclass
class PromptTemplate:
    """
    A reusable prompt template with variable placeholders.

    Variables in the template_str are denoted by {variable_name} syntax.
    The variables list declares expected variables for validation.
    """

    name: str
    template_str: str
    variables: list[str] = field(default_factory=list)
    version: str = "1.0.0"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Auto-detect variables from template string if not provided."""
        if not self.variables:
            self.variables = self._extract_variables()

    def _extract_variables(self) -> list[str]:
        """Extract variable names from template string using {var} syntax."""
        pattern = r"\{(\w+)\}"
        return sorted(set(re.findall(pattern, self.template_str)))

    def render(self, **kwargs: Any) -> str:
        """
        Render the template with provided variable values.

        Args:
            **kwargs: Variable name-value pairs for substitution.

        Returns:
            Rendered prompt string.

        Raises:
            KeyError: If a required variable is missing.
        """
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            raise KeyError(
                f"Missing required variables for template '{self.name}': {missing}"
            )
        result = self.template_str
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def validate(self, **kwargs: Any) -> list[str]:
        """
        Validate that all required variables are provided.

        Returns:
            List of missing variable names (empty if all present).
        """
        return [v for v in self.variables if v not in kwargs]

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary representation."""
        return {
            "name": self.name,
            "template_str": self.template_str,
            "variables": self.variables,
            "version": self.version,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PromptTemplate:
        """Create a PromptTemplate from a dictionary."""
        return cls(
            name=data["name"],
            template_str=data["template_str"],
            variables=data.get("variables", []),
            version=data.get("version", "1.0.0"),
            metadata=data.get("metadata", {}),
        )


class TemplateRegistry:
    """
    Registry for managing a collection of prompt templates.

    Supports adding, retrieving, listing, removing, and rendering templates
    by name. Optionally integrates with codomyrmex Config for persistence
    settings.
    """

    def __init__(self, config: Any | None = None) -> None:
        """
        Initialize the registry.

        Args:
            config: Optional Config instance for registry settings.
        """
        self._templates: dict[str, PromptTemplate] = {}
        self._config = config

    @property
    def size(self) -> int:
        """Return the number of registered templates."""
        return len(self._templates)

    def add(self, template: PromptTemplate) -> None:
        """
        Register a template in the registry.

        Args:
            template: The PromptTemplate to register.

        Raises:
            ValueError: If a template with the same name already exists.
        """
        if template.name in self._templates:
            raise ValueError(
                f"Template '{template.name}' already exists. "
                "Use update() to replace it."
            )
        self._templates[template.name] = template

    def update(self, template: PromptTemplate) -> None:
        """
        Add or replace a template in the registry.

        Args:
            template: The PromptTemplate to add or replace.
        """
        self._templates[template.name] = template

    def get(self, name: str) -> PromptTemplate:
        """
        Retrieve a template by name.

        Args:
            name: The template name.

        Returns:
            The matching PromptTemplate.

        Raises:
            KeyError: If no template with that name exists.
        """
        if name not in self._templates:
            raise KeyError(f"Template '{name}' not found in registry.")
        return self._templates[name]

    def remove(self, name: str) -> PromptTemplate:
        """
        Remove and return a template from the registry.

        Args:
            name: The template name to remove.

        Returns:
            The removed PromptTemplate.

        Raises:
            KeyError: If no template with that name exists.
        """
        if name not in self._templates:
            raise KeyError(f"Template '{name}' not found in registry.")
        return self._templates.pop(name)

    def list(self) -> list[str]:
        """
        List all registered template names.

        Returns:
            Sorted list of template names.
        """
        return sorted(self._templates.keys())

    def list_templates(self) -> list[PromptTemplate]:
        """
        List all registered templates.

        Returns:
            List of PromptTemplate objects sorted by name.
        """
        return [self._templates[name] for name in sorted(self._templates.keys())]

    def render(self, template_name: str, /, **kwargs: Any) -> str:
        """
        Render a template by name with the given variables.

        Args:
            template_name: The template name (positional-only to avoid
                           conflicts with template variable names).
            **kwargs: Variable name-value pairs for substitution.

        Returns:
            The rendered prompt string.
        """
        template = self.get(template_name)
        return template.render(**kwargs)

    def search(self, query: str) -> list[PromptTemplate]:
        """
        Search templates by name or metadata keyword.

        Args:
            query: Search term to match against template names and metadata.

        Returns:
            List of matching PromptTemplate objects.
        """
        query_lower = query.lower()
        results = []
        for template in self._templates.values():
            if query_lower in template.name.lower():
                results.append(template)
                continue
            if any(
                query_lower in str(v).lower()
                for v in template.metadata.values()
            ):
                results.append(template)
        return sorted(results, key=lambda t: t.name)

    def export_all(self) -> list[dict[str, Any]]:
        """
        Export all templates as a list of dictionaries.

        Returns:
            List of template dictionaries.
        """
        return [t.to_dict() for t in self.list_templates()]

    def import_all(self, data: list[dict[str, Any]], overwrite: bool = False) -> int:
        """
        Import templates from a list of dictionaries.

        Args:
            data: List of template dictionaries.
            overwrite: If True, overwrite existing templates.

        Returns:
            Number of templates imported.
        """
        count = 0
        for item in data:
            template = PromptTemplate.from_dict(item)
            if overwrite or template.name not in self._templates:
                self._templates[template.name] = template
                count += 1
        return count


# Module-level convenience registry
_default_registry = TemplateRegistry()


def get_default_registry() -> TemplateRegistry:
    """Get the module-level default template registry."""
    return _default_registry


__all__ = [
    "PromptTemplate",
    "TemplateRegistry",
    "get_default_registry",
]
