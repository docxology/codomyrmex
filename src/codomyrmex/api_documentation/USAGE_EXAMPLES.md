# API Documentation - Usage Examples

## Basic Usage

### Generate API Documentation

Generate comprehensive API documentation from your codebase:

```python
from codomyrmex.api_documentation import generate_api_docs

# Generate API documentation
docs = generate_api_docs(
    source_path="./src/api",
    output_path="./docs/api",
    title="My REST API",
    version="1.0.0",
    base_url="https://api.example.com/v1"
)

print(f"Generated documentation for {len(docs.endpoints)} endpoints")
```

### Extract API Specifications from Code

Extract API endpoint information from Python files:

```python
from codomyrmex.api_documentation import extract_api_specs

# Extract endpoints from a file
endpoints = extract_api_specs("./src/api/routes.py")

# Display endpoint information
for endpoint in endpoints:
    print(f"{endpoint.method} {endpoint.path}")
    print(f"  Summary: {endpoint.summary}")
    print(f"  Parameters: {len(endpoint.parameters)}")
    print()
```

### Generate OpenAPI/Swagger Specification

Create OpenAPI 3.0 specification for your API:

```python
from codomyrmex.api_documentation import generate_openapi_spec

# Generate OpenAPI spec
spec = generate_openapi_spec(
    source_path="./src/api",
    output_file="openapi.json",
    title="My API",
    version="2.0.0",
    description="Comprehensive API for managing resources"
)

# Spec is automatically saved to openapi.json
print(f"OpenAPI spec version: {spec['openapi']}")
print(f"Number of paths: {len(spec['paths'])}")
```

## Advanced Usage

### Complete Documentation Pipeline

Generate documentation in multiple formats:

```python
from codomyrmex.api_documentation import (
    APIDocumentationGenerator,
    generate_api_docs
)

# Generate documentation
docs = generate_api_docs(
    source_path="./src/api",
    output_path="./docs/api",
    title="My API",
    version="1.0.0",
    formats=['json', 'yaml', 'html', 'markdown']
)

# Access generated documentation
print(f"API Title: {docs.title}")
print(f"Base URL: {docs.base_url}")
print(f"Total Endpoints: {len(docs.endpoints)}")
print(f"Schemas: {len(docs.schemas)}")
```

### Custom Documentation Configuration

Configure documentation generation with custom settings:

```python
from codomyrmex.api_documentation import APIDocumentationGenerator

# Create generator with custom config
generator = APIDocumentationGenerator(
    source_path="./src/api",
    config={
        "include_private": False,
        "include_examples": True,
        "include_schemas": True,
        "group_by_tags": True,
        "authentication": {
            "type": "bearer",
            "scheme": "JWT"
        }
    }
)

# Analyze codebase
generator.analyze_codebase()

# Generate documentation
docs = generator.generate_documentation()

# Export in multiple formats
generator.export(format='html', output_path='./docs/api.html')
generator.export(format='markdown', output_path='./docs/API.md')
```

### Working with OpenAPI Generator

Fine-grained control over OpenAPI specification:

```python
from codomyrmex.api_documentation import (
    OpenAPIGenerator,
    APIEndpoint,
    APISchema
)

# Create OpenAPI generator
generator = OpenAPIGenerator(
    title="My API",
    version="1.0.0",
    description="A comprehensive REST API"
)

# Add custom endpoint
endpoint = APIEndpoint(
    path="/api/users/{id}",
    method="GET",
    summary="Get user by ID",
    description="Retrieve detailed user information",
    parameters=[
        {
            "name": "id",
            "in": "path",
            "required": True,
            "schema": {"type": "integer"},
            "description": "User ID"
        }
    ],
    responses={
        "200": {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/User"}
                }
            }
        },
        "404": {
            "description": "User not found"
        }
    },
    tags=["Users"]
)

generator.add_endpoint(endpoint)

# Add data schema
user_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["id", "name", "email"]
}
generator.add_schema("User", user_schema)

# Generate and export
spec = generator.generate_spec()
generator.export_json("openapi.json")
generator.export_yaml("openapi.yaml")
```

### Validate OpenAPI Specifications

Ensure generated specifications are valid:

```python
from codomyrmex.api_documentation import (
    generate_openapi_spec,
    validate_openapi_spec
)

# Generate specification
spec = generate_openapi_spec(
    source_path="./src/api",
    output_file="openapi.json"
)

# Validate specification
is_valid, errors = validate_openapi_spec(spec, strict=True)

if is_valid:
    print("✅ OpenAPI specification is valid")
else:
    print("❌ OpenAPI specification has errors:")
    for error in errors:
        print(f"  - {error}")
```

