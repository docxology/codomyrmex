"""Dark modes module - PDF dark mode utilities.

This module provides dark mode utilities for PDF documents:
- pdf: PDF dark mode filters (inversion, brightness, contrast, sepia)

The hardware, network, and software submodules have been removed as they
contained no implementation. Only the pdf submodule (with real functionality)
is retained.

Installation:
    Install dark mode dependencies with:
    ```bash
    uv sync --extra dark
    ```

Quick Start:
    ```python
    from codomyrmex.dark.pdf import DarkPDF, DarkPDFFilter, apply_dark_mode

    # Simple one-call API
    DarkPDF("input.pdf").save("output.pdf")

    # With preset
    DarkPDF("input.pdf", preset="sepia").save("output.pdf")

    # Custom filters
    apply_dark_mode("input.pdf", "output.pdf", inversion=0.85, contrast=1.2)
    ```
"""

__version__ = "0.1.0"

# PDF submodule uses optional dependencies
try:
    from . import pdf
    PDF_AVAILABLE = True
except ImportError:
    pdf = None  # type: ignore
    PDF_AVAILABLE = False

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the dark module."""
    return {
        "status": {
            "help": "Show dark mode status",
            "handler": lambda: print(
                "Dark Mode Status:\n"
                f"  PDF support:      {'available' if PDF_AVAILABLE else 'not installed'}"
            ),
        },
        "config": {
            "help": "Show dark mode configuration",
            "handler": lambda: print(
                "Dark Mode Config:\n"
                f"  Version:          {__version__}\n"
                f"  PDF available:    {PDF_AVAILABLE}\n"
                "  Submodules:       pdf"
            ),
        },
    }


__all__ = [
    "__version__",
    "pdf",
    "PDF_AVAILABLE",
    # CLI integration
    "cli_commands",
]
