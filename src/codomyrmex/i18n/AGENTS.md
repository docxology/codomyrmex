# Agent Guidelines - i18n

## Module Overview

Internationalization: translations, pluralization, and number formatting.

## Key Classes

- **Translator** — Message translation with interpolation
- **Locale** — Locale representation (language + region)
- **MessageBundle** — Translation message bundles
- **PluralRules** — Pluralization engine
- **NumberFormatter** — Locale-aware number formatting (classmethod)
- **DateFormatter** — Locale-aware date/time formatting (classmethod)

## Agent Instructions

1. **Extract strings** — Never hardcode user-facing text
2. **Use keys** — Descriptive translation keys
3. **Handle plurals** — Use PluralRules for counts
4. **Format numbers** — Use locale-aware formatting
5. **Fallback chain** — en_US → en → default

## Common Patterns

```python
from codomyrmex.i18n import (
    Translator, Locale, MessageBundle, init, t,
    NumberFormatter, DateFormatter, PluralRules
)
from datetime import date

# Initialize global translator
init(default_locale="fr")

# Add bundles manually or load from directory
tr = Translator(Locale("en"))
en = MessageBundle.from_dict(Locale("en"), {"welcome": "Hello, {name}!"})
tr.add_bundle(en)
tr.t("welcome", name="Jean")  # "Hello, Jean!"

# Load bundles from a directory of JSON files
tr.load_directory("./locales")

# Format numbers (classmethod API)
NumberFormatter.format(Locale("de"), 1234567.89)  # "1.234.567,89"
NumberFormatter.format(Locale("en"), 1000.5, decimals=0)  # "1,001"

# Format dates (classmethod API)
DateFormatter.format_date(Locale("de"), date(2025, 3, 15))  # "15.03.2025"
DateFormatter.format_date(Locale("en"), date(2025, 3, 15))  # "03/15/2025"

# Pluralization
PluralRules.pluralize(Locale("en"), 1, {"one": "1 item", "other": "{n} items"})
```

## Testing Patterns

```python
# Verify translation
tr = Translator(Locale("en"))
bundle = MessageBundle.from_dict(Locale("en"), {"hello": "Hello"})
tr.add_bundle(bundle)
assert tr.t("hello") == "Hello"

# Verify number formatting
assert NumberFormatter.format(Locale("en"), 1000.0, decimals=0) == "1,000"

# Verify date formatting
assert DateFormatter.format_date(Locale("en"), date(2025, 1, 1)) == "01/01/2025"
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
