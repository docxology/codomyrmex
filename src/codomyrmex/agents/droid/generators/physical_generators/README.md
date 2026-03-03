# Physical Generators (Consolidated)
**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `physical_generators` subpackage contains the consolidated generator functions used by the Droid agent system to scaffold the `physical_management` module. It provides content generators (producing Python source for object management, physics simulation, and sensor integration), documentation generators (README, API spec, examples, tests, requirements, architecture docs), and task functions that orchestrate full module creation, statistics testing, refactoring, prompt engineering, and Ollama integration.

## PAI Integration

| PAI Phase | Function | Usage |
|-----------|----------|-------|
| BUILD | `create_physical_management_module` | Scaffold a complete physical_management module with 10 files |
| BUILD | `prompt_engineering` | Generate prompt composition utilities and templates |
| BUILD | `ollama_module` | Scaffold Ollama client integration |
| VERIFY | `test_statistics_display` | Run timing benchmarks across simulated tasks |

## Key Exports

| Export | Type | Source File |
|--------|------|-------------|
| `create_physical_management_module` | function | `tasks.py` |
| `test_statistics_display` | function | `tasks.py` |
| `refactor_todo_processing` | function | `tasks.py` |
| `testing_and_docs` | function | `tasks.py` |
| `prompt_engineering` | function | `tasks.py` |
| `ollama_module` | function | `tasks.py` |
| `generate_physical_init_content` | function | `content_generators.py` |
| `generate_physical_manager_content` | function | `content_generators.py` |
| `generate_physical_simulation_content` | function | `content_generators.py` |
| `generate_sensor_integration_content` | function | `content_generators.py` |
| `generate_physical_readme_content` | function | `doc_generators.py` |
| `generate_physical_api_spec` | function | `doc_generators.py` |
| `generate_physical_examples` | function | `doc_generators.py` |
| `generate_physical_tests` | function | `doc_generators.py` |
| `generate_physical_requirements` | function | `doc_generators.py` |
| `generate_physical_docs_content` | function | `doc_generators.py` |

## Quick Start

```python
from codomyrmex.agents.droid.generators.physical_generators import (
    create_physical_management_module,
    generate_physical_manager_content,
)

# Scaffold the entire physical_management module
result = create_physical_management_module(
    prompt="Create physical management",
    description="IoT object management module",
)

# Or generate individual content strings
manager_src = generate_physical_manager_content()
```

## Architecture

```
agents/droid/generators/physical_generators/
    __init__.py               # Re-exports all generators and tasks
    content_generators.py     # Python source generators (init, manager, simulation, sensor)
    doc_generators.py         # Documentation generators (readme, api, examples, tests, reqs, docs)
    tasks.py                  # Task orchestration functions
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/agents/ -k "physical" -v
```

## Navigation

- Parent: [`agents/droid/generators/`](../README.md)
- Sibling: [`physical_gen/`](../physical_gen/README.md)
- Grandparent: [`agents/droid/`](../../README.md)
