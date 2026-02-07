# i18n - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Internationalization module providing translation management, pluralization rules, and locale-aware formatting.

## Functional Requirements

- Message translation with interpolation
- Pluralization rules for multiple languages
- Number and currency formatting per locale
- Date/time formatting per locale
- Fallback locale chain support

## Core Classes

| Class | Description |
|-------|-------------|
| `Translator` | Message translation engine |
| `Locale` | Locale representation |
| `MessageBundle` | Translation bundle |
| `PluralRules` | Pluralization engine |
| `NumberFormatter` | Locale-aware number formatting |

## Key Functions

| Function | Description |
|----------|-------------|
| `init(locale, bundles_path)` | Initialize translator |
| `t(key, **context)` | Translate message |
| `set_locale(locale)` | Change active locale |

## Design Principles

1. **Fallback Chain**: Language → Country → Default
2. **ICU Format**: Industry-standard message format
3. **Lazy Loading**: Load bundles on demand
4. **Thread Safety**: Safe for concurrent access

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k i18n -v
```
