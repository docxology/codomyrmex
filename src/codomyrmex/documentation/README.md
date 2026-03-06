# Documentation Module

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Documentation management and website generation module for the Codomyrmex project. Provides tools for checking documentation environments, building and serving static documentation sites (Docusaurus-based), aggregating docs from across modules, validating version consistency, and assessing documentation quality. Integrates with `logging_monitoring` for structured logging and `environment_setup` for dependency verification.

## Purpose

The documentation module exists to ensure high-quality, consistent, and automated documentation across the entire Codomyrmex ecosystem. It provides the infrastructure to generate a unified documentation website and the tools to audit and score documentation quality.

## PAI Integration

The documentation module's `audit_rasp_compliance` MCP tool is invoked by PAI `QATester` agents during the **VERIFY phase** to confirm that new modules follow the RASP documentation pattern (README + AGENTS + SPEC + PAI). `generate_module_docs` is called by `Engineer` agents during BUILD when creating new modules. See [AGENTS.md](AGENTS.md) for the full agent role access matrix.

| Algorithm Phase | Documentation Role |
|----------------|-------------------|
| BUILD | `Engineer` → `generate_module_docs` when scaffolding new modules |
| VERIFY | `QATester` → `audit_rasp_compliance` to gate RASP doc completeness |

## Key Exports

### Website Generation

- **`check_doc_environment()`** -- Verify that documentation tooling (Node.js, npm) is available and properly configured
- **`install_dependencies()`** -- Install documentation site dependencies (npm packages)
- **`start_dev_server()`** -- Launch the Docusaurus development server with hot reload
- **`build_static_site()`** -- Build the static documentation site for production deployment
- **`serve_static_site()`** -- Serve a previously built static site locally for preview

### Documentation Management

- **`aggregate_docs()`** -- Collect and aggregate documentation from all modules into a unified structure
- **`validate_doc_versions()`** -- Check version consistency across module documentation files
- **`assess_site()`** -- Run a comprehensive assessment of the documentation site
- **`print_assessment_checklist()`** -- Display a formatted checklist of documentation assessment results

### Quality Analysis

- **`DocumentationQualityAnalyzer`** -- Analyzes documentation quality across the project using configurable rules and metrics (completeness, consistency, technical accuracy, readability, structure)
- **`generate_quality_report()`** -- Generate a comprehensive quality report for project documentation
- **`DocumentationConsistencyChecker`** -- Checks cross-module documentation for consistency in naming, structure, and references. Now includes mandatory section validation and internal link checking.
- **`audit_rasp()`** -- Specifically audits for RASP compliance across modules.

## Directory Contents

- `PAI.md` – Personal AI Infrastructure documentation
- `README.md` – This file
- `SPEC.md` – Module specification
- `__init__.py` – Package initialization
- `documentation_website.py` - Core website generation functions
- `maintenance.py` - Maintenance utilities for documentation synchronization
- `pai.py` - PAI documentation generation and updates
- `quality/` - Documentation quality and audit sub-package

## Quick Start

```python
from pathlib import Path
from codomyrmex.documentation import DocumentationQualityAnalyzer, DocumentationConsistencyChecker

# Analyze quality of a file
analyzer = DocumentationQualityAnalyzer()
report = analyzer.analyze_file(Path("README.md"))
print(f"Overall Score: {report['overall_score']}")

# Check consistency of a directory
checker = DocumentationConsistencyChecker()
consistency_report = checker.check_directory("src/codomyrmex/documentation")
for issue in consistency_report.issues:
    print(f"[{issue.severity}] {issue.file_path}:{issue.line_number} - {issue.description}")
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/unit/documentation/ -v
```

## Navigation

- **Full Documentation**: [docs/modules/documentation/](../../../docs/modules/documentation/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README.md](../../../README.md)
