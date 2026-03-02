# Deps -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Dependency management tooling: circular import detection, hierarchy validation,
package health checking, security scanning, requirements consolidation, and
pyproject.toml validation.

## Architecture

Four standalone scripts with distinct responsibilities. `DependencyAnalyzer`
performs static AST analysis of import statements. `dependency_checker` runs
runtime checks via subprocess. `dependency_consolidator` scans requirements.txt
files and generates pyproject.toml additions. `validate_dependencies` validates
the consolidated configuration.

## Key Classes

### `DependencyAnalyzer` (dependency_analyzer.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `extract_imports` | `file_path: Path` | `set[str]` | Extract codomyrmex imports via AST parsing |
| `scan_module` | `module_name: str` | `None` | Scan all .py files in a module for imports |
| `scan_all_modules` | -- | `None` | Scan every module under `src/codomyrmex/` |
| `detect_circular_dependencies` | -- | `list[tuple[str, str]]` | Find bidirectional import pairs |
| `validate_dependency_hierarchy` | -- | `list[dict]` | Check imports against allowed layer rules |
| `analyze` | -- | `dict` | Run complete analysis pipeline |
| `generate_report` | -- | `str` | Markdown report with tables |
| `generate_mermaid_graph` | -- | `str` | Mermaid diagram of violations and cycles |

### Checker Functions (dependency_checker.py)

| Function | Returns | Description |
|----------|---------|-------------|
| `check_python_version()` | `dict` | Python version >= 3.10 check |
| `check_dependencies()` | `dict` | Import checks for core/LLM/analysis/data/dev packages |
| `check_security()` | `dict` | pip-audit and safety vulnerability scan |
| `check_environment()` | `dict` | Virtual env, uv, git, docker availability |
| `fix_dependencies(deps)` | `None` | Install missing packages via uv or pip |

### Consolidator Functions (dependency_consolidator.py)

| Function | Returns | Description |
|----------|---------|-------------|
| `parse_requirements_file(path)` | `list[tuple]` | Parse a requirements.txt into (name, version, source) tuples |
| `find_all_requirements_files(root)` | `list[Path]` | Find all requirements.txt under src/codomyrmex/ |
| `analyze_dependencies(root)` | `dict` | Consolidated dependency info with conflict detection |
| `generate_pyproject_additions(deps, content)` | `tuple[str, dict]` | Generate TOML section for optional-dependencies |

### Validator Functions (validate_dependencies.py)

| Function | Returns | Description |
|----------|---------|-------------|
| `parse_pyproject_dependencies(content)` | `dict` | Parse deps from pyproject.toml content |
| `check_version_constraints(deps)` | `list[str]` | Find deps missing version constraints |
| `check_duplicates(deps)` | `list[str]` | Find duplicate packages across sections |
| `check_requirements_txt_deprecated(root)` | `list[str]` | Check for deprecation notices |

## Dependencies

- **Internal**: `logging_monitoring` (get_logger, setup_logging)
- **External**: stdlib (`ast`, `subprocess`, `re`, `pathlib`, `argparse`, `json`, `sys`)

## Constraints

- `DependencyAnalyzer` skips test files and `__init__.py` during import scanning.
- Subprocess timeout: 300 seconds (5 minutes) for external tool calls.
- No auto-modification of pyproject.toml -- reports only.
- Zero-mock: real AST parsing and subprocess calls, `NotImplementedError` for unimplemented paths.

## Error Handling

- `SyntaxError` in scanned files logged as warning and skipped.
- `subprocess.TimeoutExpired` returns `(False, "", "Command timed out")`.
- All errors logged before propagation.
