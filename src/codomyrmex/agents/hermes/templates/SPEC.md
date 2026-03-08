# Hermes Templates Specification

**Version**: v1.1.9 | **Status**: Active

## Architecture

```
agents/hermes/templates/
├── __init__.py   # TemplateLibrary + 4 built-in templates
└── models.py     # PromptTemplate dataclass
```

## PromptTemplate API

| Method | Args | Returns | Description |
|--------|------|---------|-------------|
| `render()` | `**kwargs` | `str` | Render with strict variable checking |
| `render_safe()` | `**kwargs` | `str` | Render, leaving missing vars as `{var}` |

## Built-in Templates

| Name | Variables | Purpose |
|------|-----------|---------|
| `code_review` | language, code, focus_areas | Code quality review |
| `task_decomposition` | task_description, context, constraints | Task breakdown |
| `documentation` | doc_type, component_name, description, audience | Doc generation |
| `debugging` | error_message, context, language, code, expected, actual | Bug analysis |

## TemplateLibrary API

| Method | Args | Returns | Description |
|--------|------|---------|-------------|
| `get()` | `name` | `PromptTemplate` | Retrieve by name (raises `KeyError`) |
| `list_templates()` | — | `list[str]` | List all template names |
| `register()` | `template` | `None` | Register custom template |
| `has()` | `name` | `bool` | Check existence |
