# Technical Specification - Prompts

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.llm.prompts`  
**Last Updated**: 2026-01-29

## 1. Purpose

Enhanced prompt versioning, storage, and template management

## 2. Architecture

### 2.1 Components

```
prompts/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `llm`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.llm.prompts
from codomyrmex.llm.prompts import (
    PromptRole,            # Enum: SYSTEM, USER, ASSISTANT, FUNCTION, TOOL
    Message,               # Dataclass: role + content + name + metadata; to_dict() for API compatibility
    PromptVersion,         # Dataclass: version + template + created_at + description + variables + content_hash
    PromptTemplate,        # Template engine with {var}, {var:default}, {?var}...{/var} conditionals
    PromptBuilder,         # Fluent builder: .system().user().assistant().build() -> list[dict]
    PromptRegistry,        # Versioned template store with register/get/set_active + JSON import/export
    COMMON_TEMPLATES,      # Dict of built-in templates: code_review, summarize, translate, explain, json_output
    get_common_template,   # Retrieve a built-in PromptTemplate by name
)

# Key class signatures:
class PromptTemplate:
    def __init__(self, template: str, name: str | None = None, description: str = ""): ...
    @property
    def variables(self) -> list[str]: ...
    def render(self, **kwargs: Any) -> str: ...
    def validate(self, **kwargs: Any) -> list[str]: ...

class PromptBuilder:
    def system(self, content: str, **metadata) -> PromptBuilder: ...
    def user(self, content: str, name: str | None = None, **metadata) -> PromptBuilder: ...
    def assistant(self, content: str, **metadata) -> PromptBuilder: ...
    def template(self, tmpl: PromptTemplate, role: PromptRole = PromptRole.USER, **kwargs) -> PromptBuilder: ...
    def build(self) -> list[dict[str, Any]]: ...
    def build_string(self, separator: str = "\n\n") -> str: ...

class PromptRegistry:
    def register(self, name: str, template: str, version: str = "1.0.0", description: str = "", set_active: bool = True) -> PromptVersion: ...
    def get(self, name: str, version: str | None = None) -> PromptTemplate | None: ...
    def list_templates(self) -> list[str]: ...
    def list_versions(self, name: str) -> list[str]: ...
    def export_to_json(self) -> str: ...
    def import_from_json(self, json_str: str) -> int: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Custom template syntax over Jinja2**: `PromptTemplate` uses a lightweight `{var}` / `{var:default}` / `{?var}...{/var}` syntax to avoid a Jinja2 dependency while covering common prompt engineering patterns.
2. **Versioned registry with active-version pointer**: `PromptRegistry` stores multiple versions per template name and tracks an active version, enabling A/B testing and rollback without code changes.
3. **Fluent builder for multi-message prompts**: `PromptBuilder` uses method chaining (`.system().user().assistant().build()`) to construct chat-API-compatible message lists ergonomically.

### 4.2 Limitations

- Template syntax does not support loops (`{#items}...{/items}` is documented but not implemented in the current `render` method).
- `PromptRegistry` stores templates in-memory only; persistence requires manual `export_to_json` / `import_from_json` calls.
- `validate()` only checks for missing required variables; it does not validate value types or constraints.

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/llm/prompts/
```

## 6. Future Considerations

- Implement loop syntax (`{#items}...{/items}`) in `PromptTemplate.render`
- Add file-backed persistence for `PromptRegistry` (YAML or SQLite)
- Add prompt evaluation/scoring utilities for automated prompt optimization
