# templating - API Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: February 2026

## Overview

The templating module provides template rendering utilities with support for Jinja2 syntax, variable substitution, and template management.

## Classes

### TemplateEngine

Template rendering with a Jinja2 (default) or Mako backend.

```python
from codomyrmex.templating import TemplateEngine
```

#### Constructor

```python
TemplateEngine(engine: str = "jinja2", autoescape: bool = True)
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `engine` | `str` | `"jinja2"` | Backend: `"jinja2"` or `"mako"` |
| `autoescape` | `bool` | `True` | HTML-escape output to prevent XSS |

#### Methods

##### render

```python
def render(template: str, context: dict) -> str
```

Render a template string with context.

| Parameter | Type | Description |
| --- | --- | --- |
| `template` | `str` | Template source in the engine's syntax |
| `context` | `dict` | Variables for the template |

**Returns**: `str` - Rendered output

**Raises**: `TemplatingError` if rendering fails

##### load_template

```python
def load_template(path: str) -> Template
```

Load (and cache) a template file. Render it with `Template.render(context)`.

**Raises**: `TemplatingError` if loading fails

##### register_filter

```python
def register_filter(name: str, func: Callable) -> None
```

Register a custom filter, available to templates rendered or loaded afterwards. `get_filter(name)` returns a registered filter or `None`.

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
def get_template(name: str) -> str | Template | None
```

Get the registered template by name. String registrations return their source;
object registrations return the original ``Template`` instance so its engine
and identity are preserved. Missing names return ``None``. The legacy module
imports ``codomyrmex.templating.template_engine`` and
``codomyrmex.templating.template_manager`` remain supported.

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

engine = TemplateEngine()

# Load templates/email.html and render it with context
template = engine.load_template("./templates/email.html")
html = template.render({
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

# Register a custom filter
engine.register_filter("uppercase", lambda s: s.upper())

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
- [`deployment`](../deployment/API_SPECIFICATION.md) - Code generation
- [`module_template`](../module_template/API_SPECIFICATION.md) - Module scaffolding

---

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent**: [codomyrmex](../AGENTS.md)
