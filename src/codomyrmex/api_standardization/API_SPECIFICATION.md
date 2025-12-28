# API Standardization Module - API Specification

## Overview

The API Standardization module provides a unified interface for building REST APIs, GraphQL APIs, managing API versions, and generating OpenAPI specifications. This document defines the complete API surface and contracts.

## REST API Interface

### RESTAPI Class

Main REST API server class that handles HTTP requests and routes them to appropriate handlers.

#### Constructor
```python
RESTAPI(title: str, version: str, description: str = "")
```

#### Methods

##### `add_middleware(middleware: Callable[[APIRequest], Optional[APIResponse]]) -> None`
Add global middleware to the request pipeline.

**Parameters:**
- `middleware`: Function that takes an `APIRequest` and returns an optional `APIResponse`

##### `add_router(router: APIRouter) -> None`
Add a router to the API.

**Parameters:**
- `router`: `APIRouter` instance to add

##### `handle_request(method: str, path: str, headers: Optional[Dict[str, str]] = None, body: Optional[bytes] = None, query_string: Optional[str] = None) -> APIResponse`
Handle an incoming HTTP request.

**Parameters:**
- `method`: HTTP method (GET, POST, etc.)
- `path`: Request path
- `headers`: Request headers dictionary
- `body`: Request body as bytes
- `query_string`: Query string

**Returns:** `APIResponse` object

##### `get_metrics() -> Dict[str, Any]`
Get API performance metrics.

**Returns:** Dictionary with request counts, error rates, etc.

##### `get_endpoints() -> List[APIEndpoint]`
Get all registered endpoints.

**Returns:** List of `APIEndpoint` objects

### APIRouter Class

Router for managing API endpoints with support for nested routing.

#### Constructor
```python
APIRouter(prefix: str = "")
```

#### Methods

##### `get(path: str, **kwargs) -> Callable`
Decorator for GET endpoints.

##### `post(path: str, **kwargs) -> Callable`
Decorator for POST endpoints.

##### `put(path: str, **kwargs) -> Callable`
Decorator for PUT endpoints.

##### `delete(path: str, **kwargs) -> Callable`
Decorator for DELETE endpoints.

##### `patch(path: str, **kwargs) -> Callable`
Decorator for PATCH endpoints.

##### `add_endpoint(endpoint: APIEndpoint) -> None`
Add an endpoint to the router.

##### `add_router(router: APIRouter) -> None`
Add a sub-router.

##### `match_endpoint(method: HTTPMethod, path: str) -> Optional[Tuple[APIEndpoint, Dict[str, str]]]`
Match a request to an endpoint.

**Returns:** Tuple of (endpoint, path_parameters) or None

### APIRequest Class

Represents an incoming API request.

#### Properties
- `method: HTTPMethod` - HTTP method
- `path: str` - Request path
- `headers: Dict[str, str]` - Request headers
- `query_params: Dict[str, List[str]]` - Parsed query parameters
- `body: Optional[bytes]` - Raw request body
- `path_params: Dict[str, str]` - URL path parameters
- `context: Dict[str, Any]` - Request context data
- `json_body: Optional[Dict[str, Any]]` - Parsed JSON body (property)

### APIResponse Class

Represents an API response.

#### Class Methods

##### `success(data: Any = None, status_code: HTTPStatus = HTTPStatus.OK) -> APIResponse`
Create a success response.

##### `error(message: str, status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR) -> APIResponse`
Create an error response.

##### `not_found(resource: str = "Resource") -> APIResponse`
Create a not found response.

##### `bad_request(message: str = "Bad request") -> APIResponse`
Create a bad request response.

#### Properties
- `status_code: HTTPStatus` - HTTP status code
- `body: Optional[Union[str, bytes, Dict[str, Any]]]` - Response body
- `headers: Dict[str, str]` - Response headers
- `content_type: str` - Content type

### APIEndpoint Class

Represents an API endpoint configuration.

