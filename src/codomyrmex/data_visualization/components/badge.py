"""Component module."""
from dataclasses import dataclass

from ._base import BaseComponent


@dataclass
class Badge(BaseComponent):
    """Badge component."""
    label: str = ""
    color: str = "#3B82F6"

    _COLOR_MAP = {
        "success": "#5cb85c",
        "warning": "#f0ad4e",
        "danger": "#d9534f",
        "info": "#5bc0de",
        "primary": "#3B82F6",
    }

    def render(self) -> str:
        """Render."""
        bg = self._COLOR_MAP.get(self.color, self.color)
        return (
            f'<span class="badge" style="background-color: {bg}; '
            f'color: white; padding: 2px 8px; border-radius: 4px;">'
            f'{self.label}</span>'
        )

    def __str__(self) -> str:
        """Return human-readable string."""
        return self.render()
