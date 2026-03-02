# Generators -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The generators subpackage provides droid task handlers that produce source code, documentation, and test scaffolding for Codomyrmex modules. Generators are pure functions returning string content or side-effecting functions that write files to disk.

## Architecture

The package is organized into three generator categories, aggregated via `__init__.py`:

1. **Documentation generators** (`documentation.py`) -- quality assessment, coverage scoring, consistency checking
2. **Physical management generators** (`physical.py` -> `physical_generators/`) -- object manager, physics simulation, sensor integration scaffolding
3. **Spatial/3D generators** (`spatial.py`) -- 3D engine, AR/VR, rendering pipeline scaffolding

Each generator follows a common pattern: a function that returns a Python module source string, ready to be written to disk by the droid task runner.

## Key Functions

### `documentation.py`

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `assess_documentation_coverage` | `prompt: str, description: str` | `str` | Scans project for README/AGENTS.md files and scores them 0-100 |
| `add_documentation_quality_methods` | `prompt: str, description: str` | `str` | Creates `quality_assessment.py`, `consistency_checker.py`, and tests under the documentation module |
| `assess_readme_quality` | `content: str, file_path: Path` | `int` | Scores a README based on section presence, code examples, links, length |
| `assess_agents_quality` | `content: str, file_path: Path` | `int` | Scores an AGENTS.md based on agent descriptions, types, technical content |
| `generate_documentation_quality_module` | -- | `str` | Returns source for `DocumentationQualityAnalyzer` class |
| `generate_consistency_checker_module` | -- | `str` | Returns source for `DocumentationConsistencyChecker` class |

### `spatial.py`

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `generate_3d_init_content` | -- | `str` | Returns `__init__.py` source exporting Scene3D, ARSession, RenderPipeline, etc. |
| `generate_3d_engine_content` | -- | `str` | Returns source defining Vector3D, Quaternion, Scene3D, Object3D, Camera3D, Light3D, Material3D, MeshLoader, AnimationController, PhysicsEngine |
| `generate_ar_vr_content` | -- | `str` | Returns source for ARSession, VRRenderer, XRInterface |
| `generate_rendering_content` | -- | `str` | Returns source for ShaderManager, TextureManager, RenderPipeline |
| `create_3d_module_documentation` | `module_path, docs_content, files_created, logger, description` | `str` | Writes architecture.md to disk |

### `physical.py`

Re-exports all 16 symbols from the `physical_generators` subpackage, including `create_physical_management_module`, `generate_physical_manager_content`, `generate_physical_simulation_content`, `generate_sensor_integration_content`, etc.

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`
- **External**: Standard library only (`pathlib`, `os`, `sys`)

## Constraints

- Generator functions must return syntactically valid Python source code.
- File-writing generators use `Path.write_text()` with explicit `encoding="utf-8"`.
- Documentation scoring is heuristic (keyword presence); it does not parse ASTs.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `TodoItem.parse` raises `ValueError` if generator output lines are malformed (upstream contract).
- File I/O errors propagate as `OSError`; callers are expected to handle.
- All errors logged via `logging_monitoring` before propagation.
