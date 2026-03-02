# Codomyrmex Agents -- src/codomyrmex/agents/droid/generators/physical_gen

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The physical_gen subpackage contains modular generator functions that each return a single Python module source string for the physical management module. Each file is responsible for one content domain (manager, simulation, sensor, docs, tests, etc.), and the `__init__.py` aggregates all exports.

## Key Components

| File | Function | Role |
|------|----------|------|
| `__init__.py` | (re-exports) | Aggregates all 10 generator functions from sibling modules |
| `init.py` | `generate_physical_init_content` | Returns `__init__.py` source for the physical management module, exporting PhysicalObjectManager, PhysicsSimulator, SensorManager, and utility classes |
| `manager.py` | `generate_physical_manager_content` | Returns source defining ObjectType, ObjectStatus, PhysicalObject, ObjectRegistry (with grid-based spatial index), and PhysicalObjectManager |
| `simulation.py` | `generate_physical_simulation_content` | Returns source defining Vector3D (with arithmetic operators), ForceField (inverse-square), Constraint, and PhysicsSimulator (Verlet integration) |
| `sensor.py` | `generate_sensor_integration_content` | Returns source defining SensorType, DeviceStatus, SensorReading, DeviceInterface, SensorManager (with pub/sub callbacks), PhysicalConstants, UnitConverter, CoordinateSystem |
| `readme.py` | `generate_physical_readme_content` | Returns README.md content with quick-start examples for object management, physics simulation, and sensor integration |
| `api_spec.py` | `generate_physical_api_spec` | Returns API specification markdown documenting all classes, methods, enums, and utility classes |
| `examples.py` | `generate_physical_examples` | Returns a Python examples file with `object_management_example`, `physics_simulation_example`, `sensor_integration_example`, and `comprehensive_demo` |
| `tests.py` | `generate_physical_tests` | Returns a pytest test suite covering PhysicalObjectManager, PhysicsSimulator, Vector3D, SensorManager, and integration workflows |
| `requirements.py` | `generate_physical_requirements` | Returns a requirements.txt listing numpy, scipy, pydantic, aiohttp, pyserial, sqlalchemy, and dev tools |
| `docs.py` | `generate_physical_docs_content` | Returns architecture documentation covering object lifecycle, physics simulation, sensor integration, and performance characteristics |

## Operating Contracts

- Each generator function takes no arguments and returns a `str` containing syntactically valid Python or Markdown.
- The `manager.py` generator defines a grid-based spatial index in `ObjectRegistry` for O(1) proximity lookups.
- The `simulation.py` generator implements Verlet integration with gravity, force fields, and distance constraints.
- The `sensor.py` generator includes a pub/sub callback system (`subscribe_to_sensor` / `unsubscribe_from_sensor`) with bounded reading history (`max_readings = 10000`).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: No runtime imports (generators return string literals)
- **Used by**: `physical_generators/content_generators.py` (duplicates these functions), `physical_generators/doc_generators.py`, parent `physical.py` re-export layer

## Navigation

- **Parent**: [generators](../README.md)
- **Root**: [Root](../../../../../../README.md)
