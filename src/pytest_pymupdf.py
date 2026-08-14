"""Early optional PyMuPDF loader used by the repository pytest harness.

PyMuPDF's macOS arm64/Python 3.13 wheel is sensitive to native import order.
Keeping this tiny module outside the package avoids importing the full
``codomyrmex.testing`` package before pytest has initialized.
"""

try:
    import pymupdf
except ImportError:
    pass
