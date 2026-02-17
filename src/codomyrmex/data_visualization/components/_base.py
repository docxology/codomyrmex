"""Base class for all UI components."""
from dataclasses import dataclass, field
from typing import Any

@dataclass
class BaseComponent:
    """Base class for all visualization components."""
    css_class: str = ""
    style: dict[str, str] = field(default_factory=dict)

    def render(self) -> str:
        return f'<div class="{self.css_class}">{self.__class__.__name__}</div>'

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.__class__.__name__}
