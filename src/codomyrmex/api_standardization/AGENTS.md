# Codomyrmex Agents — src/codomyrmex/api_standardization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

API standardization module providing unified interfaces for building REST APIs, GraphQL APIs, managing API versions, and generating OpenAPI specifications. It ensures consistent API development across Codomyrmex projects.

## Module Overview

### Key Capabilities
- **REST API Framework**: Standardized REST API development with routing and middleware
- **GraphQL API Framework**: Type-safe GraphQL schema development and execution
- **API Versioning**: Semantic versioning with migration support and compatibility management
- **OpenAPI Generation**: Automated OpenAPI/Swagger specification generation
- **Documentation**: Integrated API documentation generation and hosting

### Key Features
- Unified API development patterns across Codomyrmex modules
- Automatic OpenAPI specification generation
- Version compatibility management and migration paths
- Type-safe GraphQL schema development
- Built-in error handling and response formatting
- Authentication and authorization framework integration

## Function Signatures

### REST API Functions

```python
def create_api(title: str = "Codomyrmex API", version: str = "1.0.0") -> RESTAPI
```

Create a new REST API instance with default configuration.

**Parameters:**
- `title` (str): API title for documentation. Defaults to "Codomyrmex API"
- `version` (str): API version string. Defaults to "1.0.0"

**Returns:** `RESTAPI` - Configured REST API instance

```python
def create_router(prefix: str = "") -> APIRouter
```

Create a new API router with optional path prefix.

**Parameters:**
- `prefix` (str): URL prefix for all routes in this router. Defaults to ""

**Returns:** `APIRouter` - New API router instance

### GraphQL API Functions

```python
def resolver(field_name: str, complexity: int = 1)
```

Decorator to register a GraphQL field resolver with complexity scoring.

**Parameters:**
- `field_name` (str): GraphQL field name this resolver handles
- `complexity` (int): Query complexity cost. Defaults to 1

**Returns:** Decorator function

```python
def mutation(name: str, input_type: GraphQLObjectType, output_type: GraphQLObjectType, complexity: int = 10)
```

Decorator to register a GraphQL mutation with input/output types.

**Parameters:**
- `name` (str): Mutation name
- `input_type` (GraphQLObjectType): GraphQL input type for mutation arguments
- `output_type` (GraphQLObjectType): GraphQL output type for mutation result
- `complexity` (int): Mutation complexity cost. Defaults to 10

**Returns:** Decorator function

```python
def create_schema() -> GraphQLSchema
```

Create a new GraphQL schema instance.

**Returns:** `GraphQLSchema` - Empty GraphQL schema ready for type registration

```python
def create_object_type(name: str, description: Optional[str] = None) -> GraphQLObjectType
```

Create a new GraphQL object type.

**Parameters:**
- `name` (str): Object type name
- `description` (Optional[str]): Type description for documentation

**Returns:** `GraphQLObjectType` - New GraphQL object type

```python
def create_field(name: str, type: Union[str, GraphQLObjectType], description: Optional[str] = None, required: bool = False) -> GraphQLField
```

Create a GraphQL field definition.

**Parameters:**
- `name` (str): Field name
- `type` (Union[str, GraphQLObjectType]): Field type (string or GraphQL type)
- `description` (Optional[str]): Field description
- `required` (bool): Whether field is non-nullable. Defaults to False

**Returns:** `GraphQLField` - GraphQL field definition

### API Versioning Functions

```python
def version(version_str: str)
```

Decorator to mark an API endpoint with a specific version.

**Parameters:**
- `version_str` (str): Version string (e.g., "1.0.0", "v2")

**Returns:** Decorator function

```python
def deprecated_version(version_str: str)
```

Decorator to mark an API endpoint version as deprecated.

**Parameters:**
- `version_str` (str): Deprecated version string

**Returns:** Decorator function

```python
def create_version_manager(default_version: str = "1.0.0") -> APIVersionManager
```

Create a new API version manager with default version.

**Parameters:**
- `default_version` (str): Default API version. Defaults to "1.0.0"

**Returns:** `APIVersionManager` - Configured version manager

