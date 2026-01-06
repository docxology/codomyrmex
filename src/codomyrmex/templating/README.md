# src/codomyrmex/templating

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Overview

Templating module providing template engine support (Jinja2, Mako) for code generation, documentation templates, and dynamic content for the Codomyrmex platform. This module consolidates `template/` and `module_template/` functionality.

The templating module serves as the templating layer, providing engine-agnostic template interfaces with support for multiple template engines.

## Key Features

- **Multiple Engines**: Support for Jinja2, Mako, and other template engines
- **Template Inheritance**: Support template inheritance and includes
- **Template Caching**: Cache compiled templates for performance
- **Custom Filters**: Register custom template filters
- **Code Generation**: Template-based code generation

## Integration Points

- **module_template/** - Module generation templates
- **documentation/** - Documentation templates
- **code/** - Code generation templates

## Usage Examples

```python
from codomyrmex.templating import TemplateEngine, TemplateManager

# Initialize template engine
engine = TemplateEngine(engine="jinja2")

# Render template from string
template_str = "Hello {{ name }}!"
rendered = engine.render(template_str, {"name": "World"})

# Load and render template from file
template = engine.load_template("template.j2")
rendered = template.render({"name": "World"})

# Register custom filter
engine.register_filter("upper", str.upper)

# Template manager
manager = TemplateManager()
manager.add_template("greeting", template_str)
rendered = manager.render("greeting", {"name": "World"})
```

## Navigation

- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Related Modules**:
    - [module_template](../module_template/README.md) - Module templates
    - [documentation](../documentation/README.md) - Documentation generation

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.templating import TemplateEngine, TemplateManager

engine = TemplateEngine()
# Use engine for template rendering
```

## Contributing

We welcome contributions! Please ensure you:
1. Follow the project coding standards.
2. Add tests for new functionality.
3. Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->

