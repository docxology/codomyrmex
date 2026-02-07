# Internationalization (i18n) — Functional Specification

**Module**: `codomyrmex.i18n`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Translation, localization, and message bundle management.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `Locale` | Class | A locale specification. |
| `MessageBundle` | Class | A collection of translated messages. |
| `Translator` | Class | Multi-locale translator. |
| `PluralRules` | Class | Pluralization rules for different locales. |
| `NumberFormatter` | Class | Format numbers for different locales. |
| `init()` | Function | init |
| `t()` | Function | t |
| `code()` | Function | code |
| `from_string()` | Function | from string |
| `add()` | Function | add |

## 3. Dependencies

See `src/codomyrmex/i18n/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.i18n import Locale, MessageBundle, Translator, PluralRules, NumberFormatter
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k i18n -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/i18n/)