```python
def create_versioned_endpoint(path: str, default_version: str) -> VersionedEndpoint
```

Create a versioned API endpoint with fallback support.

**Parameters:**
- `path` (str): Base endpoint path
- `default_version` (str): Default version to use

**Returns:** `VersionedEndpoint` - Version-aware endpoint handler

### OpenAPI Generation Functions

```python
def generate_openapi_spec(title: str = "Codomyrmex API", version: str = "1.0.0", description: Optional[str] = None, servers: Optional[List[Dict[str, str]]] = None) -> OpenAPISpecification
```

Generate a new OpenAPI specification.

**Parameters:**
- `title` (str): API title. Defaults to "Codomyrmex API"
- `version` (str): API version. Defaults to "1.0.0"
- `description` (Optional[str]): API description
- `servers` (Optional[List[Dict[str, str]]]): List of server configurations

**Returns:** `OpenAPISpecification` - New OpenAPI specification instance

```python
def create_openapi_from_rest_api(api: RESTAPI) -> OpenAPISpecification
```

Generate OpenAPI specification from REST API instance.

**Parameters:**
- `api` (RESTAPI): REST API instance to analyze

**Returns:** `OpenAPISpecification` - OpenAPI spec derived from REST API

```python
def create_openapi_from_graphql_api(api: GraphQLAPI) -> OpenAPISpecification
```

Generate OpenAPI specification from GraphQL API instance.

**Parameters:**
- `api` (GraphQLAPI): GraphQL API instance to analyze

**Returns:** `OpenAPISpecification` - OpenAPI spec derived from GraphQL API

## Data Structures

### REST API Classes

#### HTTPMethod Enum
```python
class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
```

HTTP method enumeration for REST API endpoints.

#### HTTPStatus Enum
```python
class HTTPStatus(Enum):
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500
```

Standard HTTP status codes for API responses.

#### APIRequest Class
```python
@dataclass
class APIRequest:
    method: HTTPMethod
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Optional[Any]
    context: Dict[str, Any]
```

Standardized API request representation.

#### APIResponse Class
```python
@dataclass
class APIResponse:
    status_code: HTTPStatus
    data: Any
    headers: Dict[str, str]
    metadata: Dict[str, Any]
```

Standardized API response with status and data.

#### APIEndpoint Class
```python
@dataclass
class APIEndpoint:
    path: str
    method: HTTPMethod
    handler: Callable
    summary: str
    description: Optional[str]
    tags: List[str]
    deprecated: bool
```

API endpoint definition with metadata.

#### APIRouter Class
```python
class APIRouter:
    def __init__(self, prefix: str = ""): ...

    def add_endpoint(self, endpoint: APIEndpoint) -> None: ...

    def get_endpoints(self) -> List[APIEndpoint]: ...

    def route(self, path: str, method: HTTPMethod) -> Callable: ...
```

Router for organizing and managing API endpoints.

#### RESTAPI Class
```python
class RESTAPI:
    def __init__(self, title: str, version: str, description: str): ...

    def add_router(self, router: APIRouter) -> None: ...

    def get_endpoints(self) -> List[APIEndpoint]: ...

    def handle_request(self, request: APIRequest) -> APIResponse: ...

    def generate_openapi_spec(self) -> OpenAPISpecification: ...
```

Main REST API class managing routers and endpoints.

### GraphQL API Classes

#### GraphQLType Enum
```python
class GraphQLType(Enum):
    STRING = "String"
    INT = "Int"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    ID = "ID"
```

Basic GraphQL scalar types.

#### GraphQLField Class
```python
@dataclass
class GraphQLField:
    name: str
    type: Union[str, GraphQLObjectType]
    description: Optional[str]
    required: bool
    default_value: Any
```

GraphQL field definition.

#### GraphQLObjectType Class
```python
class GraphQLObjectType:
    def __init__(self, name: str, description: Optional[str] = None): ...

    def add_field(self, field: GraphQLField) -> None: ...

    def get_fields(self) -> Dict[str, GraphQLField]: ...

    def validate(self) -> List[str]: ...
```

GraphQL object type definition.

