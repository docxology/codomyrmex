"""Component module."""
from dataclasses import dataclass

from ._base import BaseComponent


@dataclass
class ProgressBar(BaseComponent):
    """Progress bar component."""
    value: float = 0.0
    max_value: float = 100.0
    label: str = ""

    def render(self) -> str:
        """render ."""
        pct = (self.value / self.max_value * 100) if self.max_value else 0
        lbl = f'<span>{self.label}</span>' if self.label else ''
        return (
            f'<div class="progress">'
            f'{lbl}'
            f'<div class="progress-bar" style="width: {pct}%">{pct:.0f}%</div>'
            f'</div>'
        )

    def __str__(self) -> str:
        """str ."""
        return self.render()
