# Codomyrmex Agents -- src/codomyrmex/agents/droid/generators/physical_generators

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The physical_generators subpackage is the modularized implementation of the physical management module generators. It splits generator logic into three files: task handlers (side-effecting functions that write files), content generators (return source strings), and documentation generators (return doc/test/requirements strings).

## Key Components

| File | Function | Role |
|------|----------|------|
| `__init__.py` | (re-exports) | Aggregates all 16 symbols from `tasks`, `content_generators`, and `doc_generators` |
| `tasks.py` | `create_physical_management_module` | Master task handler: creates the `physical_management` module directory and writes 10 files (init, manager, simulation, sensor, README, API spec, examples, tests, requirements, architecture docs) |
| `tasks.py` | `test_statistics_display` | Task handler that benchmarks execution timing across 3 simulated tasks and prints statistics |
| `tasks.py` | `refactor_todo_processing` | Placeholder task handler acknowledging a refactoring request |
| `tasks.py` | `testing_and_docs` | Placeholder task handler acknowledging a testing/documentation request |
| `tasks.py` | `prompt_engineering` | Task handler that writes prompt composition utilities and templates into `ai_code_editing/` |
| `tasks.py` | `ollama_module` | Task handler that scaffolds a minimal Ollama client and integration test |
| `content_generators.py` | `generate_physical_init_content` | Returns `__init__.py` source for the physical management module |
| `content_generators.py` | `generate_physical_manager_content` | Returns source for ObjectType, ObjectStatus, PhysicalObject, ObjectRegistry, PhysicalObjectManager |
| `content_generators.py` | `generate_physical_simulation_content` | Returns source for Vector3D, ForceField, Constraint, PhysicsSimulator |
| `content_generators.py` | `generate_sensor_integration_content` | Returns source for SensorType, DeviceStatus, SensorReading, DeviceInterface, SensorManager, utility classes |
| `doc_generators.py` | `generate_physical_readme_content` | Returns README.md with quick-start examples |
| `doc_generators.py` | `generate_physical_api_spec` | Returns API specification markdown |
| `doc_generators.py` | `generate_physical_examples` | Returns comprehensive usage examples Python file |
| `doc_generators.py` | `generate_physical_tests` | Returns pytest test suite source |
| `doc_generators.py` | `generate_physical_requirements` | Returns requirements.txt listing dependencies |
| `doc_generators.py` | `generate_physical_docs_content` | Returns architecture documentation markdown |

## Operating Contracts

- Task handlers in `tasks.py` accept `prompt: str` and `description: str` keyword arguments (droid runner contract).
- `create_physical_management_module` creates the directory structure and writes all 10 files in a single invocation.
- Content generators and doc generators are pure functions (no side effects) returning `str`.
- `prompt_engineering` and `ollama_module` write files into `ai_code_editing/`, not `physical_management/`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config`
- **Used by**: `physical.py` (parent re-export layer), `physical_gen/` (parallel implementation), droid TODO runner via handler resolution

## Navigation

- **Parent**: [generators](../README.md)
- **Root**: [Root](../../../../../../README.md)
