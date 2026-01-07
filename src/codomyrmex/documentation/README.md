# documentation

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [scripts](scripts/README.md)
    - [src](src/README.md)
    - [static](static/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Documentation files and guides for documentation.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `bug_taxonomy.md` – File
- `consistency_checker.py` – File
- `coverage_assessment.md` – File
- `docs/` – Subdirectory
- `documentation_website.py` – File
- `docusaurus.config.js` – File
- `package-lock.json` – File
- `package.json` – File
- `quality_assessment.py` – File
- `requirements.txt` – File
- `scripts/` – Subdirectory
- `sidebars.js` – File
- `sidebars.js.backup` – File
- `src/` – Subdirectory
- `static/` – Subdirectory
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.documentation import (
    DocumentationQualityAnalyzer,
    DocumentationConsistencyChecker,
    build_static_site,
    assess_site,
    generate_quality_report,
)

# Check documentation environment
from codomyrmex.documentation import check_doc_environment
env_ok = check_doc_environment()
if not env_ok:
    print("Documentation environment not ready")

# Build static documentation site
build_static_site(output_dir="output/docs")

# Assess documentation quality
analyzer = DocumentationQualityAnalyzer()
report = generate_quality_report("docs/")
print(f"Quality score: {report.score}")

# Check documentation consistency
checker = DocumentationConsistencyChecker()
issues = checker.check_consistency("docs/")
print(f"Consistency issues: {len(issues)}")

# Assess entire site
assessment = assess_site("docs/")
print(f"Site assessment: {assessment.summary}")
```

