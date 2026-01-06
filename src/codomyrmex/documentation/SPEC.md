# documentation - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `documentation` module manages the project's documentation ecosystem. It handles Docusaurus website generation, documentation aggregation from source code, and quality validation.

## Design Principles

### Modularity
- **Separation of Concerns**: Generation (`generate_docs`), Aggregation (`aggregate_docs`), and Serving (`serve_static_site`) are distinct functions.
- **Docusaurus Core**: Leverages Docusaurus for website generation rather than custom static site logic.

### Internal Coherence
- **Unified Quality**: All documentation passes through `QualityAssessment` before deployment.
- **Consistent Structure**: `/docs/modules/` mirrors `src/codomyrmex/`.

## Functional Requirements

1.  **Generation**: Extract API documentation from docstrings.
2.  **Aggregation**: Collect module docs into the central website.
3.  **Serving**: Provide development and production servers.
4.  **Quality**: Enforce completeness, accuracy, and link validity.

## Interface Contracts

- `generate_docs(source_path, output_path, format)`: Create docs from code.
- `assess_site() -> dict`: Get quality metrics.
- `build_static_site()`: Compile production build.

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)

- **Parent**: [../SPEC.md](../SPEC.md)
