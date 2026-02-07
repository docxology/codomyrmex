# API Module — Agent Coordination

## Purpose

Unified API Module for Codomyrmex.

## Key Capabilities

- API operations and management

## Agent Usage Patterns

```python
from codomyrmex.api import *

# Agent uses api capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/api/](../../../src/codomyrmex/api/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`APISchema`** — API schema definition for documentation generation.
- **`OpenAPISpecification`** — OpenAPI specification container.
- **`DocumentationOpenAPIGenerator`** — OpenAPI 3.0 specification generator from code analysis/documentation.
- **`StandardizationOpenAPIGenerator`** — Generator for OpenAPI specifications from REST/GraphQL API instances.
- **`generate_openapi_spec()`** — Convenience function to generate OpenAPI specification from endpoints.
- **`validate_openapi_spec()`** — Convenience function to validate OpenAPI specification.
- **`create_openapi_generator()`** — Create a new OpenAPI generator for standardization.
- **`create_openapi_from_rest_api()`** — Create OpenAPI spec from a REST API.
- **`create_openapi_from_graphql_api()`** — Create OpenAPI spec from a GraphQL API.

### Submodules

- `authentication` — Authentication
- `circuit_breaker` — Circuit Breaker
- `documentation` — Documentation
- `mocking` — Mocking
- `pagination` — Pagination
- `rate_limiting` — Rate Limiting
- `standardization` — Standardization
- `webhooks` — Webhooks

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k api -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
