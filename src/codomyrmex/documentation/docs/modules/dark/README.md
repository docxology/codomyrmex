<!-- readme: generated -->

# dark

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/dark/`

## Overview

Dark modes module - PDF dark mode utilities.

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

## Public Exports

`dark` exports 5 public symbols via `__all__`:

`PDF_AVAILABLE`, `PDF_PRESETS`, `__version__`, `cli_commands`, `pdf`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../dark/](../../../../dark/)
