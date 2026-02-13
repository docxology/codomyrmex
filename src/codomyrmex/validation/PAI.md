# Personal AI Infrastructure — Validation Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Validation module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.validation import Validator, ValidationManager, ValidationResult, rules, sanitizers, schemas
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `rules` | Function/Constant | Rules |
| `sanitizers` | Function/Constant | Sanitizers |
| `schemas` | Function/Constant | Schemas |
| `Validator` | Class | Validator |
| `ValidationManager` | Class | Validationmanager |
| `ValidationResult` | Class | Validationresult |
| `ValidationWarning` | Class | Validationwarning |
| `ContextualValidator` | Class | Contextualvalidator |
| `ValidationIssue` | Class | Validationissue |
| `TypeSafeParser` | Class | Typesafeparser |
| `ValidationSummary` | Class | Validationsummary |
| `validate` | Function/Constant | Validate |
| `is_valid` | Function/Constant | Is valid |
| `get_errors` | Function/Constant | Get errors |
| `ValidationError` | Class | Validationerror |

*Plus 9 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Validation Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |
| **VERIFY** | Validation and quality checks |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
