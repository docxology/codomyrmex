# Codomyrmex Agents — src/codomyrmex/api

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [documentation](documentation/AGENTS.md)
    - [standardization](standardization/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
API infrastructure including OpenAPI specification generation, API documentation, and API standardization. Provides tools for generating OpenAPI specifications from code, standardizing API interfaces, and maintaining API documentation.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `documentation/` – Directory containing API documentation components
- `openapi_generator.py` – OpenAPI specification generator
- `standardization/` – Directory containing API standardization components

## Key Classes and Functions

### OpenAPIGenerator (`openapi_generator.py`)
- `OpenAPIGenerator()` – OpenAPI specification generator
- `generate_spec(routes: list, title: str = "API", version: str = "1.0.0") -> dict` – Generate OpenAPI specification from routes
- `generate_from_code(code_path: str, output_path: str) -> None` – Generate OpenAPI spec from code
- `validate_spec(spec: dict) -> bool` – Validate OpenAPI specification

### API Documentation (`documentation/`)
- Functions for generating API documentation from OpenAPI specifications
- Support for multiple documentation formats (Markdown, HTML, etc.)

### API Standardization (`standardization/`)
- Tools for standardizing API interfaces
- Validation and compliance checking

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation