# API Documentation Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.api_documentation` module.

## Purpose

This orchestrator provides command-line interface for API documentation generation, OpenAPI spec generation, and validation.

## Usage

```bash
# Generate API documentation
python scripts/api_documentation/orchestrate.py generate-docs --source src/ --output docs/api/

# Extract API specifications
python scripts/api_documentation/orchestrate.py extract-specs --source src/

# Generate OpenAPI specification
python scripts/api_documentation/orchestrate.py generate-openapi --source src/ --output openapi.json

# Validate OpenAPI specification
python scripts/api_documentation/orchestrate.py validate-openapi --spec openapi.json
```

## Commands

- `generate-docs` - Generate comprehensive API documentation
- `extract-specs` - Extract API specifications from code
- `generate-openapi` - Generate OpenAPI/Swagger specification
- `validate-openapi` - Validate OpenAPI specification

## Related Documentation

- **[Module README](../../src/codomyrmex/api_documentation/README.md)**: Complete module documentation
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.api_documentation.generate_api_docs`
- `codomyrmex.api_documentation.extract_api_specs`
- `codomyrmex.api_documentation.generate_openapi_spec`
- `codomyrmex.api_documentation.validate_openapi_spec`

See `codomyrmex.cli.py` for main CLI integration.

