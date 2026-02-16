"""Multi-format chart export (PNG, SVG, PDF).

Provides export utilities for saving charts and figures
to multiple output formats with configuration options.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"
    JPEG = "jpeg"
    WEBP = "webp"


@dataclass
class ExportConfig:
    """Configuration for chart export."""
    format: ExportFormat = ExportFormat.PNG
    dpi: int = 150
    width: int | None = None
    height: int | None = None
    transparent: bool = False
    quality: int = 95  # For JPEG
    tight_layout: bool = True


class ChartExporter:
    """Export matplotlib figures and charts to multiple formats."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or Path(".")

    def export(self, fig: Any, filename: str,
               config: ExportConfig | None = None) -> Path:
        """Export a matplotlib figure to file.

        Args:
            fig: Matplotlib figure object.
            filename: Base filename (extension added from config).
            config: Export configuration.

        Returns:
            Path to exported file.
        """
        cfg = config or ExportConfig()
        ext = cfg.format.value
        output_path = self._output_dir / f"{filename}.{ext}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        save_kwargs: dict[str, Any] = {
            "dpi": cfg.dpi,
            "transparent": cfg.transparent,
            "format": ext,
        }
        if cfg.tight_layout:
            save_kwargs["bbox_inches"] = "tight"
        if cfg.format == ExportFormat.JPEG:
            save_kwargs["quality"] = cfg.quality

        fig.savefig(str(output_path), **save_kwargs)
        logger.info("Exported chart to %s (%d bytes)", output_path,
                     output_path.stat().st_size)
        return output_path

    def export_multi(self, fig: Any, filename: str,
                     formats: list[ExportFormat] | None = None,
                     dpi: int = 150) -> list[Path]:
        """Export a figure to multiple formats at once."""
        fmts = formats or [ExportFormat.PNG, ExportFormat.SVG]
        paths = []
        for fmt in fmts:
            cfg = ExportConfig(format=fmt, dpi=dpi)
            paths.append(self.export(fig, filename, cfg))
        return paths

    def export_html(self, fig: Any, filename: str) -> Path:
        """Export an interactive figure to HTML (if Plotly-compatible)."""
        output_path = self._output_dir / f"{filename}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if hasattr(fig, 'write_html'):
            fig.write_html(str(output_path))
        elif hasattr(fig, 'savefig'):
            # Fallback: save as SVG embedded in HTML
            svg_path = self.export(fig, filename, ExportConfig(format=ExportFormat.SVG))
            svg_content = svg_path.read_text()
            html = f"<!DOCTYPE html><html><body>{svg_content}</body></html>"
            output_path.write_text(html)
            svg_path.unlink()
        return output_path
