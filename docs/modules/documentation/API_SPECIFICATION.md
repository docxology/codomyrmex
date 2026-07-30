# Documentation module API

The source-maintained
[API specification](../../../src/codomyrmex/documentation/API_SPECIFICATION.md)
is authoritative.

## Export groups

| Group | Public exports |
| :--- | :--- |
| Quality | `DocumentationQualityAnalyzer`, `generate_quality_report` |
| Consistency | `ConsistencyIssue`, `ConsistencyReport`, `DocumentationConsistencyChecker`, `check_documentation_consistency` |
| RASP | `ModuleAudit`, `audit_documentation`, `audit_rasp` |
| PAI | `generate_pai_md`, `write_pai_md`, `update_pai_docs` |
| Site lifecycle | `check_doc_environment`, `install_dependencies`, `start_dev_server`, `build_static_site`, `serve_static_site`, `assess_site`, `aggregate_docs`, `validate_doc_versions` |
| Broad maintenance | `update_root_docs`, `finalize_docs`, `update_spec` |

## Exact high-use signatures

```python
audit_documentation(src_dir: Path, report_file: Path) -> None
audit_rasp(base_dir: Path) -> int
generate_pai_md(module_name: str, module_dir: Path) -> str
write_pai_md(module_name: str, module_dir: Path) -> Path
update_pai_docs(
    src_dir: Path,
    apply: bool = False,
    max_lines: int = 55,
) -> None
generate_quality_report(project_path: Path) -> str
check_documentation_consistency(path: str) -> ConsistencyReport
```

## Mutation map

- `generate_pai_md`, `generate_quality_report`, quality checks, and consistency
  checks return in-memory results.
- `audit_documentation` writes the caller-provided report path.
- `write_pai_md` replaces one PAI file.
- `update_pai_docs` is preview-only unless `apply=True`.
- aggregation, package installation, site lifecycle, and root-maintenance
  helpers have filesystem, process, browser, or network side effects.

See the source specification for class fields, legacy Docusaurus behavior, and
error boundaries.

## Navigation

- [Module overview](README.md)
- [MCP tools](MCP_TOOL_SPECIFICATION.md)
- [Source API](../../../src/codomyrmex/documentation/API_SPECIFICATION.md)
