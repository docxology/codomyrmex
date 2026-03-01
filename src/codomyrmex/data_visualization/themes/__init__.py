"""
Theme definitions for data visualization.

Provides predefined color schemes and styling configurations.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ThemeName(Enum):
    """Available theme names."""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    VIBRANT = "vibrant"
    MINIMAL = "minimal"
    SCIENTIFIC = "scientific"


@dataclass
class ColorPalette:
    """Color palette configuration."""
    primary: str
    secondary: str
    accent: str
    background: str
    foreground: str
    success: str = "#28a745"
    warning: str = "#ffc107"
    error: str = "#dc3545"
    info: str = "#17a2b8"
    series: list[str] = field(default_factory=list)

    def get_series_color(self, index: int) -> str:
        """Get color for a series by index (cycles through available colors)."""
        if not self.series:
            return self.primary
        return self.series[index % len(self.series)]


@dataclass
class FontConfig:
    """Font configuration for charts."""
    family: str = "sans-serif"
    title_size: int = 16
    label_size: int = 12
    tick_size: int = 10
    legend_size: int = 11
    weight: str = "normal"


@dataclass
class GridConfig:
    """Grid configuration for charts."""
    show: bool = True
    color: str = "#e0e0e0"
    alpha: float = 0.5
    linestyle: str = "-"
    linewidth: float = 0.5


@dataclass
class Theme:
    """Complete theme configuration."""
    name: ThemeName
    colors: ColorPalette
    fonts: FontConfig = field(default_factory=FontConfig)
    grid: GridConfig = field(default_factory=GridConfig)
    figure_facecolor: str = "#ffffff"
    axes_facecolor: str = "#ffffff"
    spine_color: str = "#cccccc"
    spine_width: float = 1.0

    def to_matplotlib_rcparams(self) -> dict:
        """Convert theme to matplotlib rcParams."""
        return {
            'figure.facecolor': self.figure_facecolor,
            'axes.facecolor': self.axes_facecolor,
            'axes.edgecolor': self.spine_color,
            'axes.linewidth': self.spine_width,
            'axes.labelcolor': self.colors.foreground,
            'axes.titlecolor': self.colors.foreground,
            'xtick.color': self.colors.foreground,
            'ytick.color': self.colors.foreground,
            'text.color': self.colors.foreground,
            'grid.color': self.grid.color,
            'grid.alpha': self.grid.alpha,
            'grid.linestyle': self.grid.linestyle,
            'grid.linewidth': self.grid.linewidth,
            'font.family': self.fonts.family,
            'font.size': self.fonts.label_size,
            'axes.titlesize': self.fonts.title_size,
            'axes.labelsize': self.fonts.label_size,
            'xtick.labelsize': self.fonts.tick_size,
            'ytick.labelsize': self.fonts.tick_size,
            'legend.fontsize': self.fonts.legend_size,
        }


# Predefined themes
THEMES: dict[ThemeName, Theme] = {
    ThemeName.DEFAULT: Theme(
        name=ThemeName.DEFAULT,
        colors=ColorPalette(
            primary="#1f77b4",
            secondary="#ff7f0e",
            accent="#2ca02c",
            background="#ffffff",
            foreground="#333333",
            series=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
        ),
    ),
    ThemeName.DARK: Theme(
        name=ThemeName.DARK,
        colors=ColorPalette(
            primary="#4cc9f0",
            secondary="#f72585",
            accent="#7209b7",
            background="#1a1a2e",
            foreground="#eaeaea",
            series=["#4cc9f0", "#f72585", "#7209b7", "#3a0ca3", "#4361ee",
                    "#480ca8", "#560bad", "#b5179e", "#f15bb5", "#00f5d4"],
        ),
        figure_facecolor="#1a1a2e",
        axes_facecolor="#16213e",
        spine_color="#404040",
        grid=GridConfig(color="#404040", alpha=0.3),
    ),
    ThemeName.LIGHT: Theme(
        name=ThemeName.LIGHT,
        colors=ColorPalette(
            primary="#0d6efd",
            secondary="#6c757d",
            accent="#198754",
            background="#f8f9fa",
            foreground="#212529",
            series=["#0d6efd", "#6610f2", "#6f42c1", "#d63384", "#dc3545",
                    "#fd7e14", "#ffc107", "#198754", "#20c997", "#0dcaf0"],
        ),
        figure_facecolor="#f8f9fa",
        axes_facecolor="#ffffff",
    ),
    ThemeName.VIBRANT: Theme(
        name=ThemeName.VIBRANT,
        colors=ColorPalette(
            primary="#ff006e",
            secondary="#8338ec",
            accent="#3a86ff",
            background="#ffffff",
            foreground="#000000",
            series=["#ff006e", "#8338ec", "#3a86ff", "#fb5607", "#ffbe0b",
                    "#06d6a0", "#118ab2", "#073b4c", "#ef476f", "#ffd166"],
        ),
    ),
    ThemeName.MINIMAL: Theme(
        name=ThemeName.MINIMAL,
        colors=ColorPalette(
            primary="#2d3436",
            secondary="#636e72",
            accent="#0984e3",
            background="#ffffff",
            foreground="#2d3436",
            series=["#2d3436", "#636e72", "#b2bec3", "#dfe6e9"],
        ),
        grid=GridConfig(show=False),
        spine_color="#dfe6e9",
    ),
    ThemeName.SCIENTIFIC: Theme(
        name=ThemeName.SCIENTIFIC,
        colors=ColorPalette(
            primary="#003f5c",
            secondary="#58508d",
            accent="#bc5090",
            background="#ffffff",
            foreground="#2f4858",
            series=["#003f5c", "#2f4b7c", "#665191", "#a05195",
                    "#d45087", "#f95d6a", "#ff7c43", "#ffa600"],
        ),
        fonts=FontConfig(family="serif", weight="normal"),
    ),
}


def get_theme(name: ThemeName = ThemeName.DEFAULT) -> Theme:
    """Get a theme by name."""
    return THEMES.get(name, THEMES[ThemeName.DEFAULT])


def apply_theme(theme: Theme) -> None:
    """Apply a theme to matplotlib."""
    try:
        import matplotlib.pyplot as plt
        plt.rcParams.update(theme.to_matplotlib_rcparams())
    except ImportError as e:
        logger.debug("matplotlib not available, cannot apply theme: %s", e)
        pass  # matplotlib not available


def list_themes() -> list[str]:
    """List available theme names."""
    return [t.value for t in ThemeName]


__all__ = [
    "ThemeName",
    "ColorPalette",
    "FontConfig",
    "GridConfig",
    "Theme",
    "THEMES",
    "get_theme",
    "apply_theme",
    "list_themes",
]
