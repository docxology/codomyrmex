# Personal AI Infrastructure — i18n Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The i18n (Internationalization) module provides PAI integration for multilingual AI applications, enabling AI agents to work across languages.

## PAI Capabilities

### Translation with File-Based Bundles

Load translations from JSON files and translate with interpolation:

```python
from codomyrmex.i18n import Translator, Locale, MessageBundle

# Initialize translator
translator = Translator(Locale("en"))

# Load all JSON bundles from a directory
count = translator.load_directory("./locales")  # -> int (bundles loaded)

# Or add bundles manually
bundle = MessageBundle.from_json_file(Locale("es"), "./locales/es.json")
translator.add_bundle(bundle)

# Translate with interpolation
message = translator.t("welcome", name="Daniel")
# Falls back: exact locale -> language-only -> default -> raw key
```

### Locale-Aware Formatting

Format numbers and dates using classmethod APIs:

```python
from codomyrmex.i18n import NumberFormatter, DateFormatter, Locale
from datetime import date

# Number formatting (classmethod)
NumberFormatter.format(Locale("de"), 1234.56)  # "1.234,56"
NumberFormatter.format(Locale("en"), 1000.0, decimals=0)  # "1,000"

# Date formatting (classmethod)
DateFormatter.format_date(Locale("ja"), date(2026, 2, 6))  # "2026/02/06"
DateFormatter.format_date(Locale("de"), date(2026, 2, 6))  # "06.02.2026"

# Relative time
DateFormatter.relative_time(past_datetime)  # "5 minutes ago"
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Translator` | Multilingual content with fallback |
| `NumberFormatter` | Locale-aware number formatting |
| `DateFormatter` | Locale-aware date/time formatting |
| `PluralRules` | Correct pluralization per locale |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
