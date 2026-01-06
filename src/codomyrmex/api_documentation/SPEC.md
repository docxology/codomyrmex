# api_documentation - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `api_documentation` module automates generation of API reference documents (Markdown, OpenAPI). It introspects code to build comprehensive API specs.

## Design Principles

### Coherence
- **Code as Source of Truth**: Docs are generated from code, not maintained separately.
- **OpenAPI Compliance**: Generated specs adhere to OpenAPI 3.x standards.

## Functional Requirements

1.  **Introspection**: Parse Python modules for functions, classes, and signatures.
2.  **Generation**: Create Markdown and/or OpenAPI YAML/JSON files.

## Interface Contracts

- `doc_generator.py`: Main generation logic.
- `openapi_generator.py`: Specific generator for OpenAPI format.

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)

- **Parent**: [../SPEC.md](../SPEC.md)
