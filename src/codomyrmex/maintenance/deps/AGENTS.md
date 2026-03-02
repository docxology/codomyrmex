# Codomyrmex Agents -- src/codomyrmex/maintenance/deps

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Dependency management tooling for analyzing circular imports, validating
the module dependency hierarchy, checking installed packages and security
vulnerabilities, consolidating per-module `requirements.txt` files into
`pyproject.toml`, and validating the consolidated dependency configuration.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `dependency_analyzer.py` | `DependencyAnalyzer` | AST-based import scanner detecting circular dependencies and hierarchy violations across all modules |
| `dependency_checker.py` | `check_python_version()` | Verify Python >= 3.10 requirement |
| `dependency_checker.py` | `check_dependencies()` | Check importability of core, LLM, analysis, data, and dev packages |
| `dependency_checker.py` | `check_security()` | Run pip-audit/safety for vulnerability scanning |
| `dependency_checker.py` | `check_environment()` | Verify virtual env, uv, git, docker availability |
| `dependency_consolidator.py` | `analyze_dependencies()` | Scan all `requirements.txt` files and identify version conflicts |
| `dependency_consolidator.py` | `generate_pyproject_additions()` | Generate `[project.optional-dependencies]` TOML for pyproject.toml |
| `validate_dependencies.py` | `parse_pyproject_dependencies()` | Parse dependencies from pyproject.toml content |
| `validate_dependencies.py` | `check_version_constraints()` | Verify all dependencies have version constraints |
| `validate_dependencies.py` | `check_duplicates()` | Detect duplicate packages across sections |
| `validate_dependencies.py` | `check_requirements_txt_deprecated()` | Ensure requirements.txt files have deprecation notices |

## Operating Contracts

- `DependencyAnalyzer` uses `ast.parse()` to extract imports -- never executes target code.
- The allowed dependency hierarchy is hard-coded in `DependencyAnalyzer.__init__` (from `relationships.md`).
- `dependency_checker.py` uses subprocess with 300-second timeout for external tool calls.
- All scripts have `main()` entry points and can be run standalone.
- `dependency_consolidator.py` generates reports but does not modify pyproject.toml automatically.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `logging_monitoring.core.logger_config` (setup_logging, get_logger), stdlib `ast`, `subprocess`, `re`, `pathlib`
- **Used by**: CI/CD pipeline validation, maintenance health checks, developer tooling

## Navigation

- **Parent**: [maintenance](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
