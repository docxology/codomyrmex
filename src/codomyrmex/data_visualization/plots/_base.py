"""Base class for all plot types."""
from dataclasses import dataclass, field
from typing import Any

@dataclass
class BasePlot:
    """Base class for all plot types."""
    title: str = ""
    width: int = 800
    height: int = 400
    data: list[Any] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)

    def render(self) -> str:
        return f'<div class="plot" data-type="{self.__class__.__name__}">{self.title}</div>'

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.__class__.__name__, "title": self.title,
                "width": self.width, "height": self.height,
                "data_count": len(self.data)}
