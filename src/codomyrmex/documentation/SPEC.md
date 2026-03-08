# documentation - Functional Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `documentation` module manages the project's documentation ecosystem. It handles Docusaurus website generation, documentation aggregation from source code, and quality validation.

## Purpose

The primary purpose of this module is to automate the lifecycle of project documentation, from extraction and aggregation to quality assessment and publication. It ensures that all modules adhere to the RASP (README, AGENTS, SPEC, PAI) standard and maintain high quality scores.

## Design Principles

### Modularity

- **Separation of Concerns**: Generation (`generate_docs`), Aggregation (`aggregate_docs`), and Serving (`serve_static_site`) are distinct functions.
- **Quality Gates**: Quality analysis is decoupled from the build process but can be used as a gate in CI/CD.

### Internal Coherence

- **Unified Quality**: All documentation passes through `QualityAssessment` before deployment.
- **Consistent Structure**: `/docs/modules/` mirrors `src/codomyrmex/`.

## Functional Requirements

1. **Generation**: Extract API documentation from docstrings and generate RASP files for modules.
2. **Aggregation**: Collect module docs into the central website structure.
3. **Serving**: Provide development and production servers for documentation preview.
4. **Quality**: Enforce completeness, accuracy, link validity, and presence of mandatory sections.
5. **PAI Mapping**: Automatically map module capabilities to PAI Algorithm phases.

## Interface Contracts

- `generate_pai_md(module_name, module_dir) -> str`: Generate PAI.md content.
- `audit_rasp(base_dir) -> int`: Audit directory for RASP compliance.
- `DocumentationQualityAnalyzer.analyze_file(path) -> dict`: Get quality metrics for a file.
- `DocumentationConsistencyChecker.check_directory(path) -> ConsistencyReport`: Validate consistency.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **PAI Mapping**: [PAI.md](PAI.md)

- **Parent**: [../SPEC.md](../SPEC.md)
