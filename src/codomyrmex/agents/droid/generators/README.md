# Droid Task Generators

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The generators sub-package provides code generation functions for the droid task system. Each generator module produces complete Python source code, documentation, tests, and project scaffolding for specific domains. Generators output raw source strings that the droid orchestrator writes to disk during task execution.

Three generator domains are implemented:

- **Documentation** -- Assesses documentation coverage, generates quality analysis modules and consistency checkers
- **Physical** -- Scaffolds the physical_management module (sensors, simulation, hardware integration)
- **Spatial** -- Scaffolds the 3D modeling module (engine, AR/VR, rendering pipeline)

## Architecture

```
generators/
  __init__.py              # Re-exports all generators from sub-modules
  documentation.py         # Documentation quality assessment generators
  physical.py              # Re-exports from physical_generators/ sub-package
  spatial.py               # 3D engine, AR/VR, rendering pipeline generators
  physical_generators/     # Physical management module generators (sub-package)
  physical_gen/            # Legacy physical generation utilities
```

## Key Exports

### documentation.py

| Function | Description |
|----------|-------------|
| `assess_documentation_coverage(prompt, description)` | Scans the project for README, AGENTS.md, and technical docs. Produces a scored coverage report written to `documentation/coverage_assessment.md`. |
| `add_documentation_quality_methods(prompt, description)` | Generates `quality_assessment.py` and `consistency_checker.py` modules in the documentation package, plus test files. Updates `__init__.py` with new exports. |
| `assess_readme_quality(content, file_path)` | Scores a README 0-100 based on sections, code examples, links, length, metadata. |
| `assess_agents_quality(content, file_path)` | Scores an AGENTS.md 0-100 based on agent descriptions, technical content, examples. |
| `assess_technical_accuracy(content, file_path)` | Scores technical docs 0-100 based on terms, code references, formatting, links. |
| `generate_quality_tests()` | Returns a string containing pytest test classes for quality assessment modules. |
| `generate_documentation_quality_module()` | Returns the full source of `DocumentationQualityAnalyzer` with 5 quality metrics. |
| `generate_consistency_checker_module()` | Returns the full source of `DocumentationConsistencyChecker` with naming/formatting/content/structure checks. |

### physical.py

Re-exports all functions from `physical_generators/` sub-package:

| Function | Description |
|----------|-------------|
| `create_physical_management_module` | Orchestrates full module creation (init, manager, simulation, sensors, docs, tests) |
| `generate_physical_init_content()` | Returns `__init__.py` source for the physical_management module |
| `generate_physical_manager_content()` | Returns the PhysicalManager class source |
| `generate_physical_simulation_content()` | Returns the physics simulation engine source |
| `generate_sensor_integration_content()` | Returns the sensor integration layer source |
| `generate_physical_readme_content()` | Returns README.md content for the module |
| `generate_physical_api_spec()` | Returns API_SPECIFICATION.md content |
| `generate_physical_examples()` | Returns usage example scripts |
| `generate_physical_tests()` | Returns pytest test suite source |
| `generate_physical_requirements()` | Returns requirements.txt content |
| `generate_physical_docs_content()` | Returns architecture documentation |
| `test_statistics_display` | Display helper for test statistics |
| `refactor_todo_processing` | TO-DO processing refactoring utilities |
| `testing_and_docs` | Combined testing and documentation generation |
| `prompt_engineering` | Prompt template generation utilities |
| `ollama_module` | Ollama LLM integration module generation |

### spatial.py

| Function | Description |
|----------|-------------|
| `create_3d_module_documentation(module_path, docs_content, files_created, logger, description)` | Writes architecture docs and logs module creation |
| `generate_3d_init_content()` | Returns `__init__.py` with Scene3D, Object3D, Camera3D, AR/VR/XR, and RenderPipeline exports |
| `generate_3d_engine_content()` | Returns core engine: Vector3D, Quaternion, Scene3D, Object3D, Camera3D, Light3D, Material3D, MeshLoader, AnimationController, PhysicsEngine |
| `generate_ar_vr_content()` | Returns AR/VR/XR support: ARSession, VRRenderer, XRInterface |
| `generate_rendering_content()` | Returns rendering pipeline: ShaderManager, TextureManager, RenderPipeline |
| `generate_3d_readme_content()` | Returns README.md content for the 3D module |
| `generate_3d_api_spec()` | Returns API specification for all 3D classes |
| `generate_3d_examples()` | Returns usage example scripts (basic scene, AR, VR) |
| `generate_3d_tests()` | Returns pytest test suite for Scene3D, Object3D, Vector3D, RenderPipeline |
| `generate_3d_requirements()` | Returns requirements.txt (numpy, pyopengl, moderngl, trimesh, etc.) |
| `generate_3d_docs_content()` | Returns architecture documentation covering data flow, integration points, performance |

## Usage

Generators are invoked by the droid task system during module scaffolding:

```python
from codomyrmex.agents.droid.generators import (
    generate_3d_init_content,
    generate_3d_engine_content,
    generate_physical_manager_content,
    assess_documentation_coverage,
)

# Generate a 3D engine source file
engine_source = generate_3d_engine_content()
Path("spatial/three_d/engine_3d.py").write_text(engine_source)

# Generate physical management module
manager_source = generate_physical_manager_content()
Path("physical_management/manager.py").write_text(manager_source)

# Assess documentation coverage
result = assess_documentation_coverage(
    prompt="Check docs", description="Coverage audit"
)
print(result)  # "Documentation coverage assessed: 75.0/100"
```

## Design Principles

1. **Pure string generators** -- Each function returns a string of valid Python source code. No filesystem side effects except where explicitly documented (e.g., `assess_documentation_coverage` writes a report file).
2. **Self-contained output** -- Generated modules include all necessary imports, class definitions, and `__all__` exports. They do not require additional scaffolding.
3. **Test-inclusive** -- Every domain generator includes a companion test generator that produces a complete pytest test suite for the generated module.
4. **Documentation-inclusive** -- Each domain includes README, API spec, and architecture doc generators alongside the code generators.

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/demos/ -v
```

Generator outputs can be validated by executing the generated test suites against the generated source.

## Navigation

- [AGENTS](AGENTS.md) | [SPEC](SPEC.md) | [Parent](../README.md)
