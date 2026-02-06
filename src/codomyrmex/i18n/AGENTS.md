# Agent Guidelines - i18n

## Module Overview

Internationalization: translations, pluralization, and number formatting.

## Key Classes

- **Translator** — Message translation
- **Locale** — Locale information
- **MessageBundle** — Translation bundles
- **PluralRules** — Pluralization
- **NumberFormatter** — Locale-aware numbers

## Agent Instructions

1. **Extract strings** — Never hardcode user-facing text
2. **Use keys** — Descriptive translation keys
3. **Handle plurals** — Use PluralRules for counts
4. **Format numbers** — Use locale-aware formatting
5. **Fallback chain** — en-US → en → default

## Common Patterns

```python
from codomyrmex.i18n import Translator, init, t, NumberFormatter

# Initialize translator
init(locale="fr-FR", bundles_path="./locales")

# Translate messages
message = t("welcome_message", name="Jean")
print(message)  # "Bienvenue, Jean!"

# Pluralization
items = t("items_count", count=3)
print(items)  # "3 éléments"

# Format numbers
fmt = NumberFormatter(locale="de-DE")
print(fmt.format_number(1234567.89))  # "1.234.567,89"
print(fmt.format_currency(99.99, "EUR"))  # "99,99 €"
```

## Testing Patterns

```python
# Verify translation
init(locale="en-US")
assert t("hello") == "Hello"

# Verify pluralization
assert "1 item" in t("items", count=1)
assert "5 items" in t("items", count=5)

# Verify number formatting
fmt = NumberFormatter(locale="en-US")
assert fmt.format_number(1000) == "1,000"
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
