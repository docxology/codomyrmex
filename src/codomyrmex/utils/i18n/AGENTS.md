# Codomyrmex Agents -- src/codomyrmex/utils/i18n

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides internationalization (i18n) capabilities including multi-locale translation with interpolation, locale-aware number and date formatting, and CLDR-inspired pluralization rules.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `Locale` | Dataclass representing a locale (ISO 639-1 language + ISO 3166-1 region) with parsing via `from_string` |
| `translator.py` | `Translator` | Multi-locale translator with message bundles, interpolation, and fallback chain (exact locale, language-only, default) |
| `translator.py` | `MessageBundle` | Collection of translated messages for a specific locale; supports dict and JSON file loading |
| `formatters.py` | `PluralRules` | CLDR-style pluralization engine with per-locale rules (en, es, ru, ar) |
| `formatters.py` | `NumberFormatter` | Locale-aware number formatting with configurable decimal separators and thousands grouping |
| `date_formatter.py` | `DateFormatter` | Locale-aware date, time, and datetime formatting plus human-readable relative time (`relative_time`) |
| `__init__.py` | `init()` / `t()` | Module-level convenience functions for quick translation without explicit Translator instantiation |

## Operating Contracts

- The `Translator` applies a three-step fallback chain: exact locale code, language-only, then default locale; if all miss, the raw key is returned.
- `PluralRules.RULES` maps ISO 639-1 language codes to category functions returning `"one"`, `"few"`, `"other"`, etc.; unknown languages default to the English rule.
- `NumberFormatter.FORMATS` and `DateFormatter.FORMATS` use static lookup tables keyed by language code; unrecognized locales fall back to the `"en"` format.
- `MessageBundle.from_json_file` expects flat `{"key": "translation"}` JSON; nested structures are not supported.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.validation.schemas` (optional `Result`/`ResultStatus` import for cross-module interop)
- **Used by**: CLI modules, website rendering, any user-facing text output needing localization

## Navigation

- **Parent**: [../../AGENTS.md](../../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
