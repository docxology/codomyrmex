"""Dark modes module - network, hardware, software, PDF dark mode utilities.

This module provides dark mode utilities across different domains:
- pdf: PDF dark mode filters (inversion, brightness, contrast, sepia)
- network: Network dark mode utilities (not yet implemented)
- hardware: Hardware dark mode utilities (not yet implemented)
- software: Software dark mode utilities (not yet implemented)

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

# Lazy imports to avoid pulling in heavy dependencies at module level
from . import hardware, network, software

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
            "help": "Show dark mode status across all domains",
            "handler": lambda: print(
                "Dark Mode Status:\n"
                f"  PDF support:      {'available' if PDF_AVAILABLE else 'not installed'}\n"
                f"  Network module:   loaded\n"
                f"  Hardware module:  loaded\n"
                f"  Software module:  loaded"
            ),
        },
        "config": {
            "help": "Show dark mode configuration",
            "handler": lambda: print(
                "Dark Mode Config:\n"
                f"  Version:          {__version__}\n"
                f"  PDF available:    {PDF_AVAILABLE}\n"
                "  Submodules:       pdf, network, hardware, software"
            ),
        },
    }


__all__ = [
    "__version__",
    "pdf",
    "network",
    "hardware",
    "software",
    "PDF_AVAILABLE",
    # CLI integration
    "cli_commands",
]
