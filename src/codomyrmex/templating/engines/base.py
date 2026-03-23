"""Base classes: TemplateContext and TemplateEngine ABC."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TemplateContext:
    """Context for template rendering."""

    data: dict[str, Any] = field(default_factory=dict)
    parent: Optional["TemplateContext"] = None

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from context, checking parent if not found."""
        if key in self.data:
            return self.data[key]
        if self.parent:
            return self.parent.get(key, default)
        return default

    def set(self, key: str, value: Any) -> None:
        """set a value in the context."""
        self.data[key] = value

    def child(self, **kwargs) -> "TemplateContext":
        """Create a child context."""
        return TemplateContext(data=kwargs, parent=self)

    def __getitem__(self, key: str) -> Any:
        """Return item at the given key."""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """set item at the given key."""
        self.set(key, value)


class TemplateEngine(ABC):
    """Abstract base class for template engines."""

    @abstractmethod
    def render(self, template: str, context: dict[str, Any]) -> str:
        """Render a template with the given context."""

    @abstractmethod
    def render_file(self, path: str, context: dict[str, Any]) -> str:
        """Render a template file."""
