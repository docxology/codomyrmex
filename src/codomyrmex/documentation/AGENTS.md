# Codomyrmex Agents — src/codomyrmex/documentation

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Documentation generation and quality management module. Provides Docusaurus-based website generation, documentation consistency checking, quality assessment scoring, and doc aggregation utilities.

## Active Components

- **`documentation_website.py`** — Core website lifecycle: `check_doc_environment()`, `install_dependencies()`, `start_dev_server()`, `build_static_site()`, `serve_static_site()`, `aggregate_docs()`, `validate_doc_versions()`, `assess_site()`
- **`consistency_checker.py`** — `DocumentationConsistencyChecker`: validates naming conventions, formatting standards, and content alignment across markdown files. Produces `ConsistencyReport` with per-file `ConsistencyIssue` entries
- **`quality_assessment.py`** — `DocumentationQualityAnalyzer`: scores documentation on 5 axes (completeness, consistency, technical accuracy, readability, structure). `generate_quality_report()` produces a project-wide quality summary
- **`education/`** — Curriculum and tutorial generation submodule
- **`docusaurus.config.js`** — Docusaurus site configuration
- **`sidebars.js`** — Documentation sidebar navigation structure
- **`docs/`** — Static documentation content for the generated site
- **`scripts/`** — Build and deployment scripts for the documentation site
- **`src/`** — Docusaurus React components and pages
- **`static/`** — Static assets (images, stylesheets) for the documentation site

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Key Parameters | Trust Level |
|------|-------------|----------------|-------------|
| `generate_module_docs` | Generate or update the RASP documentation suite for a specific module | `module_name` | Safe |
| `audit_rasp_compliance` | Audit the repository for RASP (README, AGENTS, SPEC, PAI) compliance | `module_name` (optional; omit for whole repo) | Safe |

## Operating Contracts

- Call `check_doc_environment()` before any build operation to verify Node.js and npm are available.
- Use `aggregate_docs()` to collect module documentation before building the site.
- `DocumentationConsistencyChecker` operates on markdown files only — pass directory paths for recursive checks.
- Quality scores are 0-100 floats; `generate_quality_report()` analyzes key project files (`README.md`, `AGENTS.md`).
- The `education` submodule handles curriculum content separately from the main doc site.

## Common Patterns

```python
from codomyrmex.documentation import (
    check_doc_environment, build_static_site, aggregate_docs,
    DocumentationConsistencyChecker, DocumentationQualityAnalyzer,
    generate_quality_report
)

# Check environment and build site
check_doc_environment()
aggregate_docs("./src")
build_static_site()

# Check documentation consistency
checker = DocumentationConsistencyChecker()
report = checker.check_directory("./docs", recursive=True)
print(f"Files: {report.files_checked}, Issues: {len(report.issues)}")

# Assess documentation quality
analyzer = DocumentationQualityAnalyzer()
scores = analyzer.analyze_file(Path("README.md"))
print(f"Overall: {scores['overall_score']:.1f}/100")

# Generate project-wide quality report
report = generate_quality_report(Path("."))
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `generate_module_docs`, `audit_rasp_compliance`; full Python API | TRUSTED |
| **Architect** | Read + Design | API review, RASP compliance audit, documentation structure design | OBSERVED |
| **QATester** | Validation | `audit_rasp_compliance`; RASP compliance validation across modules | OBSERVED |

### Engineer Agent
**Use Cases**: Generate module documentation, audit RASP compliance across all 88 modules, BUILD phase doc generation

### Architect Agent
**Use Cases**: Review documentation architecture, validate RASP pattern completeness, design doc structure

### QATester Agent
**Use Cases**: RASP compliance audit, verify all 4 doc files exist per module, documentation quality validation

## Navigation Links

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- **Parent**: [codomyrmex](../README.md)
