# Agent Guidelines - Documentation

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Documentation generation and quality management for the Codomyrmex platform. Provides Docusaurus-
based website generation, RASP compliance auditing (`audit_rasp_compliance`), documentation
consistency checking (`DocumentationConsistencyChecker`), and quality scoring
(`DocumentationQualityAnalyzer`) on 5 axes: completeness, consistency, technical accuracy,
readability, and structure. Two MCP tools expose generation and auditing to PAI agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports all classes and utility functions |
| `documentation_website.py` | `check_doc_environment()`, `build_static_site()`, `aggregate_docs()`, `assess_site()` |
| `quality/audit.py` | `ModuleAudit`, `audit_documentation()`, `audit_rasp()` — RASP compliance checks |
| `quality/consistency_checker.py` | `DocumentationConsistencyChecker`, `check_documentation_consistency()` |
| `quality/quality_assessment.py` | `DocumentationQualityAnalyzer`, `generate_quality_report()` |
| `maintenance.py` | `finalize_docs()`, `update_root_docs()`, `update_spec()` |
| `pai.py` | `generate_pai_md()`, `update_pai_docs()`, `write_pai_md()` |
| `mcp_tools.py` | MCP tools: `generate_module_docs`, `audit_rasp_compliance` |

## Key Classes

- **ModuleAudit** — RASP completeness audit for modules (`audit_documentation()`)
- **DocumentationConsistencyChecker** — Validate naming conventions, formatting, and internal links
- **DocumentationQualityAnalyzer** — Score documentation on 5 axes (0-100 per axis)
- **`check_doc_environment()`** — Verify Docusaurus dependencies before any build
- **`aggregate_docs()`** — Collect module documentation before site build
- **`audit_rasp()`** — Audit RASP compliance across all modules

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `generate_module_docs` | Generate or update the RASP documentation suite for a specific module | SAFE |
| `audit_rasp_compliance` | Audit the repository for RASP (README, AGENTS, SPEC, PAI) compliance | SAFE |

## Agent Instructions

1. **Check environment first** — Call `check_doc_environment()` before any build operation
2. **Aggregate before build** — Use `aggregate_docs()` to collect module docs before site build
3. **Audit RASP** — Use `audit_rasp_compliance` to verify all modules have complete documentation
4. **Score before publish** — Run `DocumentationQualityAnalyzer` — scores below 60 need improvement
5. **Validate consistency** — Run `DocumentationConsistencyChecker` to catch broken links

## Operating Contracts

- Call `check_doc_environment()` before any `build_static_site()` or `serve_static_site()`
- Use `aggregate_docs()` to collect module documentation before building the site
- Quality scores are 0-100 floats; scores below 60 indicate significant improvement needed
- `DocumentationConsistencyChecker` validates mandatory sections and internal links
- **DO NOT** publish docs without running `audit_rasp_compliance` first

## Common Patterns

```python
from codomyrmex.documentation import (
    check_doc_environment, aggregate_docs, build_static_site,
    DocumentationQualityAnalyzer, audit_rasp
)

# Check environment
env_ok = check_doc_environment()
if not env_ok:
    raise RuntimeError("Documentation environment not ready")

# Aggregate module docs
aggregate_docs()

# Build static site
build_static_site()

# Quality assessment
analyzer = DocumentationQualityAnalyzer()
report = analyzer.analyze("src/codomyrmex/agents/README.md")
print(f"Quality score: {report['overall_score']:.1f}/100")

# RASP audit
results = audit_rasp("src/codomyrmex/")
print(f"Compliant modules: {results['compliant_count']}/{results['total_count']}")
```

## Testing Patterns

```python
from codomyrmex.documentation.quality.audit import ModuleAudit

audit = ModuleAudit("src/codomyrmex/agents")
result = audit.run()
assert result["has_readme"] is True
assert result["has_agents_md"] is True
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `generate_module_docs`, `audit_rasp_compliance` | TRUSTED |
| **Architect** | Read + Design | `audit_rasp_compliance` — RASP compliance review, documentation structure design | OBSERVED |
| **QATester** | Validation | `audit_rasp_compliance` — RASP compliance validation across modules | OBSERVED |
| **Researcher** | Read-only | `audit_rasp_compliance` — inspect documentation compliance state | SAFE |

### Engineer Agent
**Use Cases**: Generating module docs during BUILD, running RASP compliance audits, managing documentation pipeline.

### Architect Agent
**Use Cases**: Reviewing RASP compliance coverage, designing documentation structure, auditing doc consistency.

### QATester Agent
**Use Cases**: Validating RASP compliance across all modules during VERIFY, confirming documentation completeness.

### Researcher Agent
**Use Cases**: Inspecting documentation compliance state to understand project health during analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- **Parent**: [codomyrmex](../README.md)
