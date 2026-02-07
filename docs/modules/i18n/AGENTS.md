# Internationalization (i18n) Module — Agent Coordination

## Purpose

Translation, localization, and message bundle management.

## Key Capabilities

- **Locale**: A locale specification.
- **MessageBundle**: A collection of translated messages.
- **Translator**: Multi-locale translator.
- **PluralRules**: Pluralization rules for different locales.
- **NumberFormatter**: Format numbers for different locales.
- `init()`: init
- `t()`: t
- `code()`: code

## Agent Usage Patterns

```python
from codomyrmex.i18n import Locale

# Agent initializes internationalization (i18n)
instance = Locale()
```

## Integration Points

- **Source**: [src/codomyrmex/i18n/](../../../src/codomyrmex/i18n/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
