# Documentation Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Documentation generation, parsing, and rendering utilities.

## Key Features

- **Markdown** — Parse and render Markdown
- **Docstrings** — Extract from Python
- **API Docs** — Generate API documentation
- **Templates** — Documentation templates

## Quick Start

```python
from codomyrmex.documentation import DocGenerator

generator = DocGenerator()
generator.scan("src/")
generator.generate_api_docs("docs/api/")
generator.generate_readme_summary("docs/")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/documentation/](../../../src/codomyrmex/documentation/)
- **Parent**: [Modules](../README.md)
