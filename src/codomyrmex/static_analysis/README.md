# src/codomyrmex/static_analysis

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Core module providing static code analysis capabilities for the Codomyrmex platform. This module performs automated code quality assessment, security scanning, and complexity analysis across multiple programming languages without executing the code.

The static_analysis module serves as the foundation for code quality assurance, enabling early detection of issues and enforcement of coding standards.

## Analysis Pipeline

```mermaid
graph LR
    A[File Input] --> B[Parser]
    B --> C[Analyzers]
    C --> D[Results]
    D --> E[Reports]

    B --> F[AST Analysis]
    B --> G[Security Scan]
    B --> H[Complexity Check]

    C --> I[Quality Metrics]
    C --> J[Security Findings]
    C --> K[Maintainability Score]
```

The static analysis pipeline processes source code through multiple stages: parsing, analysis, result aggregation, and reporting. Each analyzer focuses on specific aspects of code quality including syntax validation, security vulnerabilities, and maintainability metrics.

## Directory Contents
- `.gitignore` – File
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `SECURITY.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `docs/` – Subdirectory
- `pyrefly_runner.py` – File
- `requirements.txt` – File
- `static_analyzer.py` – File
- `tests/` – Subdirectory

## Navigation
- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Src Hub**: [src](../../../src/README.md)