#### GraphQLSchema Class
```python
class GraphQLSchema:
    def __init__(self): ...

    def add_type(self, type: GraphQLObjectType) -> None: ...

    def add_query(self, query: GraphQLQuery) -> None: ...

    def add_mutation(self, mutation: GraphQLMutation) -> None: ...

    def validate(self) -> List[str]: ...

    def execute_query(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]: ...
```

GraphQL schema containing types, queries, and mutations.

#### GraphQLResolver Class
```python
class GraphQLResolver:
    def __init__(self, field_name: str, complexity: int = 1): ...

    def resolve(self, parent: Any, args: Dict[str, Any], context: Any) -> Any: ...

    def get_complexity(self) -> int: ...
```

Base class for GraphQL field resolvers.

#### GraphQLMutation Class
```python
class GraphQLMutation:
    def __init__(self, name: str, input_type: GraphQLObjectType, output_type: GraphQLObjectType): ...

    def execute(self, input: Dict[str, Any], context: Any) -> Any: ...

    def validate_input(self, input: Dict[str, Any]) -> List[str]: ...
```

GraphQL mutation definition.

#### GraphQLQuery Class
```python
class GraphQLQuery:
    def __init__(self, name: str, return_type: GraphQLObjectType): ...

    def execute(self, args: Dict[str, Any], context: Any) -> Any: ...

    def validate_args(self, args: Dict[str, Any]) -> List[str]: ...
```

GraphQL query definition.

#### GraphQLAPI Class
```python
class GraphQLAPI:
    def __init__(self, schema: GraphQLSchema): ...

    def execute(self, query: str, variables: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]: ...

    def add_resolver(self, resolver: GraphQLResolver) -> None: ...

    def validate_schema(self) -> List[str]: ...
```

Main GraphQL API class for query execution.

### API Versioning Classes

#### SimpleVersion Class
```python
@dataclass
class SimpleVersion:
    major: int
    minor: int
    patch: int
```

Simple semantic version representation.

#### VersionFormat Enum
```python
class VersionFormat(Enum):
    SEMVER = "semver"
    DATE = "date"
    CUSTOM = "custom"
```

Supported version format types.

#### APIVersion Class
```python
@dataclass
class APIVersion:
    version_string: str
    format: VersionFormat
    release_date: datetime
    deprecated: bool = False
    deprecation_date: Optional[datetime] = None
    migration_guide: Optional[str] = None
```

Complete API version information with lifecycle management.

#### VersionedEndpoint Class
```python
class VersionedEndpoint:
    def __init__(self, base_path: str, default_version: str): ...

    def add_version(self, version: str, handler: Callable) -> None: ...

    def get_handler(self, requested_version: Optional[str] = None) -> Callable: ...

    def get_supported_versions(self) -> List[str]: ...
```

Version-aware API endpoint with multiple version handlers.

#### APIVersionManager Class
```python
class APIVersionManager:
    def __init__(self, default_version: str): ...

    def register_version(self, version: APIVersion) -> None: ...

    def get_version(self, version_string: str) -> Optional[APIVersion]: ...

    def get_current_versions(self) -> List[APIVersion]: ...

    def deprecate_version(self, version_string: str, migration_guide: str) -> None: ...

    def add_migration_rule(self, from_version: str, to_version: str, migration_func: Callable) -> None: ...
```

Central manager for API version lifecycle and migrations.

### OpenAPI Generation Classes

#### OpenAPISpecification Class
```python
class OpenAPISpecification:
    def __init__(self, title: str, version: str): ...

    def add_path(self, path: str, methods: Dict[str, Dict[str, Any]]) -> None: ...

    def add_schema(self, name: str, schema: Dict[str, Any]) -> None: ...

    def add_security_scheme(self, name: str, scheme: Dict[str, Any]) -> None: ...

    def validate(self) -> List[str]: ...

    def to_dict(self) -> Dict[str, Any]: ...

    def save_to_file(self, filepath: str, format: str = 'json') -> None: ...
```

OpenAPI specification builder and validator.

