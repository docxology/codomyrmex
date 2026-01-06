# Codomyrmex Agents — src/codomyrmex/api

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [API Module Agents](AGENTS.md)
- **Children**:
    - [documentation](documentation/AGENTS.md) - API documentation generation
    - [standardization](standardization/AGENTS.md) - API standardization frameworks
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Unified API module providing comprehensive API functionality for Codomyrmex, including API documentation generation, REST/GraphQL API frameworks, versioning, and OpenAPI specification generation.

## Module Overview

### Key Capabilities
- **API Documentation**: Automated generation of API documentation from code analysis
- **REST API Framework**: Standardized REST API development with routing and middleware
- **GraphQL API Framework**: Type-safe GraphQL schema development and execution
- **API Versioning**: Semantic versioning with migration support and compatibility management
- **OpenAPI Generation**: Unified OpenAPI/Swagger specification generation from multiple sources

### Submodules

#### documentation
- API documentation generation from code
- API specification extraction
- OpenAPI specification generation from documentation
- Documentation validation and export

See [documentation/AGENTS.md](documentation/AGENTS.md) for detailed function signatures.

#### standardization
- REST API framework with routing and middleware
- GraphQL API framework with schema definition
- API versioning and migration management
- OpenAPI specification generation from API instances

See [standardization/AGENTS.md](standardization/AGENTS.md) for detailed function signatures.

## Shared Components

### OpenAPI Generator (`openapi_generator.py`)

The unified OpenAPI generator provides:

- `DocumentationOpenAPIGenerator`: Generates OpenAPI specs from code analysis/documentation
- `StandardizationOpenAPIGenerator`: Generates OpenAPI specs from REST/GraphQL API instances
- `OpenAPISpecification`: Container for OpenAPI specifications
- `APISchema`: Schema definition for documentation

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `openapi_generator.py` – Unified OpenAPI specification generation
- `documentation/` – API documentation generation submodule
- `standardization/` – API standardization frameworks submodule


### Additional Files
- `README.md` – Readme Md
- `documentation` – Documentation
- `standardization` – Standardization

## Operating Contracts

### Universal API Protocols

All API development within the Codomyrmex platform must:

1. **Standard Interfaces** - Use provided REST and GraphQL frameworks for consistency
2. **Version Management** - Implement proper API versioning with migration paths
3. **Documentation** - Generate and maintain accurate OpenAPI specifications
4. **Security** - Follow security best practices for API development
5. **Testing** - Comprehensive testing of all API endpoints and versions

### Module-Specific Guidelines

#### API Documentation
- Automatically extract documentation from code annotations and comments
- Support multiple programming languages and frameworks
- Generate documentation in multiple formats (HTML, Markdown, JSON)
- Include code examples and usage patterns

#### API Standardization
- Use standardized REST and GraphQL frameworks
- Implement proper error handling and status codes
- Follow API versioning best practices
- Generate accurate OpenAPI documentation

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **Documentation Submodule**: [documentation/README.md](documentation/README.md)
- **Standardization Submodule**: [standardization/README.md](standardization/README.md)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src/README.md](../../README.md) - Source code documentation