## Integration Examples

### With Documentation Website

Generate API documentation for Docusaurus:

```python
from codomyrmex.api_documentation import generate_api_docs

# Generate documentation in markdown format
docs = generate_api_docs(
    source_path="./src/api",
    output_path="./docs/docs/api",
    title="API Reference",
    version="1.0.0",
    formats=['markdown']
)

print("API documentation ready for Docusaurus website")
```

### With CI/CD Pipeline

Automate documentation generation in your build process:

```python
import sys
from codomyrmex.api_documentation import (
    generate_api_docs,
    validate_openapi_spec
)

try:
    # Generate documentation
    docs = generate_api_docs(
        source_path="./src/api",
        output_path="./build/docs/api",
        title="API Documentation",
        version="1.0.0",
        formats=['json', 'html']
    )
    
    # Validate OpenAPI spec
    spec = docs.to_dict()
    is_valid, errors = validate_openapi_spec(spec, strict=True)
    
    if not is_valid:
        print("❌ Documentation validation failed:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    
    print(f"✅ Generated documentation for {len(docs.endpoints)} endpoints")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Documentation generation failed: {e}")
    sys.exit(1)
```

### With Static Analysis

Combine with static analysis for comprehensive documentation:

```python
from codomyrmex.api_documentation import generate_api_docs
from codomyrmex.static_analysis import analyze_code_quality

# Generate API documentation
api_docs = generate_api_docs(
    source_path="./src/api",
    output_path="./docs/api"
)

# Analyze API code quality
quality_results = analyze_code_quality(
    code_path="./src/api",
    analysis_types=["quality", "security", "complexity"]
)

print(f"📚 Generated docs for {len(api_docs.endpoints)} endpoints")
print(f"📊 Code quality score: {quality_results.get('score', 'N/A')}/10")
```

## Real-World Scenarios

### Flask API Documentation

Document a Flask REST API:

```python
from codomyrmex.api_documentation import extract_api_specs, OpenAPIGenerator

# Extract endpoints from Flask app
endpoints = extract_api_specs("./app/routes.py")

# Create OpenAPI generator
generator = OpenAPIGenerator(
    title="Flask API",
    version="1.0.0",
    description="Flask-based REST API"
)

# Add Flask-specific configuration
for endpoint in endpoints:
    generator.add_endpoint(endpoint)

# Generate specification
spec = generator.generate_spec()
generator.export_json("./docs/flask-api.json")

print(f"Documented {len(endpoints)} Flask endpoints")
```

### FastAPI Integration

Generate documentation for FastAPI applications:

```python
from codomyrmex.api_documentation import generate_openapi_spec

# FastAPI automatically generates OpenAPI, but we can enhance it
spec = generate_openapi_spec(
    source_path="./app/routers",
    output_file="enhanced-openapi.json",
    title="FastAPI Application",
    version="2.0.0",
    description="Enhanced API documentation"
)

print("Enhanced FastAPI documentation generated")
```

### Microservices Documentation

Document multiple microservices:

```python
from codomyrmex.api_documentation import generate_api_docs

services = [
    ("./services/users", "User Service"),
    ("./services/products", "Product Service"),
    ("./services/orders", "Order Service")
]

for service_path, service_name in services:
    docs = generate_api_docs(
        source_path=service_path,
        output_path=f"./docs/{service_name.lower().replace(' ', '_')}",
        title=service_name,
        version="1.0.0"
    )
    print(f"✅ {service_name}: {len(docs.endpoints)} endpoints")
```

## Best Practices

### Include Comprehensive Docstrings

Ensure your API code has detailed docstrings:

```python
def get_user(user_id: int) -> dict:
    """
    Retrieve user information by ID.
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        User information dictionary with id, name, email
        
    Raises:
        ValueError: If user_id is invalid
        NotFoundError: If user not found
        
    Example:
        >>> user = get_user(123)
        >>> print(user['name'])
        'John Doe'
    """
    pass
```

### Use Type Hints

Leverage Python type hints for automatic schema generation:

```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str
    age: Optional[int] = None
```

### Organize with Tags

Group related endpoints using tags:

```python
# Tags are automatically extracted from docstrings
# Use consistent naming in your API documentation
```

### Keep Documentation Up to Date

Regenerate documentation as part of your development workflow:

```bash
# In your pre-commit hook or CI/CD pipeline
python -c "from codomyrmex.api_documentation import generate_api_docs; generate_api_docs('./src/api', './docs/api')"
```


