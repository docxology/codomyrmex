# Demos

Centralized registry and orchestration framework for system demonstrations.

> Source module: [`src/codomyrmex/demos/`](../../../src/codomyrmex/demos/)

## Key Capabilities

- **Decorator-Based Registry**: Mark functions or scripts as demos using the `@demo` decorator
- **Auto-Discovery**: Automatically discover demo functions in specified directories
- **Orchestration**: Run individual demos or full suites through the thin orchestrator
- **Consistent Reporting**: Standardized result reporting across all demo executions

## Quick Start

```python
from codomyrmex.demos import demo, get_registry

@demo(name="my_feature_demo", description="Demonstrates my new feature")
def run_my_demo():
    return True

registry = get_registry()
registry.run_demo("my_feature_demo")
```

## MCP Tools

This module does not currently expose MCP tools. Use the Python API directly.

## References

- [Source README](../../../src/codomyrmex/demos/README.md)
- [AGENTS.md](../../../src/codomyrmex/demos/AGENTS.md)
- [PAI.md](../../../src/codomyrmex/demos/PAI.md)
