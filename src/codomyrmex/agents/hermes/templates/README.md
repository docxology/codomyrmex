# Hermes Prompt Templates

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

**Module**: `codomyrmex.agents.hermes.templates` | **Status**: Active

## Overview

Reusable, parameterized prompt template library for the Hermes agent. Provides built-in templates for common development tasks and supports custom template registration.

## Key Exports

- **`TemplateLibrary`** — Template registry with built-in and custom templates.
- **`PromptTemplate`** — Template model with `render()` and `render_safe()`.
- **`CODE_REVIEW`** — Code review template with language, code, focus areas.
- **`TASK_DECOMPOSITION`** — Task decomposition with context and constraints.
- **`DOCUMENTATION`** — Documentation generation template.
- **`DEBUGGING`** — Debugging template with error, context, expected/actual.

## Quick Start

```python
from codomyrmex.agents.hermes.templates import TemplateLibrary

lib = TemplateLibrary()
template = lib.get("code_review")
prompt = template.render(language="python", code="x = 1", focus_areas="security")
```

## Navigation

- **📁 Parent**: [Hermes](../README.md)
- **🏠 Root**: [codomyrmex](../../../../../README.md)
