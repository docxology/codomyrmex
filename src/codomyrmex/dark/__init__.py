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

import contextlib
import importlib
from importlib.util import find_spec

__version__ = "0.1.0"

# PDF uses native optional dependencies. Do not import it while loading the
# parent package: MCP discovery imports ``dark.mcp_tools`` for metadata, and
# eagerly loading PyMuPDF there can crash the interpreter on otherwise valid
# installations. The real submodule is loaded only when a caller asks for it.
# PyMuPDF's supported import name is ``pymupdf``. The historical ``fitz``
# alias loads an extra compatibility package and is prone to native crashes
# after other extension modules have been imported in a long-lived process.
PDF_AVAILABLE = find_spec("pymupdf") is not None and find_spec("PIL") is not None

# Keep capability metadata independent from the native PDF implementation.
# MCP discovery and health checks must be able to answer without importing
# PyMuPDF, which is an optional native dependency and can be unsafe to load
# repeatedly in a long-lived discovery process.
PDF_PRESETS: dict[str, dict[str, float]] = {
    "dark": {
        "inversion": 0.90,
        "brightness": 0.90,
        "contrast": 0.90,
        "sepia": 0.10,
    },
    "sepia": {
        "inversion": 0.85,
        "brightness": 0.95,
        "contrast": 0.90,
        "sepia": 0.40,
    },
    "high_contrast": {
        "inversion": 1.0,
        "brightness": 1.0,
        "contrast": 1.3,
        "sepia": 0.0,
    },
    "low_light": {
        "inversion": 0.80,
        "brightness": 0.70,
        "contrast": 0.85,
        "sepia": 0.05,
    },
}


def __getattr__(name: str):
    """Lazily load the optional PDF submodule on explicit access."""
    if name == "pdf":
        module = importlib.import_module(".pdf", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Shared schemas for cross-module interop
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus


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
    "PDF_AVAILABLE",
    "PDF_PRESETS",
    "__version__",
    # CLI integration
    "cli_commands",
    "pdf",
]
