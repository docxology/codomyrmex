"""Visualization themes and styling."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ThemeColors:
    """Theme color palette."""
    background: str = "#ffffff"
    text: str = "#000000"
    primary: str = "#3498db"
    secondary: str = "#2ecc71"
    accent: str = "#e74c3c"
    edge_default: str = "#95a5a6"
    status_success: str = "#2ecc71"
    status_warning: str = "#f39c12"
    status_error: str = "#e74c3c"
    status_neutral: str = "#95a5a6"

@dataclass
class ThemeFont:
    """Theme font settings."""
    family: str = "sans-serif"
    title_size: int = 16
    label_size: int = 12
    tick_size: int = 10

class Theme:
    """Visualization theme manager."""

    def __init__(self, name: str = "default"):
        self.name = name
        self.colors = ThemeColors()
        self.font = ThemeFont()

    def get_color_sequence(self, n: int, base_color: str = "primary") -> list[str]:
        """Get a sequence of n colors based on a base color."""
        import matplotlib.pyplot as plt
        import numpy as np

        if base_color == "primary":
            pass
        else:
            pass

        # Generate varied colors
        cmap = plt.get_cmap("viridis")
        return [cmap(i) for i in np.linspace(0, 1, n)]

    def get_status_color(self, status: str) -> str:
        """Get color for a status string."""
        status = status.lower()
        if status in ["active", "success", "stable", "complete"]:
            return self.colors.status_success
        elif status in ["warning", "draft", "in_progress"]:
            return self.colors.status_warning
        elif status in ["error", "deprecated", "removed"]:
            return self.colors.status_error
        else:
            return self.colors.status_neutral

    def apply_to_axes(self, ax: Any) -> None:
        """Apply theme to matplotlib axes."""
        if hasattr(ax, 'set_facecolor'):
            ax.set_facecolor(self.colors.background)
        if hasattr(ax, 'tick_params'):
            ax.tick_params(colors=self.colors.text, labelsize=self.font.tick_size)
        if hasattr(ax, 'set_title') and ax.get_title():
            ax.set_title(ax.get_title(), color=self.colors.text, fontsize=self.font.title_size)

    def create_legend(self, ax: Any, handles: list[Any], labels: list[str], **kwargs) -> None:
        """Create styled legend."""
        ax.legend(handles, labels, **kwargs)


def get_default_theme() -> Theme:
    """Get the default theme instance."""
    return Theme("default")
