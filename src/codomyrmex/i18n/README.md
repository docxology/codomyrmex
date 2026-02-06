# Internationalization (i18n) Module

**Version**: v0.1.0 | **Status**: Active

Translation, localization, and message bundle management.

## Quick Start

```python
from codomyrmex.i18n import Translator, Locale, MessageBundle, t

# Create translator
translator = Translator(default_locale=Locale("en"))

# Add bundles
en_bundle = MessageBundle(Locale("en"))
en_bundle.add("greeting", "Hello, {name}!")
en_bundle.add("items", "{count} items")

es_bundle = MessageBundle(Locale("es"))
es_bundle.add("greeting", "¡Hola, {name}!")
es_bundle.add("items", "{count} artículos")

translator.add_bundle(en_bundle)
translator.add_bundle(es_bundle)

# Translate with interpolation
translator.set_locale(Locale("es"))
print(translator.t("greeting", name="World"))  # ¡Hola, World!

# Load from JSON files
translator.load_directory("./locales")  # Loads en.json, es.json, etc.
```

## Exports

| Class/Function | Description |
|----------------|-------------|
| `Locale` | Language/region pair (e.g., `Locale("en", "US")`) |
| `MessageBundle` | Collection of translated messages for one locale |
| `Translator` | Multi-locale translator with fallback chain |
| `PluralRules` | Pluralization for en, es, ru, ar with CLDR rules |
| `NumberFormatter` | Locale-aware number formatting (1,234.56 vs 1.234,56) |
| `init(locale)` | Initialize default translator |
| `t(key, **kwargs)` | Shorthand translation function |

## Pluralization

```python
from codomyrmex.i18n import PluralRules, Locale

forms = {"one": "{n} apple", "other": "{n} apples"}
result = PluralRules.pluralize(Locale("en"), 5, forms)
# "5 apples"
```

## Number Formatting

```python
from codomyrmex.i18n import NumberFormatter, Locale

NumberFormatter.format(Locale("en"), 1234.56)  # "1,234.56"
NumberFormatter.format(Locale("de"), 1234.56)  # "1.234,56"
NumberFormatter.format(Locale("fr"), 1234.56)  # "1 234,56"
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
