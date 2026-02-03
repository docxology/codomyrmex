"""PDF dark mode filters inspired by dark-pdf.

Provides native Python implementations of PDF dark mode filters using
PyMuPDF (fitz) for PDF rendering and Pillow for image processing.

Classes:
    DarkPDFFilter: Configurable filter with inversion, brightness, contrast, sepia
    DarkPDF: High-level convenience wrapper with presets

Functions:
    apply_dark_mode: Standalone function for one-call PDF dark mode conversion
"""

try:
    from .filters import DarkPDFFilter, apply_dark_mode
    from .dark_pdf_wrapper import DarkPDF

    FILTERS_AVAILABLE = True
except ImportError:
    DarkPDFFilter = None  # type: ignore
    apply_dark_mode = None  # type: ignore
    DarkPDF = None  # type: ignore
    FILTERS_AVAILABLE = False

__all__ = [
    "DarkPDFFilter",
    "apply_dark_mode",
    "DarkPDF",
    "FILTERS_AVAILABLE",
]
