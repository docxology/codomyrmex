# PDF — Functional Specification

**Module**: `codomyrmex.dark.pdf`
**Status**: Active

## 1. Overview

PDF dark mode filters inspired by dark-pdf.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `DarkPDF` | Class | High-level API for applying dark mode to PDFs. |
| `DarkPDFFilter` | Class | Configurable dark mode filter for PDF pages. |

## 3. API Usage

```python
from codomyrmex.dark.pdf import DarkPDF
```

## 4. Dependencies

See `src/codomyrmex/dark/pdf/__init__.py` for import dependencies.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k pdf -v
```

## References

- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [Parent: Dark Modes](../SPEC.md)
