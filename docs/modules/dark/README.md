# Dark Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `dark` module provides dark mode utilities across multiple domains. The primary implemented capability is PDF dark mode filtering, which applies inversion, brightness, contrast, and sepia adjustments to PDF documents. The module also includes placeholder submodules for network, hardware, and software dark mode utilities. PDF processing is powered by PyMuPDF and Pillow, with the filter pipeline inspired by the dark-pdf JavaScript project.

## Key Features

- **PDF dark mode conversion**: Apply dark mode filters to PDF documents with a simple one-call API via `DarkPDF`
- **Configurable filter pipeline**: Adjust inversion, brightness, contrast, and sepia parameters independently
- **Built-in presets**: Pre-configured filter combinations including `dark`, `sepia`, `high_contrast`, and `low_light`
- **Batch processing**: Process multiple PDF files in a single call with `DarkPDF.batch()`
- **Functional API**: Standalone `apply_dark_mode()` function for quick one-off conversions
- **Graceful dependency handling**: `PDF_AVAILABLE` flag for runtime capability detection when PyMuPDF/Pillow are not installed
- **Multi-domain architecture**: Organized into `pdf`, `network`, `hardware`, and `software` submodules

## Key Components

| Component | Description |
|-----------|-------------|
| `pdf` | Submodule providing PDF dark mode filters; contains `DarkPDF`, `DarkPDFFilter`, and `apply_dark_mode` |
| `network` | Submodule for network dark mode utilities (placeholder) |
| `hardware` | Submodule for hardware dark mode utilities (placeholder) |
| `software` | Submodule for software dark mode utilities (placeholder) |
| `PDF_AVAILABLE` | Boolean flag indicating whether PDF processing dependencies (PyMuPDF, Pillow) are installed |

## Available Presets

| Preset | Inversion | Brightness | Contrast | Sepia |
|--------|-----------|------------|----------|-------|
| `dark` (default) | 0.90 | 0.90 | 0.90 | 0.10 |
| `sepia` | 0.85 | 0.95 | 0.90 | 0.40 |
| `high_contrast` | 1.00 | 1.00 | 1.30 | 0.00 |
| `low_light` | 0.80 | 0.70 | 0.85 | 0.05 |

## Installation

```bash
# Install dark mode dependencies (PyMuPDF and Pillow)
uv sync --extra dark
```

## Quick Start

```python
from codomyrmex.dark.pdf import DarkPDF, DarkPDFFilter, apply_dark_mode

# Simple one-call API
DarkPDF("input.pdf").save("output.pdf")

# With a preset
DarkPDF("input.pdf", preset="sepia").save("output.pdf")

# Custom filter parameters
apply_dark_mode("input.pdf", "output.pdf", inversion=0.85, contrast=1.2)

# Batch processing
DarkPDF.batch(
    ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    output_dir="dark_pdfs/",
    preset="dark",
)
```

## Credits

The PDF filter logic is inspired by [dark-pdf](https://github.com/benjifriedman/dark-pdf), a Next.js application for applying dark mode to PDFs. The original JavaScript filter pipeline has been reimplemented natively in Python using PyMuPDF and Pillow. The dark-pdf source is included as a git submodule at `pdf/vendor/dark-pdf/` for reference.


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k dark -v
```

## Related Modules

- [documents](../documents/) - Document processing utilities that may consume dark mode outputs
- [data_visualization](../data_visualization/) - Visualization module where dark theming may be relevant

## Navigation

- **Source**: [src/codomyrmex/dark/](../../../src/codomyrmex/dark/)
- **Parent**: [docs/modules/](../README.md)
