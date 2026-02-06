# Agent Guidelines - Dark

## Module Overview

Dark mode utilities for PDFs, network, hardware, and software.

## Key Classes

- **DarkPDF** — PDF dark mode processing
- **DarkPDFFilter** — Filter types: inversion, brightness, contrast, sepia
- **apply_dark_mode(path)** — Apply dark mode to PDF

## Agent Instructions

1. **Use apply_dark_mode** — Convenience function for simple conversions
2. **Choose filter type** — Inversion for basic, sepia for readability
3. **Adjust brightness** — Reduce for eye comfort
4. **Preserve images** — Use smart inversion to skip images
5. **Check output quality** — Verify text remains readable

## Common Patterns

```python
from codomyrmex.dark import apply_dark_mode, DarkPDF, DarkPDFFilter

# Simple dark mode conversion
dark_pdf = apply_dark_mode("document.pdf")
dark_pdf.save("document_dark.pdf")

# Advanced customization
processor = DarkPDF("document.pdf")
processor.set_filter(DarkPDFFilter.SEPIA)
processor.set_brightness(0.8)
processor.set_contrast(1.1)
processor.process()
processor.save("output.pdf")

# Batch processing
for pdf in pdf_files:
    apply_dark_mode(pdf).save(pdf.replace(".pdf", "_dark.pdf"))
```

## Testing Patterns

```python
# Verify dark mode processing
from codomyrmex.dark import apply_dark_mode

result = apply_dark_mode("test.pdf")
assert result is not None
assert result.page_count > 0

# Verify filter application
processor = DarkPDF("test.pdf")
processor.set_filter(DarkPDFFilter.INVERSION)
assert processor.current_filter == DarkPDFFilter.INVERSION
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
