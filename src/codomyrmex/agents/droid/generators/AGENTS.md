# Codomyrmex Agents -- src/codomyrmex/agents/droid/generators

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The generators subpackage contains droid task handler functions that produce source code, documentation, tests, and module scaffolding for Codomyrmex modules. Each generator returns string content or writes files to disk when invoked by the droid TODO runner.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | (re-exports) | Aggregates all generators from `documentation`, `physical`, and `spatial` submodules |
| `documentation.py` | `assess_documentation_coverage` | Scans README, AGENTS.md, and technical docs to produce a scored coverage report |
| `documentation.py` | `add_documentation_quality_methods` | Writes `quality_assessment.py` and `consistency_checker.py` into the documentation module |
| `documentation.py` | `assess_readme_quality` / `assess_agents_quality` / `assess_technical_accuracy` | Heuristic scoring functions evaluating document content against checklists |
| `documentation.py` | `generate_documentation_quality_module` / `generate_consistency_checker_module` | Return full Python module source as strings (DocumentationQualityAnalyzer, DocumentationConsistencyChecker) |
| `physical.py` | (re-exports) | Proxies all symbols from `physical_generators` subpackage for backward compatibility |
| `spatial.py` | `generate_3d_init_content` / `generate_3d_engine_content` / `generate_ar_vr_content` / `generate_rendering_content` | Return source strings for a 3D modeling module (Scene3D, Object3D, Camera3D, RenderPipeline, AR/VR classes) |
| `spatial.py` | `generate_3d_readme_content` / `generate_3d_api_spec` / `generate_3d_tests` | Return documentation and test strings for the 3D module |
| `spatial.py` | `create_3d_module_documentation` | Writes architecture docs to disk and logs creation |

## Operating Contracts

- All generator functions return strings (module source code) or write files and return a summary string.
- Documentation scoring uses heuristic keyword matching; scores range 0-100.
- The `physical.py` module is a re-export layer only; actual logic resides in `physical_generators/` subpackage.
- File-writing generators use `Path.write_text()` with UTF-8 encoding.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config`
- **Used by**: `codomyrmex.agents.droid.run_todo_droid` (via handler resolution), droid TODO processing

## Navigation

- **Parent**: [droid](../README.md)
- **Root**: [Root](../../../../../README.md)
