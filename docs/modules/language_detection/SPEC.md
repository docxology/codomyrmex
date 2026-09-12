<!-- spec: generated -->

# Language Detection — Functional Specification

**Module**: `codomyrmex.language_detection`  
**Version**: v1.3.0  
**Status**: Active

## 1. Overview

Language detection module for the Codomyrmex platform.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `detect_language()` | Function | Detect the language of the provided text. |
| `detect_languages_with_probabilities()` | Function | Detect multiple languages with probabilities for the provided text. |

### Source Files

- `mcp_tools.py`

## 3. Dependencies

See `src/codomyrmex/language_detection/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.language_detection import detect_language, detect_languages_with_probabilities
```

## 5. Testing

```bash
uv run python -m pytest tests/ -k language_detection -v
```

