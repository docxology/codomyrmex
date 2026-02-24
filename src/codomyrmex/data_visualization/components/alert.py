"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class Alert(BaseComponent):
    """Alert component."""
    message: str = ""
    level: str = "info"

    _BG_MAP = {
        "success": "#dff0d8",
        "warning": "#fcf8e3",
        "danger": "#f2dede",
        "info": "#d9edf7",
    }

    def render(self) -> str:
        """Execute Render operations natively."""
        bg = self._BG_MAP.get(self.level, "#d9edf7")
        return (
            f'<div class="alert alert-{self.level}" '
            f'style="background-color: {bg}; padding: 12px; border-radius: 4px;">'
            f'{self.message}</div>'
        )

    def __str__(self) -> str:
        """Execute   Str   operations natively."""
        return self.render()
