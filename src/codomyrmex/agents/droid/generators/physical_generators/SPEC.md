# Physical Generators -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The physical_generators subpackage is the canonical, modularized implementation of generators for the physical management module. It separates concerns into task handlers (file-writing side effects), content generators (pure source-string functions), and documentation generators (pure doc/test-string functions).

## Architecture

Three-file separation of concerns, re-exported via `__init__.py`:

1. **tasks.py** -- Side-effecting task handlers invoked by the droid runner (accept `prompt` + `description` kwargs)
2. **content_generators.py** -- Pure functions returning Python source strings for core module files
3. **doc_generators.py** -- Pure functions returning Markdown, test, and requirements strings

The `__init__.py` re-exports all 16 symbols for backward compatibility with the parent `physical.py` module.

## Key Functions

### tasks.py -- Task Handlers

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `create_physical_management_module` | `prompt: str, description: str` | `str` | Creates full module directory tree and writes 10 files (init, object_manager, simulation_engine, sensor_integration, README, API spec, examples, tests, requirements, architecture docs) |
| `test_statistics_display` | `prompt: str, description: str` | `str` | Simulates 3 tasks with `time.sleep`, computes avg/min/max timing statistics |
| `refactor_todo_processing` | `prompt: str, description: str` | `str` | Acknowledges refactoring task (placeholder) |
| `testing_and_docs` | `prompt: str, description: str` | `str` | Acknowledges testing/docs task (placeholder) |
| `prompt_engineering` | `prompt: str, description: str` | `str` | Writes `prompt_composition.py` and 3 template files into `ai_code_editing/` |
| `ollama_module` | `prompt: str, description: str` | `str` | Writes `ollama_client.py`, `ollama_integration.py`, and test file into `ai_code_editing/` |

### content_generators.py -- Content Generators

| Function | Returns | Generated Symbols |
|----------|---------|-------------------|
| `generate_physical_init_content` | `str` | Module `__init__.py` with star imports and `__all__` |
| `generate_physical_manager_content` | `str` | `ObjectType`, `ObjectStatus`, `PhysicalObject`, `ObjectRegistry`, `PhysicalObjectManager` |
| `generate_physical_simulation_content` | `str` | `Vector3D`, `ForceField`, `Constraint`, `PhysicsSimulator` |
| `generate_sensor_integration_content` | `str` | `SensorType`, `DeviceStatus`, `SensorReading`, `DeviceInterface`, `SensorManager`, `PhysicalConstants`, `UnitConverter`, `CoordinateSystem` |

### doc_generators.py -- Documentation Generators

| Function | Returns | Content |
|----------|---------|---------|
| `generate_physical_readme_content` | `str` | README with features, architecture, quick-start examples |
| `generate_physical_api_spec` | `str` | API specification covering all classes, methods, enums |
| `generate_physical_examples` | `str` | Python demo file with 4 example functions |
| `generate_physical_tests` | `str` | Pytest test suite: 5 test classes, integration tests |
| `generate_physical_requirements` | `str` | requirements.txt: numpy, scipy, pydantic, aiohttp, pyserial, sqlalchemy, dev tools |
| `generate_physical_docs_content` | `str` | Architecture document covering data flow, integration points, performance characteristics |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config` (task handlers only)
- **External**: Standard library (`pathlib`, `os`, `sys`, `time`) for task handlers; no imports in content/doc generators

## Constraints

- Task handlers must accept `*, prompt: str, description: str` keyword-only arguments to conform to the droid runner contract.
- Content generators must return syntactically valid Python 3.10+ source.
- `create_physical_management_module` uses `mkdir(exist_ok=True)` and `Path.write_text()` -- it overwrites existing files without warning.
- `prompt_engineering` and `ollama_module` write outside the physical_management module (into `ai_code_editing/`).
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `create_physical_management_module` relies on `Path.mkdir` and `Path.write_text`; `OSError` propagates on filesystem failures.
- Task handlers log via `logger.info` on success; errors propagate to the droid runner which catches and records them in `DroidMetrics`.
- All errors logged via `logging_monitoring` before propagation.
