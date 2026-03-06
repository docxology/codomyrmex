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
    from .dark_pdf_wrapper import DarkPDF
    from .filters import DarkPDFFilter, apply_dark_mode

    FILTERS_AVAILABLE = True
except ImportError:
    DarkPDFFilter = None
    apply_dark_mode = None
    DarkPDF = None
    FILTERS_AVAILABLE = False

__all__ = [
    "FILTERS_AVAILABLE",
    "DarkPDF",
    "DarkPDFFilter",
    "apply_dark_mode",
]
