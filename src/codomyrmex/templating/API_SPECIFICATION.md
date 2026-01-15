# templating - API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The templating module provides template rendering utilities with support for Jinja2 syntax, variable substitution, and template management.

## Classes

### TemplateEngine

Jinja2-based template rendering engine.

```python
from codomyrmex.templating import TemplateEngine
```

#### Constructor

```python
TemplateEngine(
    template_dir: Optional[str] = None,
    auto_escape: bool = True,
    undefined_strict: bool = False
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `template_dir` | `str` | `None` | Directory containing templates |
| `auto_escape` | `bool` | `True` | Enable HTML auto-escaping |
| `undefined_strict` | `bool` | `False` | Raise error on undefined variables |

#### Methods

##### render

```python
def render(template: str, context: Dict[str, Any]) -> str
```

Render template string with context.

| Parameter | Type | Description |
|-----------|------|-------------|
| `template` | `str` | Template string with Jinja2 syntax |
| `context` | `Dict[str, Any]` | Variables for template |

**Returns**: `str` - Rendered output

**Raises**: `TemplatingError` if rendering fails

##### render_file

```python
def render_file(template_name: str, context: Dict[str, Any]) -> str
```

Load and render template from file.

| Parameter | Type | Description |
|-----------|------|-------------|
| `template_name` | `str` | Name of template file in template_dir |
| `context` | `Dict[str, Any]` | Variables for template |

**Returns**: `str` - Rendered output

##### render_to_file

```python
def render_to_file(template: str, context: Dict[str, Any], output_path: str) -> bool
```

Render template and write to file.

##### add_filter

```python
def add_filter(name: str, func: Callable) -> None
```

Add custom filter function.

##### add_global

```python
def add_global(name: str, value: Any) -> None
```

Add global variable accessible in all templates.

---

### TemplateManager

Template collection management utility.

```python
from codomyrmex.templating import TemplateManager
```

#### Methods

##### list_templates

```python
def list_templates() -> List[str]
```

List available templates.

##### get_template

```python
def get_template(name: str) -> str
```

Get template content by name.

##### create_template

```python
def create_template(name: str, content: str) -> bool
```

Create new template.

##### delete_template

```python
def delete_template(name: str) -> bool
```

Delete template by name.

---

## Exceptions

### TemplatingError

```python
from codomyrmex.templating import TemplatingError
```

Raised when template operations fail. Inherits from `CodomyrmexError`.

---

## Usage Examples

### Basic Rendering

```python
from codomyrmex.templating import TemplateEngine

engine = TemplateEngine()

template = "Hello, {{ name }}! You have {{ count }} messages."
result = engine.render(template, {"name": "World", "count": 5})
# Output: "Hello, World! You have 5 messages."
```

### Template Files

```python
from codomyrmex.templating import TemplateEngine

engine = TemplateEngine(template_dir="./templates")

# Render templates/email.html with context
html = engine.render_file("email.html", {
    "user": "John",
    "items": ["Item 1", "Item 2", "Item 3"]
})
```

### Control Structures

```python
template = """
{% for item in items %}
- {{ item.name }}: {{ item.price }}
{% endfor %}

{% if discount %}
Discount applied: {{ discount }}%
{% endif %}
"""

result = engine.render(template, {
    "items": [
        {"name": "Widget", "price": 10.00},
        {"name": "Gadget", "price": 25.00}
    ],
    "discount": 15
})
```

### Custom Filters

```python
from codomyrmex.templating import TemplateEngine

engine = TemplateEngine()

# Add custom filter
engine.add_filter("uppercase", lambda s: s.upper())

template = "{{ message | uppercase }}"
result = engine.render(template, {"message": "hello"})
# Output: "HELLO"
```

### Code Generation

```python
from codomyrmex.templating import TemplateEngine

engine = TemplateEngine()

python_template = '''
class {{ class_name }}:
    """{{ docstring }}"""
    
    def __init__(self{% for attr in attributes %}, {{ attr.name }}: {{ attr.type }}{% endfor %}):
{% for attr in attributes %}
        self.{{ attr.name }} = {{ attr.name }}
{% endfor %}
'''

code = engine.render(python_template, {
    "class_name": "Person",
    "docstring": "Represents a person.",
    "attributes": [
        {"name": "name", "type": "str"},
        {"name": "age", "type": "int"}
    ]
})
```

---

## Template Syntax

### Variables
- `{{ variable }}` - Output variable
- `{{ obj.attribute }}` - Access attribute
- `{{ list[0] }}` - Access list element

### Filters
- `{{ name | upper }}` - Uppercase
- `{{ name | lower }}` - Lowercase
- `{{ name | title }}` - Title case
- `{{ list | join(", ") }}` - Join list
- `{{ value | default("N/A") }}` - Default value

### Control
- `{% if condition %}...{% endif %}` - Conditional
- `{% for item in list %}...{% endfor %}` - Loop
- `{% include "partial.html" %}` - Include template
- `{% macro name(args) %}...{% endmacro %}` - Macro definition

---

## Integration

### Dependencies
- `jinja2` - Template engine
- `codomyrmex.logging_monitoring` for logging
- `codomyrmex.exceptions` for error handling

### Related Modules
- [`documentation`](../documentation/API_SPECIFICATION.md) - Documentation generation
- [`build_synthesis`](../build_synthesis/API_SPECIFICATION.md) - Code generation
- [`module_template`](../module_template/API_SPECIFICATION.md) - Module scaffolding

---

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent**: [codomyrmex](../AGENTS.md)
