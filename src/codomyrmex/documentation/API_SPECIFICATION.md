# Documentation package API specification

This document describes the exports in
`codomyrmex.documentation.__all__`. Repository-level validation commands under
`scripts/documentation/` are separate CLIs and are not re-exported here.

## Quality and audit interfaces

### `ModuleAudit(path: Path, src_root: Path)`

Audits one Python package directory. Call `audit()` to populate:

- `missing_docs: list[str]`;
- `placeholder_docs: list[str]`;
- `has_py_typed: bool`;
- `init_has_docstring: bool`;
- `files_count: int`.

The required RASP files for this legacy package audit are `README.md`,
`AGENTS.md`, `SPEC.md`, and `PAI.md`.

### `audit_documentation(src_dir: Path, report_file: Path) -> None`

Walks Python packages beneath `src_dir` and writes a Markdown report to
`report_file`. Missing input directories are reported to stdout and do not
raise.

### `audit_rasp(base_dir: Path) -> int`

Prints a RASP presence report. Returns `0` when every discovered package has
all four files and `1` otherwise. The return value is an exit code, not a
missing-file count.

### `DocumentationQualityAnalyzer()`

`analyze_file(file_path: Path) -> dict[str, float]` returns heuristic scores on
a 0–100 scale for completeness, consistency, technical accuracy, readability,
structure, and `overall_score`. A missing file currently returns an error entry
despite the narrower static return annotation.

### `generate_quality_report(project_path: Path) -> str`

Returns a Markdown report string for selected project documentation files. It
does not write the returned report.

### `DocumentationConsistencyChecker(config: dict[str, Any] | None = None)`

- `check_file(file_path: str) -> list[ConsistencyIssue]`
- `check_directory(directory: str, recursive: bool = True) -> ConsistencyReport`

`check_documentation_consistency(path: str) -> ConsistencyReport` is the
convenience wrapper.

### Data classes

```python
ConsistencyIssue(
    file_path: str,
    line_number: int,
    issue_type: str,
    description: str,
    severity: str = "warning",
    suggestion: str | None = None,
)

ConsistencyReport(
    total_files: int,
    files_checked: int,
    issues: list[ConsistencyIssue] = [],
    passed: bool = True,
)
```

## PAI documentation interfaces

### `generate_pai_md(module_name: str, module_dir: Path) -> str`

Parses the target package's `__init__.py` and README and returns source-derived
PAI Markdown without writing it.

### `write_pai_md(module_name: str, module_dir: Path) -> Path`

Writes the generated content to `<module_dir>/PAI.md` and returns that path.
This replaces an existing file.

### `update_pai_docs(src_dir: Path, apply: bool = False, max_lines: int = 55) -> None`

Scans top-level module PAI files. The default is preview-only; `apply=True`
updates files classified as stubs at or below `max_lines`.

## Documentation-site interfaces

These functions operate the package-local Docusaurus surface. The Codomyrmex
repository's authoritative reader build is `make docs-check` with MkDocs.

| Export | Behavior |
| :--- | :--- |
| `check_doc_environment()` | Returns whether Node.js and a supported package manager are available |
| `install_dependencies(package_manager="npm", cwd=None)` | Runs the package-manager install command in the bundled documentation directory or the explicit `cwd` |
| `start_dev_server(package_manager="npm")` | Starts the blocking Docusaurus development server |
| `build_static_site(package_manager="npm")` | Builds the package-local Docusaurus site |
| `serve_static_site(package_manager="npm")` | Serves a previously built package-local site |
| `assess_site()` | Opens the configured URL and prints a manual checklist |
| `aggregate_docs(source_root=None, dest_root=None)` | Copies recognized module docs and may replace destination subtrees |
| `validate_doc_versions()` | Returns `(valid, errors, warnings)` for source/aggregate comparisons |

Package-manager and aggregation operations mutate local state. They are not
part of the default repository documentation gate.

## Root-maintenance interfaces

`update_root_docs(src_dir: Path)`, `finalize_docs(src_dir: Path)`, and
`update_spec(src_dir: Path)` are legacy broad maintenance operations. They can
rewrite repository documentation and package initialization files. Inspect
their implementation and proposed diff before use; do not run them during the
active hand-pass freeze.

## Public import example

```python
from pathlib import Path

from codomyrmex.documentation import (
    DocumentationConsistencyChecker,
    generate_pai_md,
    generate_quality_report,
)

report = generate_quality_report(Path("."))
checker = DocumentationConsistencyChecker()
consistency = checker.check_directory("docs")
pai_preview = generate_pai_md(
    "documentation",
    Path("src/codomyrmex/documentation"),
)
```

## MCP boundary

The two MCP tools are implemented in `mcp_tools.py` and intentionally are not
members of the package `__all__`. See
[MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) for their schemas,
default dry-run behavior, and trust boundary.

## Navigation

- [Package overview](README.md)
- [Functional specification](SPEC.md)
- [MCP tool specification](MCP_TOOL_SPECIFICATION.md)
- [Security](SECURITY.md)