#### OpenAPIGenerator Class
```python
class OpenAPIGenerator:
    def __init__(self, title: str, version: str): ...

    def add_rest_api(self, api: RESTAPI) -> None: ...

    def add_graphql_api(self, api: GraphQLAPI) -> None: ...

    def add_version_manager(self, version_manager: APIVersionManager) -> None: ...

    def generate_spec(self) -> OpenAPISpecification: ...

    def validate_spec(self, spec: OpenAPISpecification) -> List[str]: ...
```

Generator for creating OpenAPI specifications from API instances.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `api_versioning.py` – API versioning and compatibility management
- `graphql_api.py` – GraphQL API implementation
- `openapi_generator.py` – OpenAPI specification generation
- `rest_api.py` – REST API implementation

## Operating Contracts

### Universal API Protocols

All API development within the Codomyrmex platform must:

1. **Standard Interfaces** - Use provided REST and GraphQL frameworks for consistency
2. **Version Management** - Implement proper API versioning with migration paths
3. **Documentation** - Generate and maintain accurate OpenAPI specifications
4. **Security** - Follow security best practices for API development
5. **Testing** - Comprehensive testing of all API endpoints and versions

### Module-Specific Guidelines

#### API Development
- Use standardized REST and GraphQL frameworks
- Implement proper error handling and status codes
- Follow API versioning best practices
- Generate accurate OpenAPI documentation

#### Version Management
- Define clear version compatibility rules
- Provide migration paths for breaking changes
- Communicate version changes to consumers
- Deprecate versions with appropriate timelines

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API reference

### Related Modules

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Responsibilities

### API Development Agent
**Role**: Implement and maintain API endpoints using standardized frameworks.

**Responsibilities**:
- Create REST API endpoints using `RESTAPI` and `APIRouter` classes
- Implement GraphQL schemas with proper type definitions
- Ensure API endpoints follow REST/GraphQL best practices
- Add appropriate error handling and status codes
- Write comprehensive API documentation

**Key Interfaces**:
```python
# REST API creation
api = RESTAPI("My API", "1.0.0", "API description")
@api.router.get("/endpoint")
def handler(request): return APIResponse.success(data)

# GraphQL schema creation
schema = GraphQLSchema()
user_type = GraphQLObjectType("User")
schema.add_type(user_type)
```

### Version Management Agent
**Role**: Handle API versioning and backward compatibility.

**Responsibilities**:
- Define API versions using `APIVersion` and `APIVersionManager`
- Implement data migration functions between versions
- Mark deprecated versions and plan removal timelines
- Update version compatibility rules
- Communicate breaking changes to API consumers

**Key Interfaces**:
```python
version_manager = APIVersionManager("1.0.0")
version_manager.register_version(APIVersion("2.0.0", VersionFormat.SEMVER, datetime.now()))
version_manager.add_migration_rule("1.0.0", "2.0.0", migration_function)
```

### Documentation Agent
**Role**: Generate and maintain API documentation.

**Responsibilities**:
- Use `OpenAPIGenerator` to create OpenAPI specifications
- Ensure all endpoints are properly documented
- Generate API client libraries from specifications
- Host API documentation and keep it current
- Validate documentation accuracy against implementation

**Key Interfaces**:
```python
generator = OpenAPIGenerator("API Title", "1.0.0")
generator.add_rest_api(rest_api)
generator.add_graphql_api(graphql_api)
spec = generator.generate_spec()
spec.save_to_file("openapi.json")
```

### Testing Agent
**Role**: Ensure API quality through comprehensive testing.

**Responsibilities**:
- Write unit tests for all API endpoints
- Create integration tests for API workflows
- Test API versioning and migration
- Validate OpenAPI specification generation
- Performance test API endpoints
- Test error conditions and edge cases

**Key Testing Areas**:
- Request/response handling
- Schema validation
- Version compatibility
- Documentation accuracy
- Error handling

## Coordination Protocols

### API Design Reviews
1. **Endpoint Design**: All new endpoints must be reviewed for REST/GraphQL compliance
2. **Version Planning**: Major version changes require cross-team coordination
3. **Documentation**: OpenAPI specs must be validated before deployment

