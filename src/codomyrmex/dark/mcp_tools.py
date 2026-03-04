"""MCP tool definitions for the dark module.

Exposes PDF dark mode status and capabilities as MCP tools.
The actual PDF transformation requires optional dependencies (PyMuPDF, Pillow).
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="dark",
    description="Check if dark mode PDF dependencies are installed and list available presets.",
)
def dark_status() -> dict[str, Any]:
    """Check dark mode module availability and list supported presets.

    Returns:
        dict with status, pdf_available flag, version, and available presets.
    """
    try:
        from codomyrmex.dark import PDF_AVAILABLE, __version__

        presets = []
        if PDF_AVAILABLE:
            try:
                from codomyrmex.dark.pdf.dark_pdf_wrapper import DarkPDF

                presets = list(DarkPDF.PRESETS.keys()) if hasattr(DarkPDF, "PRESETS") else []
            except (ImportError, AttributeError):
                pass

        return {
            "status": "success",
            "pdf_available": PDF_AVAILABLE,
            "version": __version__,
            "presets": presets,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="dark",
    description="List the available dark mode filter presets and their parameter values.",
)
def dark_list_presets() -> dict[str, Any]:
    """List available dark mode presets with their filter parameters.

    Returns:
        dict with status and presets mapping (name -> filter params).
    """
    try:
        from codomyrmex.dark import PDF_AVAILABLE

        if not PDF_AVAILABLE:
            return {
                "status": "success",
                "pdf_available": False,
                "presets": {},
                "install_hint": "uv sync --extra dark",
            }

        from codomyrmex.dark.pdf.dark_pdf_wrapper import DarkPDF

        presets = {}
        if hasattr(DarkPDF, "PRESETS"):
            for name, params in DarkPDF.PRESETS.items():
                presets[name] = (
                    dict(params.items()) if isinstance(params, dict) else str(params)
                )

        return {
            "status": "success",
            "pdf_available": True,
            "presets": presets,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
