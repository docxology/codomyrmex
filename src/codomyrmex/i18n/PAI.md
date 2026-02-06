# Personal AI Infrastructure — i18n Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The i18n (Internationalization) module provides PAI integration for multilingual AI applications, enabling AI agents to work across languages.

## PAI Capabilities

### AI-Generated Translations

Combine i18n with LLM translation:

```python
from codomyrmex.i18n import Translator, MessageBundle
from codomyrmex.llm import LLMClient

# Initialize translator
translator = Translator()
translator.load_bundles("./locales")

# Translate with AI for missing keys
llm = LLMClient()

def get_translation(key, locale):
    # Try cached translation first
    if translator.has_key(key, locale):
        return translator.t(key, locale=locale)
    
    # AI-assisted translation
    english = translator.t(key, locale="en")
    translated = llm.complete(
        f"Translate to {locale}: {english}"
    )
    return translated
```

### Locale-Aware Formatting

Format data for PAI agents across locales:

```python
from codomyrmex.i18n import NumberFormatter, DateFormatter

# Format for user's locale
formatter = NumberFormatter(locale="de-DE")
print(formatter.format(1234.56))  # "1.234,56"

date_fmt = DateFormatter(locale="ja-JP")
print(date_fmt.format(date))  # "2026年2月6日"
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Translator` | Multilingual content |
| `NumberFormatter` | Locale-aware numbers |
| `DateFormatter` | Locale-aware dates |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