#### Constructor
```python
APIEndpoint(
    path: str,
    method: HTTPMethod,
    handler: Callable[[APIRequest], APIResponse],
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: List[str] = None,
    parameters: List[Dict[str, Any]] = None,
    request_body: Optional[Dict[str, Any]] = None,
    responses: Dict[int, Dict[str, Any]] = None,
    middleware: List[Callable[[APIRequest], Optional[APIResponse]]] = None
)
```

## GraphQL API Interface

### GraphQLAPI Class

Main GraphQL API class for executing queries and mutations.

#### Constructor
```python
GraphQLAPI(schema: GraphQLSchema)
```

#### Methods

##### `register_resolver(type_name: str, field_name: str, resolver: GraphQLResolver) -> None`
Register a field resolver.

##### `register_mutation(mutation: GraphQLMutation) -> None`
Register a mutation.

##### `execute_query(query: str, variables: Optional[Dict[str, Any]] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Execute a GraphQL query.

**Returns:** Dictionary with 'data' and/or 'errors' keys

##### `get_schema_sdl() -> str`
Get the GraphQL schema as SDL string.

##### `get_metrics() -> Dict[str, Any]`
Get API metrics.

##### `validate_query(query: str) -> List[str]`
Validate a GraphQL query.

**Returns:** List of validation error messages

### GraphQLSchema Class

GraphQL schema definition container.

#### Methods

##### `add_type(type_def: GraphQLObjectType) -> None`
Add a type to the schema.

##### `get_type(name: str) -> Optional[GraphQLObjectType]`
Get a type by name.

##### `generate_sdl() -> str`
Generate GraphQL Schema Definition Language.

### GraphQLObjectType Class

Represents a GraphQL object type.

#### Methods

##### `add_field(field: GraphQLField) -> None`
Add a field to the type.

##### `get_field(name: str) -> Optional[GraphQLField]`
Get a field by name.

### GraphQLResolver Class

Field resolver for GraphQL.

#### Constructor
```python
GraphQLResolver(field_name: str, resolver_func: Callable, complexity: int = 1)
```

#### Methods

##### `resolve(parent: Any, args: Dict[str, Any], context: Dict[str, Any]) -> Any`
Resolve the field value.

### GraphQLMutation Class

GraphQL mutation definition.

#### Constructor
```python
GraphQLMutation(
    name: str,
    input_type: GraphQLObjectType,
    output_type: Union[str, GraphQLObjectType],
    resolver: Callable,
    description: Optional[str] = None
)
```

#### Methods

##### `execute(input_data: Dict[str, Any], context: Dict[str, Any]) -> Any`
Execute the mutation.

## API Versioning Interface

### APIVersionManager Class

Manages API versions and versioned endpoints.

#### Constructor
```python
APIVersionManager(default_version: str = "1.0.0", version_format: VersionFormat = VersionFormat.SEMVER)
```

#### Methods

##### `register_version(version: APIVersion) -> None`
Register a new API version.

##### `get_version(version_str: str) -> Optional[APIVersion]`
Get a version by string.

##### `validate_version(version_str: str) -> bool`
Validate that a version is supported.

##### `parse_version_from_request(headers: Dict[str, str], query_params: Dict[str, List[str]]) -> str`
Parse version from request.

##### `register_endpoint(endpoint: VersionedEndpoint) -> None`
Register a versioned endpoint.

##### `add_migration_rule(from_version: str, to_version: str, migrator: Callable) -> None`
Add a migration rule between versions.

##### `migrate_data(data: Any, from_version: str, to_version: str) -> Any`
Migrate data between versions.

##### `get_version_info() -> Dict[str, Any]`
Get comprehensive version information.

### APIVersion Class

Represents an API version.

#### Constructor
```python
APIVersion(
    version: str,
    format: VersionFormat,
    release_date: datetime,
    description: str = "",
    deprecated: bool = False,
    deprecated_date: Optional[datetime] = None,
    breaking_changes: List[str] = None,
    features: List[str] = None
)
```

#### Methods

