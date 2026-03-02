# AI Agent Guidelines — api/documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Automates API documentation generation by introspecting Python source code via AST parsing to produce OpenAPI 3.0.3 specifications and structured endpoint inventories.

## Key Components

| Component | Role |
|-----------|------|
| `APIEndpoint` | Dataclass capturing a discovered endpoint: `path`, `method`, `summary`, `parameters`, `request_body`, `responses` |
| `APIDocumentation` | Dataclass aggregating `title`, `version`, `description`, `endpoints` list, and `tags` |
| `APIDocumentationGenerator` | Main class: AST-based endpoint discovery, OpenAPI spec generation, JSON/YAML export, spec validation |
| `OpenAPISpecification` | Re-exported from parent `openapi_generator` module |
| `StandardizationOpenAPIGenerator` | Re-exported as `OpenAPIGenerator` for backward compatibility |

## Operating Contracts

- `APIDocumentationGenerator.__init__(source_dir)` takes a directory path to scan.
- `discover_endpoints()` walks Python files using `ast.parse` to find route decorators and handler signatures.
- `generate_openapi_spec()` returns an OpenAPI 3.0.3-compliant dict from discovered endpoints.
- `export_json(path)` and `export_yaml(path)` write specs to disk.
- `validate_spec()` checks the generated spec for completeness issues.
- Code is the source of truth; docs are never maintained separately.

## Integration Points

- **Parent**: `api` module re-exports doc generation capabilities.
- **Consumers**: CI/CD pipelines, `documentation` module, MCP tool `generate_module_docs`.
- **Dependencies**: `ast` (stdlib), parent module's `openapi_generator.py`.

## Navigation

- **Parent**: [api/README.md](../README.md)
- **Sibling**: [SPEC.md](SPEC.md) | [README.md](README.md)
- **Root**: [../../../../README.md](../../../../README.md)
