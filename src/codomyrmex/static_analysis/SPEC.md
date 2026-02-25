# static_analysis -- Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

AST-based static analysis module for import dependency scanning, architectural
layer classification, layer-boundary violation detection, export auditing, dead
export detection, and unused function detection across the Codomyrmex package.

## Design Principles

- **AST-Only Analysis**: Parses Python source via `ast` module -- never imports analyzed code
- **Zero External Dependencies**: Uses only Python stdlib (`ast`, `os`, `pathlib`)
- **Layer-Aware**: Classifies modules into architectural layers matching the package SPEC
- **Non-Destructive**: Read-only analysis; never modifies analyzed files
- **Codebase-Wide Scope**: Scans all `.py` files recursively, skipping `__pycache__`

## Functional Requirements

### Import Scanning (`scan_imports`)

- Walk all `.py` files recursively under a source directory
- Extract `codomyrmex.*` imports using AST (`ImportFrom` and `Import` nodes)
- Skip `__pycache__` directories and files at the source root level
- Ignore self-imports (module importing itself)
- Return structured edges with fields: `src`, `dst`, `file`, `src_layer`, `dst_layer`

### Single-File Import Extraction (`extract_imports_ast`)

- Parse a single Python file using `ast.parse`
- Extract the second-level module name from `codomyrmex.{module}` imports
- Handle both `from codomyrmex.X import Y` and `import codomyrmex.X` forms
- Return an empty list on `SyntaxError` or `UnicodeDecodeError` (graceful degradation)

### Layer Classification (`get_layer`)

- Map every module name to one of four layers: Foundation, Core, Service, Specialized
- Layer sets are defined as module-level constants matching `SPEC.md`
- Modules not in any set are classified as `"other"`

The canonical layer membership:

| Layer | Modules |
|-------|---------|
| Foundation | `config_management`, `environment_setup`, `logging_monitoring`, `model_context_protocol`, `telemetry`, `terminal_interface` |
| Core | `cache`, `coding`, `compression`, `data_visualization`, `documents`, `encryption`, `git_operations`, `llm`, `networking`, `performance`, `scrape`, `search`, `security`, `serialization`, `static_analysis` |
| Service | `api`, `auth`, `ci_cd_automation`, `cloud`, `containerization`, `database_management`, `deployment`, `documentation`, `logistics`, `orchestrator` |
| Specialized | All remaining modules (~47 modules including `agents`, `cerebrum`, `cli`, `simulation`, etc.) |

### Violation Detection (`check_layer_violations`)

- Assign numeric ranks: Foundation=0, Core=1, Service=2, Specialized=3
- A violation occurs when `src_rank < dst_rank` (lower-layer module imports higher-layer module)
- Return violations with human-readable reason strings
- Do not flag `"other"` layer modules as violations

Violation rules restated:

1. Foundation modules must not import Core, Service, or Specialized modules
2. Core modules must not import Service or Specialized modules
3. Service modules must not import Specialized modules

### Export Auditing (`audit_exports`)

- Discover all module directories with `__init__.py` under the source root
- Skip directories in `SKIP_DIRS`: `__pycache__`, `py.typed`, `.git`, `node_modules`, `htmlcov`
- Parse `__init__.py` for `__all__` definitions via both standard assignment (`__all__ = [...]`) and annotated assignment
- Report modules missing `__all__` with issue type `MISSING_ALL`

### Single-File Export Check (`check_all_defined`)

- Parse a single `__init__.py` file
- Return `(has_all: bool, names: list[str] | None)`
- Extract string constant values from `ast.List` or `ast.Tuple` in the `__all__` assignment
- Return `(True, None)` if `__all__` is assigned but not parseable as a list literal
- Return `(False, None)` if no `__all__` assignment exists

### Dead Export Detection (`find_dead_exports`)

- Collect all imported names from `codomyrmex.*` imports across the entire codebase
- For each module with a parseable `__all__`, check which exported names are never imported elsewhere
- Return findings with `module`, `export_name`, and `detail` fields

### Unused Function Detection (`find_unused_functions`)

- Collect all top-level public function definitions (not starting with `_`)
- Collect all `ast.Name` references across the codebase
- Report functions whose names never appear as references
- Skip functions in `SKIP_DIRS` paths

### Unified Audit (`full_audit`)

- Run `audit_exports`, `find_dead_exports`, and `find_unused_functions` in sequence
- Return a dict with keys: `missing_all`, `dead_exports`, `unused_functions`, `summary`
- The `summary` sub-dict provides counts: `modules_missing_all`, `dead_export_count`, `unused_function_count`

## Output Formats

All functions return Python data structures (lists of dicts or tuples). There is
no file-based output format -- consumers handle serialization.

| Function | Return Type |
|----------|-------------|
| `scan_imports` | `list[dict[str, Any]]` -- edge dicts |
| `check_layer_violations` | `list[dict[str, Any]]` -- violation dicts (superset of edge fields + `reason`) |
| `extract_imports_ast` | `list[str]` -- module names |
| `audit_exports` | `list[dict[str, str]]` -- finding dicts |
| `check_all_defined` | `tuple[bool, list[str] \| None]` |
| `find_dead_exports` | `list[dict[str, Any]]` |
| `find_unused_functions` | `list[dict[str, Any]]` |
| `full_audit` | `dict[str, Any]` |

## Quality Requirements

- **Test Coverage**: Tests use real source directories; no mocks per zero-mock policy
- **Type Hints**: All public functions have full type annotations
- **Documentation**: Complete docstrings on all public functions
- **Error Handling**: `SyntaxError` and `UnicodeDecodeError` in parsed files are caught and result in empty returns, not crashes

## Navigation

- **Parent**: [../SPEC.md](../SPEC.md) -- Package specification
- **README**: [README.md](README.md) -- Module overview
- **AGENTS**: [AGENTS.md](AGENTS.md) -- Agent coordination
