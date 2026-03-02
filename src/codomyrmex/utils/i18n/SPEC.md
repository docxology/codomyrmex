# i18n -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Internationalization library providing translation, number formatting, date formatting, and pluralization with locale fallback chains. All formatters are stateless after construction; the `Translator` manages locale-to-bundle mappings.

## Architecture

```
Locale(language, region)
  +-- code -> "en-US"
  +-- from_string("en-US") -> Locale

MessageBundle(messages: dict)
  +-- add(key, value) / get(key, default) / has(key)
  +-- from_json_file(path) / from_dict(d) / to_dict()

Translator(default_locale: Locale)
  +-- add_bundle(locale, bundle)
  +-- translate(key, locale, **kwargs) -> str
  +-- load_directory(path)

PluralRules(locale_code)
  +-- pluralize(count, singular, plural) -> str

NumberFormatter(locale_code)
  +-- format(number) -> str

DateFormatter(locale_code)
  +-- format_date / format_time / format_datetime
  +-- relative_time(dt) -> str
```

## Key Classes

### Translator Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_bundle(locale, bundle)` | `None` | Register messages for a locale |
| `translate(key, locale, **kwargs)` | `str` | Lookup with interpolation and fallback |
| `load_directory(path)` | `None` | Bulk-load `{code}.json` files as bundles |
| `available_locales()` | `list[Locale]` | All registered locales |

### PluralRules

| Locale | Rule |
|--------|------|
| `en`, `es` | `count != 1` selects plural |
| `ru` | Three-form Slavic rules |
| `ar` | Six-form Arabic rules |

### NumberFormatter Locales

| Locale | Decimal | Thousands | Example |
|--------|---------|-----------|---------|
| `en` | `.` | `,` | `1,234.56` |
| `de` | `,` | `.` | `1.234,56` |
| `fr` | `,` | ` ` | `1 234,56` |

### DateFormatter

- Locale patterns for `en`, `de`, `fr`, `es`, `ja`.
- `relative_time(dt)` returns: "just now", "N seconds/minutes/hours/days ago".

## Dependencies

- `json`, `pathlib`, `datetime`, `math` (stdlib)
- `codomyrmex.logging_monitoring`

## Constraints

- Plural rules cover 4 locale families; others fall back to English rules.
- Number formatting handles integers and floats but not currency symbols.
- Date patterns are hardcoded per locale, not loaded from CLDR.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [utils](../README.md)
