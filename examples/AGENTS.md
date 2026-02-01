# Codomyrmex Agents — examples

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

This directory contains executable examples and demonstrations for the Codomyrmex platform. Examples serve as learning resources and templates for common use cases.

## Active Components

| Component | Description |
|-----------|-------------|
| `basic_usage/` | Introductory examples for beginners |
| `advanced/` | Complex workflows for experienced users |
| `ai_workflows/` | AI-assisted development patterns |
| `module_integration/` | Cross-module integration examples |

## Agent Guidelines

### When Working with Examples

1. **Preserve Runnability**: Ensure examples remain executable after modifications
2. **Update Comments**: Keep inline documentation current with code changes
3. **Test Changes**: Run examples to verify they work correctly
4. **Document Dependencies**: List any external requirements clearly

### Example Structure

```
examples/
├── basic_usage/           # Simple, introductory examples
│   ├── hello_codomyrmex.py
│   └── module_demo.py
├── advanced/              # Complex workflows
│   ├── multi_agent.py
│   └── pipeline_example.py
├── ai_workflows/          # AI integration patterns
│   └── llm_code_review.py
└── module_integration/    # Cross-module examples
    └── full_stack_demo.py
```

## Operating Contracts

- Maintain alignment between example code and current API
- Examples should gracefully handle missing dependencies
- Include expected output in docstrings where applicable
- Record example execution in telemetry for usage analytics

## Navigation Links

- **🏠 Project Root**: [../README.md](../README.md) - Main documentation
- **📚 Documentation Examples**: [../docs/examples/](../docs/examples/)
- **🔧 Scripts**: [../scripts/](../scripts/) - Automation utilities
- **📦 Source Code**: [../src/codomyrmex/](../src/codomyrmex/)
