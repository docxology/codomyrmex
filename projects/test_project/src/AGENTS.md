# Codomyrmex Agents — projects/test_project/src

## Signposting
- **Parent**: [Repository Root](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Source code implementation for the test project demonstrating modular application architecture, API development, business logic implementation, and comprehensive error handling. This source directory serves as a complete example of Codomyrmex application development best practices.

The src directory showcases professional software development patterns, clean architecture principles, and integration with the Codomyrmex platform.

## Application Architecture

### Core Design Principles
- **Modular Design**: Clean separation of concerns and responsibilities
- **API-First**: Well-defined interfaces and contracts
- **Error Resilience**: Comprehensive error handling and recovery
- **Testable Code**: Code designed for comprehensive testing
- **Maintainable Structure**: Clear organization and documentation

### Architecture Layers
```
Application Architecture
├── Interface Layer
│   ├── API endpoints and interfaces
│   ├── Request/response handling
│   └── Input validation and sanitization
├── Business Logic Layer
│   ├── Core business rules and algorithms
│   ├── Data processing and transformation
│   └── Business validation and constraints
├── Data Access Layer
│   ├── Data retrieval and persistence
│   ├── Data transformation and mapping
│   └── Data integrity and consistency
└── Infrastructure Layer
    ├── External service integrations
    ├── Logging and monitoring
    └── Configuration management
```

## Code Organization

### Directory Structure
- **Core Modules**: Main application logic and business rules
- **API Modules**: REST API endpoints and interface definitions
- **Utilities**: Shared utilities and helper functions
- **Models**: Data models and type definitions
- **Services**: Business service implementations
- **Tests**: Unit and integration test suites

### Naming Conventions
- **Modules**: Descriptive, lowercase names with underscores
- **Classes**: PascalCase with clear, descriptive names
- **Functions**: snake_case with action-oriented names
- **Constants**: UPPERCASE with underscores
- **Variables**: snake_case with descriptive names

## Development Standards

### Code Quality Standards
- **PEP 8 Compliance**: Python coding standards adherence
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Docstring documentation for all public interfaces
- **Error Handling**: Proper exception handling and logging
- **Performance**: Efficient algorithms and resource usage

### Testing Standards
- **Unit Tests**: Comprehensive unit test coverage
- **Integration Tests**: End-to-end functionality testing
- **Test Documentation**: Clear test case documentation
- **Mock Usage**: Appropriate use of mocks and test doubles
- **Test Organization**: Logical test file and case organization

### Security Standards
- **Input Validation**: All input data validation and sanitization
- **Authentication**: Proper authentication and authorization
- **Data Protection**: Secure handling of sensitive data
- **Audit Logging**: Security event logging and monitoring
- **Vulnerability Prevention**: Protection against common vulnerabilities

## Implementation Patterns

### API Development Patterns
- **RESTful Design**: RESTful API design principles
- **Request Validation**: Input validation and error responses
- **Response Formatting**: Consistent API response structures
- **Error Handling**: Proper HTTP error codes and messages
- **Documentation**: OpenAPI/Swagger API documentation

### Business Logic Patterns
- **Service Layer**: Business logic encapsulation in services
- **Domain Models**: Rich domain object implementations
- **Validation**: Business rule validation and enforcement
- **Transaction Management**: Data consistency and transaction handling
- **Event Handling**: Business event processing and reactions

### Data Access Patterns
- **Repository Pattern**: Data access abstraction and encapsulation
- **Query Optimization**: Efficient data retrieval and manipulation
- **Connection Management**: Database connection handling and pooling
- **Migration Support**: Database schema migration and versioning
- **Data Integrity**: Data consistency and referential integrity

## Active Components

### Core Source Files
- `README.md` – Source code documentation and development guide

### Application Modules
- **Main Application**: Core application entry point and orchestration
- **API Endpoints**: REST API endpoint implementations
- **Business Services**: Business logic and service implementations
- **Data Models**: Data structure and model definitions
- **Utilities**: Shared utility functions and helpers

### Development Assets
- Unit and integration test suites
- Development configuration and setup scripts
- Code documentation and API specifications
- Performance benchmarking and profiling tools
- Development environment setup utilities


### Additional Files
- `SPEC.md` – Spec Md

## Code Implementation

### Development Workflow
1. **Requirement Analysis**: Understand and document requirements
2. **Design**: Create architecture and interface designs
3. **Implementation**: Write clean, tested, and documented code
4. **Testing**: Comprehensive unit and integration testing
5. **Review**: Code review and quality assurance
6. **Deployment**: Production deployment and monitoring

### Quality Assurance
1. **Static Analysis**: Code linting and static analysis
2. **Unit Testing**: Individual component testing
3. **Integration Testing**: Component interaction testing
4. **Performance Testing**: Load and performance validation
5. **Security Testing**: Security vulnerability assessment

### Maintenance Procedures
1. **Bug Fixes**: Issue identification and resolution
2. **Feature Development**: New feature implementation
3. **Refactoring**: Code improvement and optimization
4. **Documentation Updates**: Documentation maintenance and updates
5. **Dependency Updates**: Third-party library updates and testing

## Performance and Monitoring

### Performance Optimization
- **Algorithm Efficiency**: Optimal algorithm selection and implementation
- **Memory Management**: Efficient memory usage and garbage collection
- **Database Optimization**: Query optimization and indexing
- **Caching Strategies**: Appropriate caching implementation
- **Resource Management**: CPU and I/O resource optimization

### Monitoring and Observability
- **Application Metrics**: Key performance and business metrics
- **Logging**: Structured logging and log analysis
- **Tracing**: Request tracing and performance profiling
- **Health Checks**: Application health and dependency monitoring
- **Alerting**: Automated alerting for issues and anomalies

## Operating Contracts

### Universal Code Protocols

All source code must:

1. **Quality Standards**: Meet established code quality and style standards
2. **Testing Coverage**: Comprehensive test coverage for all functionality
3. **Documentation**: Complete documentation for all public interfaces
4. **Security Compliance**: Meet security requirements and best practices
5. **Performance Requirements**: Meet established performance targets

### Code-Specific Guidelines

#### API Implementation
- Implement consistent error handling and response formats
- Include comprehensive input validation and sanitization
- Provide clear API documentation and examples
- Implement appropriate authentication and authorization
- Include rate limiting and abuse protection

#### Business Logic Implementation
- Encapsulate business rules in appropriate service classes
- Implement proper transaction boundaries and consistency
- Include comprehensive business validation and error handling
- Provide clear separation between business and infrastructure concerns
- Implement appropriate logging and audit trails

#### Data Access Implementation
- Use appropriate data access patterns and abstractions
- Implement efficient queries and data retrieval
- Include proper error handling for data access failures
- Provide data validation and integrity checking
- Implement appropriate caching and performance optimizations

## Code Maintenance

### Update Procedures
Code must be updated when:
- New requirements or features are identified
- Security vulnerabilities are discovered
- Performance issues require optimization
- Dependencies require updates
- Platform changes affect compatibility

### Quality Assurance
- **Code Review**: Peer review of all code changes
- **Automated Testing**: Continuous integration and testing
- **Performance Testing**: Performance regression testing
- **Security Testing**: Security vulnerability scanning
- **Integration Testing**: End-to-end functionality testing

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Source Hierarchy
- **Source Overview**: [README.md](README.md) - Source code documentation and development guide

### Related Documentation
- **Project Overview**: [../README.md](../README.md) - Test project documentation
- **Configuration**: [../config/README.md](../config/README.md) - Configuration management
- **Data Processing**: [../data/README.md](../data/README.md) - Data processing guide
- **Reports**: [../reports/README.md](../reports/README.md) - Output and reporting

### Platform Navigation
- **Projects Directory**: [../../README.md](../../README.md) - Project template overview

## Agent Coordination

### Code Synchronization

When application requirements change:

1. **Architecture Updates**: Modify application architecture and design
2. **Implementation Updates**: Update code to meet new requirements
3. **Testing Updates**: Update test suites for new functionality
4. **Documentation Updates**: Update code documentation and API specs
5. **Integration Updates**: Update integration points and interfaces

### Quality Gates

Before code changes:

1. **Requirement Verification**: Requirements clearly understood and documented
2. **Design Review**: Architecture and design reviewed and approved
3. **Code Review**: Implementation reviewed by experienced developers
4. **Testing Validation**: All tests pass and coverage maintained
5. **Integration Testing**: Code works with other application components

## Code Metrics

### Quality Metrics
- **Test Coverage**: Percentage of code covered by automated tests
- **Code Complexity**: Cyclomatic complexity and maintainability metrics
- **Technical Debt**: Code quality and technical debt measurements
- **Performance Benchmarks**: Code execution performance metrics
- **Security Score**: Security vulnerability and compliance metrics

### Development Metrics
- **Development Velocity**: Code development and delivery speed
- **Bug Density**: Number of bugs per lines of code
- **Code Churn**: Code modification and refactoring frequency
- **Review Cycle Time**: Time from code completion to production deployment
- **Maintenance Effort**: Time spent on code maintenance and support

## Version History

- **v0.1.0** (December 2025) - Initial test project source code demonstrating modular application architecture, API development, business logic, and comprehensive error handling