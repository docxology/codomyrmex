# Documentation Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Documentation management and website generation module for the Codomyrmex project. Provides tools for checking documentation environments, building and serving static documentation sites (Docusaurus-based), aggregating docs from across modules, validating version consistency, and assessing documentation quality. Integrates with `logging_monitoring` for structured logging and `environment_setup` for dependency verification.

## Key Exports

### Website Generation

- **`check_doc_environment()`** -- Verify that documentation tooling (Node.js, npm) is available and properly configured
- **`run_command_stream_output()`** -- Execute a shell command with real-time streaming output for build processes
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

- **`DocumentationQualityAnalyzer`** -- Analyzes documentation quality across the project using configurable rules and metrics
- **`generate_quality_report()`** -- Generate a comprehensive quality report for project documentation
- **`DocumentationConsistencyChecker`** -- Checks cross-module documentation for consistency in naming, structure, and references

## Directory Contents

- `__init__.py` - Module exports from website, quality, and consistency subsystems
- `documentation_website.py` - Core website generation functions (build, serve, aggregate, validate)
- `consistency_checker.py` - Cross-module documentation consistency validation
- `quality_assessment.py` - Documentation quality analysis and report generation
- `docusaurus.config.js` - Docusaurus site configuration
- `sidebars.js` - Documentation site sidebar structure
- `package.json` - Node.js dependencies for the documentation site
- `scripts/` - Build and validation scripts
- `docs/` - Documentation source content
- `src/` - Docusaurus React components and pages
- `static/` - Static assets for the documentation site
- `CHANGELOG.md` - Module change history
- `SECURITY.md` - Security considerations for documentation generation
- `USAGE_EXAMPLES.md` - Usage examples and patterns
- `bug_taxonomy.md` - Documentation bug classification reference
- `coverage_assessment.md` - Documentation coverage analysis

## Quick Start

```python
from codomyrmex.documentation import ConsistencyIssue, ConsistencyReport

# Create a ConsistencyIssue instance
consistencyissue = ConsistencyIssue()

# Use ConsistencyReport for additional functionality
consistencyreport = ConsistencyReport()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k documentation -v
```

## Navigation

- **Full Documentation**: [docs/modules/documentation/](../../../docs/modules/documentation/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
