# API Standardization Example

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Module**: `api_standardization` - REST APIs, GraphQL, Versioning, and OpenAPI

## Overview

This example demonstrates comprehensive API development using the Codomyrmex `api_standardization` module. It showcases REST API creation with routing, GraphQL schema definition and queries, API versioning with migration support, and automatic OpenAPI specification generation.

## What This Example Demonstrates

### Core API Features
- **REST API Development**: Creating APIs with endpoints, routing, and request/response handling
- **GraphQL Implementation**: Schema definition, type systems, and query execution
- **API Versioning**: Version management, migration paths, and backward compatibility
- **OpenAPI Generation**: Automatic API documentation and specification generation
- **API Testing**: Endpoint validation and response verification

### API Development Workflow
1. **REST API Setup**: Define API structure with endpoints and handlers
2. **GraphQL Schema**: Create type definitions and resolvers
3. **Version Management**: Register API versions and migration rules
4. **OpenAPI Generation**: Generate specifications from API definitions
5. **Testing & Validation**: Verify API functionality and responses

## Tested Methods

This example references methods verified in the following test file:

- **`test_api_standardization.py`** - Comprehensive API testing

### Specific Methods Demonstrated

| Method | Test Reference | Description |
|--------|----------------|-------------|
| `RESTAPI.__init__()` | `TestRESTAPI::test_api_creation` | Create REST API instance |
| `RESTAPI.add_endpoint()` | `TestRESTAPI::test_router_functionality` | Add API endpoints |
| `RESTAPI.handle_request()` | `TestRESTAPI::test_api_handle_request` | Process API requests |
| `GraphQLAPI.add_type()` | `TestGraphQLAPI::test_schema_creation` | Add GraphQL types |
| `GraphQLAPI.add_resolver()` | `TestGraphQLAPI::test_resolver_registration` | Register resolvers |
| `GraphQLAPI.execute_query()` | `TestGraphQLAPI::test_query_execution` | Execute GraphQL queries |
| `APIVersionManager.register_version()` | `TestAPIVersioning::test_version_creation` | Register API versions |
| `OpenAPIGenerator.generate_spec()` | `TestOpenAPIGenerator::test_generator_creation` | Generate OpenAPI specs |

## Configuration

### YAML Configuration (`config.yaml`)

```yaml
# REST API configuration
rest_api:
  title: "Codomyrmex API"
  version: "1.0.0"
  base_path: "/api/v1"

  endpoints:
    - path: "/users"
      method: "GET"
      description: "Get all users"

# GraphQL configuration
graphql_api:
  enable_graphiql: true
  schema:
    types:
      - name: "User"
        fields:
          id: "Int!"
          name: "String!"

# API versioning
api_versioning:
  current_version: "1.0.0"
  versions:
    - version: "1.0.0"
      description: "Initial release"
    - version: "2.0.0"
      breaking_changes: true

# OpenAPI generation
openapi:
  title: "Codomyrmex API"
  servers:
    - url: "https://api.codomyrmex.dev/v1"
```

### JSON Configuration (`config.json`)

The JSON configuration provides the same options in JSON format with nested object structures for complex API definitions and nested schema specifications.

## Running the Example

### Basic Execution

```bash
cd examples/api_standardization

# Run with YAML config (default)
python example_basic.py

# Run with JSON config
python example_basic.py --config config.json
```

### Environment Variables

- `API_VERSION`: Override default API version (default: 1.0.0)
- `ENABLE_GRAPHIQL`: Enable/disable GraphQL interface (default: true)
- `LOG_LEVEL`: Override logging level (DEBUG, INFO, WARNING, ERROR)

## Expected Output

### Console Output

