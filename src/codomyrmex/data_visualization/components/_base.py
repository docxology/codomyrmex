"""Base class for all UI components."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BaseComponent:
    """Base class for all visualization components.

    Attributes:
        css_class: Additional CSS class(es) for the outer element.
        style: Inline style dict ``{property: value}``.
    """
    css_class: str = ""
    style: dict[str, str] = field(default_factory=dict)

    def render(self) -> str:
        """Render the component as an HTML string."""
        return f'<div class="{self.css_class}">{self.__class__.__name__}</div>'

    def to_dict(self) -> dict[str, Any]:
        """Serialize component metadata to a dictionary."""
        return {"type": self.__class__.__name__}

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(css_class={self.css_class!r})"
