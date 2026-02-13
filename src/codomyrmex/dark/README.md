# Dark Module

Dark mode utilities for different domains: PDF, network, hardware, and software.

## Submodules

| Submodule | Status | Description |
|-----------|--------|-------------|
| `pdf` | Implemented | PDF dark mode filters (inversion, brightness, contrast, sepia) |
| `network` | Planned | Network dark mode utilities — Planned for future implementation |
| `hardware` | Planned | Hardware dark mode utilities — Planned for future implementation |
| `software` | Planned | Software dark mode utilities — Planned for future implementation |

## Key Exports

### Submodules
- **`pdf`** — PDF dark mode filters (inversion, brightness, contrast, sepia); `None` if dependencies missing
- **`network`** — Network dark mode utilities — Planned for future implementation
- **`hardware`** — Hardware dark mode utilities — Planned for future implementation
- **`software`** — Software dark mode utilities — Planned for future implementation

### Availability Flags
- **`PDF_AVAILABLE`** — Boolean flag indicating whether PDF processing dependencies (PyMuPDF, Pillow) are available

## Installation

```bash
uv sync --extra dark
```

This installs PyMuPDF and Pillow, required for the PDF submodule.

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

## Available Presets

| Preset | Inversion | Brightness | Contrast | Sepia |
|--------|-----------|------------|----------|-------|
| `dark` (default) | 0.90 | 0.90 | 0.90 | 0.10 |
| `sepia` | 0.85 | 0.95 | 0.90 | 0.40 |
| `high_contrast` | 1.00 | 1.00 | 1.30 | 0.00 |
| `low_light` | 0.80 | 0.70 | 0.85 | 0.05 |

## Credits

The PDF filter logic is inspired by [dark-pdf](https://github.com/benjifriedman/dark-pdf), a Next.js application for applying dark mode to PDFs. The original JavaScript filter pipeline has been reimplemented natively in Python using PyMuPDF and Pillow.

The dark-pdf source is included as a git submodule at `pdf/vendor/dark-pdf/` for reference.


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k dark -v
```

## Navigation

- **Full Documentation**: [docs/modules/dark/](../../../docs/modules/dark/)
- **Parent Directory**: [codomyrmex](../README.md)
