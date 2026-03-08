# Dark Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

Dark mode utilities for PDF processing, providing high-quality visual transformations.

## Submodules

| Submodule | Status | Description |
|-----------|--------|-------------|
| `pdf` | Implemented | PDF dark mode filters (inversion, brightness, contrast, sepia) |

## Installation

```bash
uv sync --extra dark
```

This installs PyMuPDF and Pillow, required for the PDF submodule.

## Quick Start

### Simple One-Call API
```python
from codomyrmex.dark.pdf import apply_dark_mode

# Apply standard dark mode and save
apply_dark_mode("input.pdf", "output.pdf")
```

### Fluent API (Fluent & Chainable)
```python
from codomyrmex.dark.pdf import DarkPDF

(
    DarkPDF("input.pdf")
    .set_filter("sepia")
    .set_brightness(0.8)
    .set_contrast(1.2)
    .save("output_custom.pdf")
)
```

### Batch Processing
```python
from codomyrmex.dark.pdf import DarkPDF

DarkPDF.batch(
    ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    output_dir="dark_pdfs/",
    preset="high_contrast",
)
```

## Available Presets

| Preset | Inversion | Brightness | Contrast | Sepia |
|--------|-----------|------------|----------|-------|
| `dark` (default) | 0.90 | 0.90 | 0.90 | 0.10 |
| `sepia` | 0.85 | 0.95 | 0.90 | 0.40 |
| `high_contrast` | 1.00 | 1.00 | 1.30 | 0.00 |
| `low_light` | 0.80 | 0.70 | 0.85 | 0.05 |

## Testing

The module follows a **Strict Zero-Mock Policy**. All tests use real PDF artifacts.

```bash
uv run python -m pytest src/codomyrmex/tests/ -k dark -v
```

## Orchestrator Example

A working example script is available at `scripts/dark/dark_orchestrator.py`.

```bash
uv run scripts/dark/dark_orchestrator.py
```

## Navigation

- **Full Documentation**: [docs/modules/dark/](../../../docs/modules/dark/)
- **Parent Directory**: [codomyrmex](../README.md)
