"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class StatBox(BaseComponent):
    """Stat box component."""
    label: str = ""
    value: str = ""
    delta: str = ""
    direction: str = ""  # "up" or "down"

    def render(self) -> str:
        color = "green" if self.direction == "up" else ("red" if self.direction == "down" else "gray")
        return (
            f'<div class="statbox">'
            f'<div class="statbox-label">{self.label}</div>'
            f'<div class="statbox-value">{self.value}</div>'
            f'<div class="statbox-delta" style="color: {color}">{self.delta}</div>'
            f'</div>'
        )

    def __str__(self) -> str:
        return self.render()
