# Static Analysis — Functional Specification

**Module**: `codomyrmex.static_analysis`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Static Analysis Module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `analyze_codebase()` | Function | Alias for analyze_project for backward compatibility. |
| `analyze_code_quality()` | Function | Analyze code quality for workflow integration. |

### Submodule Structure

- `complexity/` — Static Analysis Complexity Module
- `linting/` — Static Analysis Linting Module

### Source Files

- `exceptions.py`
- `pyrefly_runner.py`
- `static_analyzer.py`

## 3. Dependencies

See `src/codomyrmex/static_analysis/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.static_analysis import analyze_codebase, analyze_code_quality
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k static_analysis -v
```
