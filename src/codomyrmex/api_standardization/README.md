# API Standardization Module

The API Standardization module provides a comprehensive framework for building consistent, versioned, and well-documented APIs in Codomyrmex. It supports both REST and GraphQL APIs with automatic OpenAPI specification generation.

## Features

- **REST API Framework**: Complete REST API implementation with routing, middleware, and request/response handling
- **GraphQL API Support**: GraphQL schema definition, resolvers, and query execution
- **API Versioning**: Semantic versioning with backward compatibility and migration support
- **OpenAPI Generation**: Automatic OpenAPI/Swagger specification generation
- **Type Safety**: Strong typing with comprehensive error handling
- **Middleware Support**: Extensible middleware system for cross-cutting concerns

## Components

### REST API (`rest_api.py`)

The REST API framework provides:

- HTTP method routing with parameter extraction
- Middleware pipeline for authentication, logging, etc.
- Structured request/response objects
- Automatic error handling and status codes
- Router composition for modular API design

```python
from codomyrmex.api_standardization import create_api, HTTPMethod, APIResponse

api = create_api("My API", "1.0.0", "My API description")

@api.router.get("/users/{id}")
def get_user(request):
    user_id = request.path_params["id"]
    # ... get user logic ...
    return APIResponse.success({"id": user_id, "name": "John Doe"})

# Handle a request
response = api.handle_request("GET", "/users/123")
```

### GraphQL API (`graphql_api.py`)

The GraphQL API implementation includes:

- Schema definition with object types and fields
- Resolver functions for field resolution
- Mutation support with input validation
- Query complexity analysis
- SDL (Schema Definition Language) generation

```python
from codomyrmex.api_standardization import create_schema, create_object_type, GraphQLAPI

# Create schema
schema = create_schema()

# Define types
user_type = create_object_type("User")
user_type.add_field(GraphQLField("id", "ID", required=True))
user_type.add_field(GraphQLField("name", "String"))

schema.add_type(user_type)
schema.query_type = create_object_type("Query")

# Create API
api = GraphQLAPI(schema)

# Execute query
result = api.execute_query('{ user(id: "1") { id name } }')
```

### API Versioning (`api_versioning.py`)

API versioning provides:

- Multiple version format support (semantic, date, integer)
- Version compatibility checking
- Migration path management
- Request-based version detection
- Deprecation handling

```python
from codomyrmex.api_standardization import create_version_manager, APIVersion, VersionFormat
from datetime import datetime

version_manager = create_version_manager("1.0.0")

# Register versions
version_manager.register_version(APIVersion(
    version="2.0.0",
    format=VersionFormat.SEMVER,
    release_date=datetime.now(),
    description="Major update with breaking changes"
))

# Parse version from request
version = version_manager.parse_version_from_request(
    headers={"X-API-Version": "2.0.0"},
    query_params={}
)
```

### OpenAPI Generation (`openapi_generator.py`)

Automatic OpenAPI specification generation:

- REST API endpoint discovery
- GraphQL schema conversion
- Version information inclusion
- Security scheme definitions
- JSON/YAML output formats

```python
from codomyrmex.api_standardization import generate_openapi_spec

generator = generate_openapi_spec("My API", "1.0.0")
generator.add_rest_api(my_rest_api)
generator.add_graphql_api(my_graphql_api)
generator.add_version_manager(my_version_manager)

spec = generator.generate_spec()
spec.save_to_file("openapi.json", "json")
```

## Usage Examples

### Complete REST API Example

```python
from codomyrmex.api_standardization import create_api, HTTPMethod, APIResponse, APIRouter

# Create API
api = create_api("User Management API", "1.0.0", "Manage users and permissions")

# Define routes
@api.router.get("/users")
def list_users(request):
    """List all users."""
    # Pagination from query params
    limit = int(request.query_params.get("limit", ["10"])[0])
    offset = int(request.query_params.get("offset", ["0"])[0])

    # ... fetch users logic ...
    users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    return APIResponse.success({"users": users, "total": len(users)})

@api.router.post("/users")
def create_user(request):
    """Create a new user."""
    user_data = request.json_body
    if not user_data or "name" not in user_data:
        return APIResponse.bad_request("Name is required")

    # ... create user logic ...
    new_user = {"id": 3, "name": user_data["name"]}
    return APIResponse.success(new_user, HTTPStatus.CREATED)

@api.router.get("/users/{id}")
def get_user(request):
    """Get a specific user."""
    user_id = request.path_params["id"]

    # ... fetch user logic ...
    user = {"id": user_id, "name": "Alice"}
    return APIResponse.success(user)

# Middleware example
def auth_middleware(request):
    """Authentication middleware."""
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return APIResponse.error("Authentication required", HTTPStatus.UNAUTHORIZED)
    # ... validate token ...
    return None  # Continue to next middleware/handler

api.add_middleware(auth_middleware)

# Handle requests
response = api.handle_request("GET", "/users", query_string="limit=5")
print(f"Status: {response.status_code}")
print(f"Body: {response.body}")
```