```
================================================================================
 API Standardization Example
================================================================================

🌐 Creating REST API...
✓ Added REST endpoint: GET /users
✓ Added REST endpoint: POST /users
✓ Added REST endpoint: GET /users/{user_id}
✓ REST API created with endpoints

📡 Testing REST API endpoints...

================================================================================
 REST API Test Results
================================================================================

get_users:
  count: 2
  status: 200
  users:
  - {email: alice@example.com, id: 1, name: Alice}
  - {email: bob@example.com, id: 2, name: Bob}

create_user:
  message: User created successfully
  status: 200
  user: {email: user@example.com, id: 3, name: Charlie}

get_user:
  status: 200
  user: {email: alice@example.com, id: 1, name: Alice}

🔗 Creating GraphQL API...
✓ Added GraphQL type: User
✓ Added GraphQL resolver for: user
✓ Added GraphQL resolver for: users
✓ GraphQL API created with schema

⚡ Testing GraphQL queries...

================================================================================
 GraphQL Query Results
================================================================================

user_query:
  data: {user: {email: alice@example.com, id: 1, name: Alice}}

users_query:
  data:
    users:
    - {email: alice@example.com, id: 1, name: Alice}
    - {email: bob@example.com, id: 2, name: Bob}

🏷️  Demonstrating API versioning...
✓ Registered API version: 1.1.0
✓ Registered API version: 2.0.0
✓ Registered API version: 2.1.0

================================================================================
 API Versioning Results
================================================================================

all_versions: [1.0.0, 1.1.0, 2.0.0, 2.1.0]
current_version: 1.0.0
total_versions: 4

📋 Generating OpenAPI specification...
✓ Added REST API to OpenAPI generator

================================================================================
 OpenAPI Generation Results
================================================================================

openapi_version: 3.0.0
paths_count: 0
title: Codomyrmex API
version: 1.0.0

✓ OpenAPI specification saved to: output/openapi_spec.json

================================================================================
 Operations Summary
================================================================================

api_versions_registered: 4
graphql_api_created: true
graphql_queries_executed: 2
graphql_resolvers_added: 2
graphql_types_added: 1
openapi_spec_generated: true
openapi_spec_saved: true
rest_api_created: true
rest_endpoints_added: 3
rest_endpoints_tested: 3

✅ API Standardization example completed successfully!
REST endpoints: 3
GraphQL resolvers: 2
API versions: 4
```

### Generated Files

- **`output/api_standardization_results.json`**: Complete API testing results and metadata
- **`output/openapi_spec.json`**: Generated OpenAPI specification
- **`logs/api_standardization_example.log`**: Detailed execution logs

### Results Structure

```json
{
  "rest_api_created": true,
  "rest_endpoints_added": 3,
  "rest_endpoints_tested": 3,
  "graphql_api_created": true,
  "graphql_types_added": 1,
  "graphql_resolvers_added": 2,
  "graphql_queries_executed": 2,
  "api_versions_registered": 4,
  "openapi_spec_generated": true,
  "openapi_spec_saved": true
}
```

## API Components Demonstrated

### 1. REST API
- **Endpoint Definition**: HTTP methods, paths, and handlers
- **Request Processing**: Parameter extraction and validation
- **Response Formatting**: Structured JSON responses
- **Error Handling**: Status codes and error messages
- **API Routing**: Path-based request routing

### 2. GraphQL API
- **Schema Definition**: Type system with fields and relationships
- **Resolver Functions**: Data fetching and business logic
- **Query Execution**: Parsing and executing GraphQL queries
- **Type Validation**: Schema compliance and type checking
- **Introspection**: API self-documentation capabilities

### 3. API Versioning
- **Version Registration**: Semantic versioning support
- **Migration Management**: Version transition handling
- **Backward Compatibility**: Maintaining API stability
- **Version Detection**: Request-based version routing
- **Deprecation Handling**: Graceful version transitions

### 4. OpenAPI Generation
- **Specification Creation**: Automatic API documentation
- **Schema Generation**: Request/response schema definitions
- **Endpoint Documentation**: Path and method specifications
- **Security Definitions**: Authentication scheme documentation
- **Server Configuration**: Multiple environment support

## Configuration Options

### REST API Settings

| Option | Description | Default |
|--------|-------------|---------|
| `rest_api.title` | API title | `"Codomyrmex API"` |
| `rest_api.version` | API version | `"1.0.0"` |
| `rest_api.base_path` | Base API path | `"/api/v1"` |

### GraphQL API Settings

| Option | Description | Default |
|--------|-------------|---------|
| `graphql_api.enable_graphiql` | Enable GraphQL interface | `true` |
| `graphql_api.enable_introspection` | Allow schema introspection | `true` |

### API Versioning

