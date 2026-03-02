# Agent Guidelines - Dark

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Dark mode utilities for PDFs. The module provides high-level and low-level APIs for transforming documents for better readability in low-light environments.

## Key Classes

- **DarkPDF** — Fluent API for PDF dark mode processing.
- **DarkPDFFilter** — Core filter logic: inversion, brightness, contrast, sepia.
- **apply_dark_mode(path, [output])** — Convenience function for conversion.

## Agent Instructions

1. **Use Fluent API** — Prefer `DarkPDF(path).set_brightness(0.8).save(out)` for clear, readable code.
2. **Choose Presets** — Use `preset="sepia"` or `preset="high_contrast"` for common needs.
3. **Adjust Parameters** — Fine-tune `inversion`, `brightness`, `contrast`, and `sepia` for specific document types.
4. **Zero-Mock Testing** — Always test with real PDF artifacts, never mock PyMuPDF or Pillow.
5. **Check Output Quality** — Ensure text remains legible after transformation.

## Common Patterns

```python
from codomyrmex.dark.pdf import apply_dark_mode, DarkPDF, DarkPDFFilter

# Simple dark mode conversion (one-call)
apply_dark_mode("document.pdf", "document_dark.pdf")

# Fluent API with customization
(
    DarkPDF("document.pdf")
    .set_filter("sepia")
    .set_brightness(0.8)
    .set_contrast(1.1)
    .save("output.pdf")
)

# Batch processing
DarkPDF.batch(
    ["doc1.pdf", "doc2.pdf"],
    output_dir="dark_pdfs/",
    preset="dark"
)
```

## Testing Patterns

```python
# Verify dark mode processing with zero mocks
from codomyrmex.dark.pdf import apply_dark_mode, DarkPDF

processor = apply_dark_mode("test.pdf")
assert processor.page_count > 0
assert processor.current_filter.inversion == 0.90
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, privacy architecture design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output quality validation | OBSERVED |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