### GraphQL API with Versioning Example

```python
from codomyrmex.api_standardization import (
    create_schema, create_object_type, GraphQLAPI,
    create_version_manager, generate_openapi_spec
)

# Create GraphQL schema
schema = create_schema()

# Define User type
user_type = create_object_type("User", "User account information")
user_type.add_field(GraphQLField("id", "ID", required=True))
user_type.add_field(GraphQLField("name", "String", required=True))
user_type.add_field(GraphQLField("email", "String"))
user_type.add_field(GraphQLField("createdAt", "String"))

schema.add_type(user_type)

# Define Query type
query_type = create_object_type("Query")
query_type.add_field(GraphQLField("users", "[User]", args={"limit": "Int", "offset": "Int"}))
query_type.add_field(GraphQLField("user", "User", args={"id": "ID!"}))

schema.query_type = query_type

# Create GraphQL API
graphql_api = GraphQLAPI(schema)

# Register resolvers
@graphql_api.resolver("users")
def resolve_users(parent, args, context):
    limit = args.get("limit", 10)
    offset = args.get("offset", 0)
    # ... fetch users from database ...
    return [
        {"id": "1", "name": "Alice", "email": "alice@example.com"},
        {"id": "2", "name": "Bob", "email": "bob@example.com"}
    ]

@graphql_api.resolver("user")
def resolve_user(parent, args, context):
    user_id = args["id"]
    # ... fetch user by ID ...
    return {"id": user_id, "name": "Alice", "email": "alice@example.com"}

# Create version manager
version_manager = create_version_manager("1.0.0")

# Generate OpenAPI specification
openapi_gen = generate_openapi_spec("User API", "1.0.0")
openapi_gen.add_graphql_api(graphql_api)
openapi_gen.add_version_manager(version_manager)

spec = openapi_gen.generate_spec()
print("OpenAPI spec generated:")
print(spec.to_json(indent=2))
```

## Architecture

The API standardization module follows these architectural principles:

1. **Separation of Concerns**: Each component (REST, GraphQL, versioning, OpenAPI) is independent
2. **Composition over Inheritance**: APIs are composed from smaller, reusable components
3. **Type Safety**: Strong typing throughout with comprehensive validation
4. **Extensibility**: Plugin architecture for custom middleware, resolvers, and generators
5. **Standards Compliance**: Full compliance with OpenAPI 3.0.3 and GraphQL specifications

## Integration with Codomyrmex

The API standardization module integrates seamlessly with other Codomyrmex modules:

- **Security Audit**: APIs can be scanned for security vulnerabilities
- **Logging Monitoring**: Automatic request/response logging and metrics
- **Performance**: Built-in performance monitoring and optimization
- **Containerization**: APIs can be easily containerized and deployed
- **Documentation**: Automatic API documentation generation

## Testing

The module includes comprehensive unit tests covering:

- REST API request/response handling
- GraphQL schema validation and execution
- API versioning and migration
- OpenAPI specification generation
- Integration between components

Run tests with:
```bash
pytest testing/unit/test_api_standardization.py
```

## Error Handling

The module provides robust error handling:

- **Validation Errors**: Invalid requests are rejected with appropriate HTTP status codes
- **Schema Errors**: GraphQL schema validation with detailed error messages
- **Version Errors**: Clear error messages for unsupported API versions
- **Generation Errors**: OpenAPI specification validation with fix suggestions

## Performance Considerations

- **Lazy Loading**: Schemas and specifications are generated on-demand
- **Caching**: Compiled regex patterns and parsed schemas are cached
- **Streaming**: Large responses can be streamed for better memory usage
- **Complexity Limits**: GraphQL queries have configurable complexity limits
- **Metrics**: Built-in performance monitoring and alerting

## Security Features

- **Input Validation**: Comprehensive input validation and sanitization
- **Rate Limiting**: Configurable rate limiting for API endpoints
- **CORS Support**: Cross-origin resource sharing configuration
- **Authentication**: Middleware-based authentication and authorization
- **Audit Logging**: Complete audit trail of API access and modifications
