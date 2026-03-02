# Codomyrmex Agents — src/codomyrmex/documentation

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Documentation generation and quality management module. Provides Docusaurus-based website generation, documentation consistency checking, quality assessment scoring, and doc aggregation utilities.

## Active Components

- **`documentation_website.py`** — Core website lifecycle: `check_doc_environment()`, `install_dependencies()`, `build_static_site()`, `serve_static_site()`, `aggregate_docs()`, `validate_doc_versions()`, `assess_site()`
- **`quality/consistency_checker.py`** — `DocumentationConsistencyChecker`: validates naming conventions, formatting standards, and content alignment.
- **`quality/quality_assessment.py`** — `DocumentationQualityAnalyzer`: scores documentation on 5 axes (completeness, consistency, technical accuracy, readability, structure).
- **`quality/audit.py`** — `ModuleAudit`: Audits modules for RASP completeness.
- **`maintenance.py`** — Utilities for synchronizing `__init__.py` and RASP files across the project.
- **`pai.py`** — PAI-specific documentation generation.

## MCP Tools Available

| Tool | Description | Key Parameters | Trust Level |
|------|-------------|----------------|-------------|
| `generate_module_docs` | Generate or update the RASP documentation suite for a specific module | `module_name` | Safe |
| `audit_rasp_compliance` | Audit the repository for RASP (README, AGENTS, SPEC, PAI) compliance | `module_name` (optional) | Safe |

## Operating Contracts

- Call `check_doc_environment()` before any build operation.
- Use `aggregate_docs()` to collect module documentation before building the site.
- `DocumentationConsistencyChecker` now validates mandatory sections and internal links.
- Quality scores are 0-100 floats; scores below 60 indicate significant improvement needed.

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `generate_module_docs`, `audit_rasp_compliance`; full Python API | TRUSTED |
| **Architect** | Read + Design | API review, RASP compliance audit, documentation structure design | OBSERVED |
| **QATester** | Validation | `audit_rasp_compliance`; RASP compliance validation across modules | OBSERVED |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- **Parent**: [codomyrmex](../README.md)
