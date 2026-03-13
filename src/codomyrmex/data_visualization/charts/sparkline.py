"""Inline SVG sparkline renderer.

Generates compact, embeddable SVG sparklines for use in tables, cards,
and dashboard components.  No external dependencies required.

Example::

    svg = render_sparkline([3, 7, 2, 9, 4, 6, 8, 1, 5])
    print(svg)  # <svg ...> polyline </svg>

    # With configuration
    svg = render_sparkline(
        values=[10, 20, 15, 25, 18],
        config=SparklineConfig(width=200, height=40, color="#22c55e"),
    )
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True)
class SparklineConfig:
    """Configuration for sparkline rendering.

    Attributes:
        width: SVG width in pixels.
        height: SVG height in pixels.
        color: Stroke color (CSS color string).
        fill_color: Optional fill below the line.
        stroke_width: Line thickness.
        dot_radius: Radius for endpoint dots (0 to disable).
        padding: Internal padding in pixels.
        title: Optional accessible title for the SVG.
    """

    width: int = 120
    height: int = 30
    color: str = "#6366f1"
    fill_color: str = ""
    stroke_width: float = 1.5
    dot_radius: float = 2.0
    padding: float = 2.0
    title: str = ""


@dataclass
class SparklineResult:
    """Result of a sparkline render.

    Attributes:
        svg: The generated SVG markup.
        min_value: Minimum value in the series.
        max_value: Maximum value in the series.
        point_count: Number of data points.
    """

    svg: str
    min_value: float
    max_value: float
    point_count: int


def _scale_points(
    values: Sequence[float],
    width: float,
    height: float,
    padding: float,
) -> list[tuple[float, float]]:
    """Scale data values to SVG coordinate space."""
    if not values:
        return []

    n = len(values)
    min_v = min(values)
    max_v = max(values)
    v_range = max_v - min_v if max_v != min_v else 1.0

    usable_w = width - 2 * padding
    usable_h = height - 2 * padding

    points: list[tuple[float, float]] = []
    for i, v in enumerate(values):
        x = padding + (i / max(n - 1, 1)) * usable_w
        y = padding + (1.0 - (v - min_v) / v_range) * usable_h
        points.append((round(x, 2), round(y, 2)))

    return points


def render_sparkline(
    values: Sequence[float],
    config: SparklineConfig | None = None,
) -> SparklineResult:
    """Render a sparkline as an inline SVG string.

    Args:
        values: Numeric data series.
        config: Optional rendering configuration.

    Returns:
        A :class:`SparklineResult` containing the SVG markup and metadata.

    Raises:
        ValueError: If *values* is empty.
    """
    if not values:
        msg = "Cannot render sparkline from empty data"
        raise ValueError(msg)

    cfg = config or SparklineConfig()
    points = _scale_points(values, cfg.width, cfg.height, cfg.padding)
    points_str = " ".join(f"{x},{y}" for x, y in points)

    parts: list[str] = []

    # SVG open
    title_attr = f' aria-label="{html.escape(cfg.title)}"' if cfg.title else ""
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{cfg.width}" height="{cfg.height}" '
        f'viewBox="0 0 {cfg.width} {cfg.height}"'
        f"{title_attr}>"
    )

    if cfg.title:
        parts.append(f"<title>{html.escape(cfg.title)}</title>")

    # Optional fill area
    if cfg.fill_color and len(points) >= 2:
        fill_points = points_str + (
            f" {points[-1][0]},{cfg.height - cfg.padding}"
            f" {points[0][0]},{cfg.height - cfg.padding}"
        )
        parts.append(
            f'<polygon points="{fill_points}" fill="{cfg.fill_color}" opacity="0.15" />'
        )

    # Polyline
    parts.append(
        f'<polyline points="{points_str}" '
        f'fill="none" stroke="{cfg.color}" '
        f'stroke-width="{cfg.stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" />'
    )

    # Endpoint dots
    if cfg.dot_radius > 0 and points:
        for pt in (points[0], points[-1]):
            parts.append(
                f'<circle cx="{pt[0]}" cy="{pt[1]}" '
                f'r="{cfg.dot_radius}" fill="{cfg.color}" />'
            )

    parts.append("</svg>")

    return SparklineResult(
        svg="\n".join(parts),
        min_value=float(min(values)),
        max_value=float(max(values)),
        point_count=len(values),
    )


def render_sparkline_html(
    values: Sequence[float],
    label: str = "",
    config: SparklineConfig | None = None,
) -> str:
    """Render a sparkline wrapped in an HTML container with optional label.

    Args:
        values: Numeric data series.
        label: Optional text label to display beside the sparkline.
        config: Rendering configuration.

    Returns:
        HTML string with the sparkline and label.
    """
    result = render_sparkline(values, config)
    label_html = (
        f'<span style="font-size:12px;color:#888;margin-right:4px">{html.escape(label)}</span>'
        if label
        else ""
    )
    return (
        f'<span style="display:inline-flex;align-items:center;gap:4px">'
        f"{label_html}{result.svg}"
        f'<span style="font-size:11px;color:#666">'
        f"{result.min_value:.0f}–{result.max_value:.0f}</span>"
        f"</span>"
    )


__all__ = [
    "SparklineConfig",
    "SparklineResult",
    "render_sparkline",
    "render_sparkline_html",
]
