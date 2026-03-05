"""Enums and dataclasses for the advanced plotter engine.

These are shared across all submodules: scatter, heatmap, histogram, etc.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PlotType(Enum):
    """Types of plots available."""

    LINE = "line"
    SCATTER = "scatter"
    BAR = "bar"
    HISTOGRAM = "histogram"
    PIE = "pie"
    HEATMAP = "heatmap"
    BOX = "box"
    VIOLIN = "violin"
    DENSITY = "density"
    CORRELATION = "correlation"
    TIMESERIES = "timeseries"
    DASHBOARD = "dashboard"
    INTERACTIVE = "interactive"


class ChartStyle(Enum):
    """Chart styling options."""

    DEFAULT = "default"
    MINIMAL = "minimal"
    DARK = "dark"
    WHITE = "white"
    TICKS = "ticks"
    DARKGRID = "darkgrid"
    WHITEGRID = "whitegrid"


class ColorPalette(Enum):
    """Color palette options."""

    DEFAULT = "default"
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    COOLWARM = "coolwarm"
    RAINBOW = "rainbow"
    PASTEL = "pastel"
    DARK = "dark"
    BRIGHT = "bright"


@dataclass
class PlotConfig:
    """Configuration for plot generation."""

    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    figsize: tuple[int, int] = (10, 6)
    dpi: int = 100
    style: ChartStyle = ChartStyle.DEFAULT
    palette: ColorPalette = ColorPalette.DEFAULT
    grid: bool = True
    legend: bool = True
    tight_layout: bool = True
    save_format: str = "png"
    save_dpi: int = 300
    show_plot: bool = True
    transparent: bool = False
    bbox_inches: str = "tight"


@dataclass
class DataPoint:
    """Individual data point for plotting."""

    x: float | int | str | datetime
    y: float | int | str | datetime
    label: str | None = None
    color: str | None = None
    size: float | None = None
    alpha: float = 1.0


@dataclass
class Dataset:
    """Dataset for plotting."""

    name: str
    data: list[DataPoint]
    plot_type: PlotType
    color: str | None = None
    label: str | None = None
    alpha: float = 1.0
    linewidth: float = 2.0
    markersize: float = 6.0


# Mapping from ChartStyle enum to seaborn style name
_STYLE_MAP: dict[ChartStyle, str] = {
    ChartStyle.MINIMAL: "white",
    ChartStyle.DARK: "dark",
    ChartStyle.WHITE: "white",
    ChartStyle.TICKS: "ticks",
    ChartStyle.DARKGRID: "darkgrid",
    ChartStyle.WHITEGRID: "whitegrid",
    ChartStyle.DEFAULT: "whitegrid",
}

# Mapping from ColorPalette enum to seaborn palette name
_PALETTE_MAP: dict[ColorPalette, str] = {
    p: p.value for p in ColorPalette if p != ColorPalette.DEFAULT
}
_PALETTE_MAP[ColorPalette.DEFAULT] = "husl"


def resolve_sns_style(style: ChartStyle) -> str:
    """Map a ChartStyle enum to its seaborn style name."""
    return _STYLE_MAP.get(style, "whitegrid")


def resolve_sns_palette(palette: ColorPalette) -> str:
    """Map a ColorPalette enum to its seaborn palette name."""
    return _PALETTE_MAP.get(palette, "husl")


def get_available_styles() -> list[ChartStyle]:
    """Get list of available chart styles."""
    return list(ChartStyle)


def get_available_palettes() -> list[ColorPalette]:
    """Get list of available color palettes."""
    return list(ColorPalette)


def get_available_plot_types() -> list[PlotType]:
    """Get list of available plot types."""
    return list(PlotType)