##### `is_compatible_with(other_version: APIVersion) -> bool`
Check version compatibility.

##### `__lt__(other: APIVersion) -> bool`
Compare versions for ordering.

### VersionedEndpoint Class

Represents an endpoint with multiple versions.

#### Constructor
```python
VersionedEndpoint(path: str, versions: Dict[str, Callable], default_version: str)
```

#### Methods

##### `get_handler(version: Optional[str] = None) -> Callable`
Get handler for a specific version.

##### `add_version(version: str, handler: Callable) -> None`
Add a version handler.

##### `deprecate_version(version: str) -> None`
Mark a version as deprecated.

## OpenAPI Generator Interface

### OpenAPIGenerator Class

Generates OpenAPI specifications from API definitions.

#### Constructor
```python
OpenAPIGenerator(
    title: str,
    version: str,
    description: str = "",
    base_url: str = "/api"
)
```

#### Methods

##### `add_rest_api(api: RESTAPI) -> None`
Add a REST API to the specification.

##### `add_graphql_api(api: GraphQLAPI) -> None`
Add a GraphQL API to the specification.

##### `add_version_manager(version_manager: APIVersionManager) -> None`
Add version information to the specification.

##### `add_security_schemes(schemes: Dict[str, Dict[str, Any]]) -> None`
Add security scheme definitions.

##### `add_global_responses(responses: Dict[str, Dict[str, Any]]) -> None`
Add global response definitions.

##### `add_tags(tags: List[Dict[str, str]]) -> None`
Add tag definitions.

##### `set_external_docs(url: str, description: str = "...") -> None`
Set external documentation.

##### `validate_spec() -> List[str]`
Validate the OpenAPI specification.

**Returns:** List of validation errors

##### `generate_spec() -> OpenAPISpecification`
Generate the final OpenAPI specification.

### OpenAPISpecification Class

Container for OpenAPI specification data.

#### Methods

##### `to_dict() -> Dict[str, Any]`
Get specification as dictionary.

##### `to_json(indent: int = 2) -> str`
Get specification as JSON string.

##### `to_yaml() -> str`
Get specification as YAML string.

##### `save_to_file(filepath: str, format: str = "json") -> None`
Save specification to file.

## Enums and Constants

### HTTPMethod Enum
- `GET`
- `POST`
- `PUT`
- `DELETE`
- `PATCH`
- `OPTIONS`
- `HEAD`

### HTTPStatus Enum
Standard HTTP status codes (200, 201, 400, 401, 403, 404, 409, 500, 501, 502, 503)

### VersionFormat Enum
- `SEMVER` - Semantic versioning (1.0.0)
- `DATE` - Date-based versioning (2024-01-01)
- `INT` - Integer versioning (1, 2, 3)

### GraphQLType Enum
- `STRING`
- `INT`
- `FLOAT`
- `BOOLEAN`
- `ID`

## Error Handling

All methods that can fail raise appropriate exceptions:

- `ValueError`: Invalid parameters or configurations
- `KeyError`: Missing required keys or endpoints
- `TypeError`: Incorrect parameter types
- `RuntimeError`: Execution failures

GraphQL-specific errors are returned in the response `errors` array.

## Performance Characteristics

- **REST API**: O(1) routing with O(n) middleware per request
- **GraphQL**: O(query_complexity) execution with configurable limits
- **Versioning**: O(1) version lookups with O(migration_depth) data migration
- **OpenAPI Generation**: O(number_of_endpoints) generation time

## Thread Safety

- `RESTAPI` and `GraphQLAPI`: Thread-safe for concurrent requests
- `APIVersionManager`: Thread-safe for version operations
- `OpenAPIGenerator`: Not thread-safe, generate specifications in single thread

## Extensibility Points

- **Middleware**: Custom middleware functions for request processing
- **Resolvers**: Custom GraphQL field resolvers
- **Migration Rules**: Custom data migration functions
- **Type Converters**: Custom OpenAPI type conversion functions
- **Validators**: Custom validation functions for requests and responses
