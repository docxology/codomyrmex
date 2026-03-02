# Demos Module

The `demos` module provides a centralized registry and orchestration framework for system demonstrations across the Codomyrmex workspace.

## Features
- **Centralized Registry**: A decorator-based registry for marking functions or scripts as demos.
- **Discovery**: Automatically discover demos in specific directories.
- **Orchestration**: Run individual demos or suites of demos using the thin orchestrator.
- **Reporting**: Consistent reporting of demo results.

## Usage

### Registering a Demo

```python
from codomyrmex.demos import demo

@demo(name="my_feature_demo", description="Demonstrates my new feature")
def run_my_demo():
    # Demo logic here
    return True
```

### Running Demos

```python
from codomyrmex.demos import get_registry

registry = get_registry()
registry.run_demo("my_feature_demo")
```
