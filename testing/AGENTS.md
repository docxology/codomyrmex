# Codomyrmex Agents — testing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the testing coordination document for all test suites and validation systems in the Codomyrmex repository. It defines the comprehensive testing framework that ensures code quality, functionality, and reliability across the entire platform.

The testing directory contains unit tests, integration tests, and validation frameworks that follow test-driven development (TDD) practices with real data analysis (no mock methods).

## Test Organization

### Test Types

The testing framework is organized by test scope and methodology:

| Test Type | Purpose | Coverage | Location |
|-----------|---------|----------|----------|
| **Unit Tests** | Individual component testing | Functions, classes, modules | `unit/` |
| **Integration Tests** | Component interaction testing | Module coordination, workflows | `integration/` |
| **System Tests** | End-to-end validation | Complete workflows, user scenarios | Root-level scripts |

### Test Categories

Tests are further categorized by functionality:
- **Core Module Tests**: Individual module validation
- **Orchestration Tests**: Multi-module workflow testing
- **Performance Tests**: Benchmarking and profiling
- **Security Tests**: Vulnerability and compliance validation
- **Documentation Tests**: Documentation accuracy validation

## Active Components

### Core Test Infrastructure
- `README.md` – Testing directory documentation
- `__init__.py` – Test package initialization
- `conftest.py` – Shared test configuration and fixtures
- `run_all_git_examples.py` – Git operations test runner

### Test Suites
- `unit/` – Unit test suites for individual components
- `integration/` – Integration tests for component interactions

## Operating Contracts

### Universal Testing Protocols

All tests in this directory must:

1. **Real Data Analysis**: Use actual data and implementations (no mock methods)
2. **TDD Compliance**: Follow test-driven development practices
3. **Comprehensive Coverage**: Maintain ≥80% test coverage
4. **Performance Benchmarks**: Include performance testing where applicable
5. **Documentation Validation**: Test documentation accuracy alongside code

### Test-Specific Guidelines

#### Unit Tests
- Test individual functions, classes, and modules in isolation
- Focus on edge cases and error conditions
- Include property-based testing where applicable
- Mock external dependencies when necessary for isolation

#### Integration Tests
- Test real component interactions and workflows
- Validate data flow between modules
- Test error propagation and recovery
- Include performance validation under load

#### Test Development
- Write tests before implementing features (TDD)
- Include both positive and negative test cases
- Document test intent and expected behavior
- Use descriptive test names and assertions

## Test Execution

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/codomyrmex --cov-report=html

# Run specific test suites
pytest testing/unit/
pytest testing/integration/

# Run tests for specific modules
pytest -k "module_name"
```

### Test Configuration

The testing framework uses:
- **pytest** as the primary test runner
- **coverage.py** for code coverage analysis
- **pytest.ini** for test configuration
- **conftest.py** for shared fixtures and setup

## Navigation

### For Users
- **Quick Start**: [README.md](../../testing/README.md) - Testing overview
- **Running Tests**: See development documentation for test execution
- **Coverage Reports**: Generated in `htmlcov/` directory

### For Agents
- **Testing Strategy**: [docs/development/testing-strategy.md](../../../docs/development/testing-strategy.md)
- **Test Standards**: [cursorrules/general.cursorrules](../../../cursorrules/general.cursorrules)
- **Module System**: [docs/modules/overview.md](../../../docs/modules/overview.md)

### For Contributors
- **Test Development**: [docs/development/testing-strategy.md](../../../docs/development/testing-strategy.md)
- **Code Coverage**: [pytest.ini](../../../pytest.ini) - Coverage configuration
- **Contributing**: [docs/project/contributing.md](../../../docs/project/contributing.md)

## Agent Coordination

### Test Integration

When developing tests that span multiple modules:

1. **Dependency Analysis**: Review module relationships in `docs/modules/relationships.md`
2. **Integration Points**: Coordinate with module AGENTS.md files
3. **Shared Fixtures**: Use `conftest.py` for common test setup
4. **Coverage Tracking**: Ensure comprehensive coverage across integrated components

### Quality Gates

Before merging test changes:

1. **All Tests Pass**: Complete test suite passes on all supported platforms
2. **Coverage Maintained**: Test coverage remains ≥80%
3. **Performance Validated**: Performance benchmarks meet requirements
4. **Documentation Updated**: Test documentation reflects changes
5. **Integration Verified**: Integration tests validate cross-module functionality

## Test Metrics

### Coverage Targets
- **Unit Tests**: ≥85% coverage for individual modules
- **Integration Tests**: ≥75% coverage for module interactions
- **System Tests**: 100% coverage for critical user workflows

### Performance Benchmarks
- Unit tests: <100ms per test suite
- Integration tests: <30 seconds per test suite
- Full test suite: <5 minutes execution time

## Version History

- **v0.1.0** (December 2025) - Initial comprehensive testing framework with TDD practices

## Related Documentation

- **[Testing Strategy](docs/development/testing-strategy.md)** - Comprehensive testing approach
- **[Module System](docs/modules/overview.md)** - Module architecture and relationships
- **[Contributing Guide](docs/project/contributing.md)** - Testing requirements and workflow
