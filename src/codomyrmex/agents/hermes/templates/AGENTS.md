# Hermes Templates — Agentic Guide

**Module**: `codomyrmex.agents.hermes.templates` | **Version**: v1.1.9

## Quick Reference

```python
from codomyrmex.agents.hermes.templates import TemplateLibrary, CODE_REVIEW
```

## Agent Instructions

1. **Use `TemplateLibrary`** for template lookup: `lib.get("code_review")`
2. **`render()`** raises `KeyError` for missing variables — validate first
3. **`render_safe()`** fills missing vars with `{var_name}` placeholders
4. **Custom templates**: Use `lib.register(PromptTemplate(name=..., ...))`
5. **4 built-ins**: `code_review`, `task_decomposition`, `documentation`, `debugging`

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/test_hermes_templates.py -v --no-cov
```