### Version Release Process
1. **Version Definition**: Create `APIVersion` with release notes
2. **Migration Planning**: Define migration paths for breaking changes
3. **Testing**: Full test suite must pass for new versions
4. **Documentation**: Update API documentation with version changes
5. **Communication**: Notify API consumers of changes

### Breaking Change Protocol
1. **Assessment**: Evaluate impact of breaking changes
2. **Migration Path**: Provide clear migration instructions
3. **Deprecation Period**: Allow minimum 6 months for version migration
4. **Communication**: Send advance notice to all API consumers

## Quality Gates

### Pre-Commit Checks
- All endpoints must have proper error handling
- OpenAPI specification must validate without errors
- API tests must pass with >90% coverage
- No deprecated versions without migration paths

### Pre-Release Checks
- API documentation is current and accurate
- Version compatibility is maintained
- Performance benchmarks are met
- Security audit passes

### Post-Release Monitoring
- Monitor API error rates and performance
- Track version adoption and migration progress
- Collect user feedback on API changes
- Plan future improvements based on usage patterns

## Communication Channels

### Internal Coordination
- **API Design Discussions**: Use `#api-design` channel for endpoint design reviews
- **Version Planning**: Coordinate major versions through architecture review meetings
- **Breaking Changes**: All breaking changes require approval from architecture team

### External Communication
- **API Changelog**: Maintain public changelog for API consumers
- **Deprecation Notices**: Send advance notice for deprecated features
- **Migration Guides**: Provide detailed migration documentation
- **Support Channels**: Monitor API consumer support requests

## Tool Integration

### Development Tools
- **API Testing**: Use provided test framework for endpoint validation
- **Documentation**: Auto-generate docs from OpenAPI specifications
- **Version Control**: Tag releases with semantic versions
- **CI/CD**: Automated testing and deployment pipelines

### Monitoring Tools
- **API Metrics**: Track request rates, error rates, and performance
- **Version Usage**: Monitor which API versions are being used
- **Documentation Analytics**: Track documentation usage and feedback

## Dependencies

### Required Modules
- **Logging Monitoring**: For request logging and error tracking
- **Security Audit**: For API security validation
- **Performance**: For API performance monitoring

### Optional Integrations
- **Containerization**: For API containerization and deployment
- **Database Management**: For API data persistence
- **Authentication**: For API access control

## Error Handling

### API Errors
- **4xx Errors**: Client errors with clear error messages
- **5xx Errors**: Server errors logged with full context
- **GraphQL Errors**: Structured error responses
- **Version Errors**: Clear messages for unsupported versions

### Recovery Procedures
- **Circuit Breakers**: Implement for external service calls
- **Graceful Degradation**: Continue operating with reduced functionality
- **Rollback Plans**: Quick rollback procedures for failed deployments

## Performance Targets

### Response Times
- **REST API**: <100ms for simple requests, <500ms for complex operations
- **GraphQL**: <200ms for typical queries, configurable complexity limits
- **OpenAPI Generation**: <5 seconds for typical API specifications

### Throughput
- **Requests/second**: Support 1000+ concurrent requests
- **Error Rate**: Maintain <1% error rate under normal load
- **Availability**: 99.9% uptime target

## Security Requirements

### Authentication & Authorization
- **API Keys**: Secure key management and rotation
- **OAuth/JWT**: Support for industry-standard authentication
- **Role-Based Access**: Granular permission control

### Data Protection
- **Input Validation**: Comprehensive validation of all inputs
- **Output Sanitization**: Prevent data leakage in responses
- **Rate Limiting**: Prevent abuse and DoS attacks
- **Audit Logging**: Complete audit trail of API access

## Future Evolution

### Planned Enhancements
- **Real-time APIs**: WebSocket support for real-time features
- **API Federation**: Combine multiple APIs into unified interfaces
- **Advanced Caching**: Intelligent response caching strategies
- **AI Integration**: AI-powered API optimization and monitoring

### Community Engagement
- **Feedback Collection**: Gather API consumer feedback regularly
- **Feature Requests**: Prioritize based on user needs
- **Standards Compliance**: Stay current with API industry standards