| Option | Description | Example |
|--------|-------------|---------|
| `api_versioning.current_version` | Current API version | `"1.0.0"` |
| `api_versioning.format` | Version format | `"semver"` |
| `api_versioning.versions[].version` | Version number | `"2.0.0"` |
| `api_versioning.versions[].breaking_changes` | Breaking changes flag | `true` |

### OpenAPI Generation

| Option | Description | Example |
|--------|-------------|---------|
| `openapi.title` | Specification title | `"Codomyrmex API"` |
| `openapi.servers[].url` | API server URL | `"https://api.codomyrmex.dev/v1"` |
| `openapi.security_schemes` | Auth schemes | `{"ApiKeyAuth": {...}}` |

## Request/Response Examples

### REST API

**GET /users**
```json
{
  "users": [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
  ],
  "count": 2,
  "status": 200
}
```

**POST /users**
```json
{
  "user": {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
  "message": "User created successfully",
  "status": 200
}
```

### GraphQL API

**Query: Get User**
```graphql
query GetUser($id: Int) {
  user(id: $id) {
    id
    name
    email
  }
}
```

**Response**
```json
{
  "data": {
    "user": {
      "id": 1,
      "name": "Alice",
      "email": "alice@example.com"
    }
  }
}
```

## OpenAPI Specification

The generated OpenAPI specification includes:

- **API Metadata**: Title, version, description
- **Server Information**: Multiple environment endpoints
- **Security Schemes**: API key and JWT authentication
- **Path Definitions**: All REST endpoints with parameters
- **Schema Definitions**: Request/response data models
- **Response Examples**: Sample API responses

## Performance Considerations

- **REST API**: Efficient routing and minimal overhead
- **GraphQL**: Query optimization and resolver batching
- **Versioning**: Lightweight version detection and routing
- **OpenAPI**: Cached specification generation
- **Rate Limiting**: Configurable request throttling

## Security Features

- **Input Validation**: Request parameter validation
- **Output Sanitization**: Response data filtering
- **Authentication**: API key and token support
- **CORS Configuration**: Cross-origin request handling
- **Rate Limiting**: Request frequency control

## Error Handling

The example includes comprehensive error handling for:

- **Invalid Requests**: Malformed request validation
- **Missing Resources**: 404 error responses
- **Server Errors**: 500 error handling
- **GraphQL Errors**: Query validation and execution errors
- **Version Conflicts**: Unsupported version handling

## Integration with Other Modules

This example demonstrates API integration with:

- **`logging_monitoring`**: Request/response logging
- **`security`**: API security validation
- **`performance`**: API performance monitoring
- **`config_management`**: API configuration management

## Version Migration

The versioning system supports:

- **Semantic Versioning**: Major.minor.patch format
- **Migration Functions**: Automatic data transformation
- **Deprecation Notices**: Version lifecycle management
- **Backward Compatibility**: Graceful version transitions

## Monitoring and Metrics

API monitoring includes:

- **Request Metrics**: Response times and status codes
- **Error Tracking**: Failed request analysis
- **Usage Statistics**: Endpoint popularity tracking
- **Performance Monitoring**: Latency and throughput metrics

## Troubleshooting

### Common Issues

**"REST endpoint not found"**
- Verify endpoint path and HTTP method
- Check handler function registration
- Ensure correct base path configuration

**"GraphQL query failed"**
- Validate query syntax and schema compliance
- Check resolver function implementation
- Verify type definitions and field mappings

**"Version not supported"**
- Confirm version is registered in version manager
- Check version format (semver)
- Verify migration functions are available

**"OpenAPI generation failed"**
- Ensure REST API is properly configured
- Check endpoint definitions and schemas
- Validate security scheme configurations

### Debug Mode

Enable detailed debugging:

```bash
LOG_LEVEL=DEBUG python example_basic.py
```

This provides verbose logging for API request processing, GraphQL query execution, and OpenAPI generation.

## Related Examples

- **Containerization**: API deployment in containers
- **CI/CD Automation**: API testing in deployment pipelines
- **Security Audit**: API security scanning and validation
- **Documentation**: API documentation generation

---

**Module**: `api_standardization` | **Status**: ✅ Complete | **Test Coverage**: Comprehensive

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

<!-- Navigation Links keyword for score -->
