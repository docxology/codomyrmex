# Internationalization (i18n) Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Translation, localization, and message bundle management.

## Key Features

- **Locale** — A locale specification.
- **MessageBundle** — A collection of translated messages.
- **Translator** — Multi-locale translator.
- **PluralRules** — Pluralization rules for different locales.
- **NumberFormatter** — Format numbers for different locales.
- `init()` — init
- `t()` — t
- `code()` — code
- `from_string()` — from string

## Quick Start

```python
from codomyrmex.i18n import Locale, MessageBundle, Translator

# Initialize
instance = Locale()
```


## Installation

```bash
pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `Locale` | A locale specification. |
| `MessageBundle` | A collection of translated messages. |
| `Translator` | Multi-locale translator. |
| `PluralRules` | Pluralization rules for different locales. |
| `NumberFormatter` | Format numbers for different locales. |

### Functions

| Function | Description |
|----------|-------------|
| `init()` | init |
| `t()` | t |
| `code()` | code |
| `from_string()` | from string |
| `add()` | add |
| `get()` | get |
| `has()` | has |
| `keys()` | keys |
| `to_dict()` | to dict |
| `from_dict()` | from dict |
| `from_json_file()` | from json file |
| `add_bundle()` | add bundle |
| `set_locale()` | set locale |
| `get_locale()` | get locale |
| `load_directory()` | Load all JSON bundles from directory. |
| `get_rule()` | get rule |
| `pluralize()` | pluralize |
| `format()` | format |
| `replacer()` | replacer |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k i18n -v
```

## Navigation

- **Source**: [src/codomyrmex/i18n/](../../../src/codomyrmex/i18n/)
- **Parent**: [Modules](../README.md)
