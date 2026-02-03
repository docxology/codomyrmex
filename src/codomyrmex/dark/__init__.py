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
from . import network
from . import hardware
from . import software

# PDF submodule uses optional dependencies
try:
    from . import pdf
    PDF_AVAILABLE = True
except ImportError:
    pdf = None  # type: ignore
    PDF_AVAILABLE = False

__all__ = [
    "__version__",
    "pdf",
    "network",
    "hardware",
    "software",
    "PDF_AVAILABLE",
]
