# Codomyrmex Agents — src/codomyrmex/tests

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [examples](../../../scripts/examples/AGENTS.md)
    - [fixtures](fixtures/AGENTS.md)
    - [integration](integration/AGENTS.md)
    - [output](output/AGENTS.md)
    - [performance](performance/AGENTS.md)
    - [unit](unit/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the testing coordination document for all test suites and validation systems in the Codomyrmex repository. It defines the testing framework that ensures code quality, functionality, and reliability across the entire platform.

The testing directory contains unit tests, integration tests, and validation frameworks that follow test-driven development (TDD) practices with real data analysis (no mock methods).

## Function Signatures

### Test Infrastructure Functions

```python
def project_root() -> Path
```

Get the project root directory path.

**Returns:** `Path` - Absolute path to project root directory

```python
def examples_dir(project_root: Path) -> Path
```

Get the examples directory path.

**Parameters:**
- `project_root` (Path): Project root directory path

**Returns:** `Path` - Path to examples directory

```python
def testing_dir(project_root: Path) -> Path
```

Get the testing directory path.

**Parameters:**
- `project_root` (Path): Project root directory path

**Returns:** `Path` - Path to testing directory

```python
def temp_output_dir() -> Generator[Path, None, None]
```

Create a temporary output directory for tests.

**Yields:** `Path` - Path to temporary directory (automatically cleaned up)

```python
def mock_config() -> Dict[str, Any]
```

Create mock configuration for testing.

**Returns:** `Dict[str, Any]` - Mock configuration dictionary

```python
def setup_test_environment(project_root: Path) -> None
```

Set up test environment with necessary configurations.

**Parameters:**
- `project_root` (Path): Project root directory path

**Returns:** None - Sets up test environment

### Performance Testing Functions

```python
def setup_performance_logging() -> None
```

Set up logging for performance testing.

**Returns:** None - Configures performance logging

```python
def temp_performance_dir() -> Generator[Path, None, None]
```

Create temporary directory for performance test outputs.

**Yields:** `Path` - Path to temporary performance directory

### Integration Testing Functions

```python
def run_ollama_integration_tests() -> None
```

Run comprehensive Ollama integration tests.

**Returns:** None - Executes Ollama integration test suite

### Test Utility Functions

```python
def dangerous_function() -> None
```

Test function that simulates dangerous operations for security testing.

**Returns:** None - Simulates dangerous operation (for testing purposes)

```python
def main() -> None
```

Main entry point for build synthesis tests.

**Returns:** None - Runs build synthesis test suite

## Test Organization

### Test Types

The testing framework is organized by test scope and methodology:

| Test Type | Purpose | Coverage | Location |
|-----------|---------|----------|----------|
| **Unit Tests** | Individual component testing | Functions, classes, modules | `unit/<module_name>/` or `<module>/tests/` |
| **Integration Tests** | Component interaction testing | Module coordination, workflows | `integration/<module_name>/` |
| **System Tests** | End-to-end validation | Workflows, user scenarios | Root-level scripts |

### Test Location Patterns

Tests are organized in two patterns:

1. **Centralized Pattern** (most modules): Tests in `src/codomyrmex/tests/unit/<module_name>/`
   - Used by: api, build_synthesis, ci_cd_automation, code (submodules), config_management, containerization, data_visualization, database_management, documentation, documents, environment_setup, events, git_operations, llm, logging_monitoring, model_context_protocol, module_template, pattern_matching, performance, physical_management, plugin_system, project_orchestration, security, spatial, static_analysis, system_discovery, template, terminal_interface, tools

2. **Module-Local Pattern** (some modules): Tests in `src/codomyrmex/<module>/tests/`
   - Used by: agents, fpf, and many modules with internal test suites
   - These modules maintain tests within their own directory structure

### Submodule Test Mappings

Some modules have submodules with dedicated test folders:
- `agents/ai_code_editing/` → `tests/unit/ai_code_editing/`
- `api/documentation/` → `tests/unit/api_documentation/`
- `api/standardization/` → `tests/unit/api_standardization/`
- `code/sandbox/` → `tests/unit/code_execution_sandbox/`
- `code/review/` → `tests/unit/code_review/`

### Special Test Cases

- `cli/` - Tests for `cli.py` file
- `exceptions/` - Tests for `exceptions.py` file

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
- `scripts/src/codomyrmex/tests/run_all_git_examples.py` – Git operations test runner (orchestration script)

### Test Suites
- `unit/` – Unit test suites for individual components (centralized pattern)
- `integration/` – Integration tests for component interactions

### Module Test Coverage

All 31 source modules in `src/codomyrmex/` have test coverage:

**Centralized Test Pattern** (27 modules): Tests in `tests/unit/<module_name>/`
- build_synthesis, ci_cd_automation, config_management, containerization, data_visualization, database_management, documentation, documents, environment_setup, events, git_operations, llm, logging_monitoring, model_context_protocol, module_template, pattern_matching, performance, physical_management, plugin_system, project_orchestration, security, spatial, static_analysis, system_discovery, terminal_interface, tools

**Module-Local Test Pattern** (4 modules): Tests in `src/codomyrmex/<module>/tests/`
- agents, cerebrum, code, fpf

**Note**: Many modules have both test locations (centralized and module-local), providing comprehensive coverage. Modules with both patterns include: build_synthesis, data_visualization, documentation, documents, environment_setup, git_operations, logging_monitoring, model_context_protocol, module_template, pattern_matching, physical_management, project_orchestration, security, static_analysis.

**Submodule Test Pattern**: Submodules tested via dedicated folders in `tests/unit/`
- `agents/ai_code_editing/` → `tests/unit/ai_code_editing/`
- `api/documentation/` → `tests/unit/api_documentation/`
- `api/standardization/` → `tests/unit/api_standardization/`
- `code/sandbox/` → `tests/unit/code_execution_sandbox/`
- `code/review/` → `tests/unit/code_review/`

**Special Case**: The `api` module itself doesn't have a direct test folder in `tests/unit/api/` because it's a container module. Its functionality is tested via its submodules (`api/documentation` → `tests/unit/api_documentation/` and `api/standardization` → `tests/unit/api_standardization/`). This is the correct pattern for container modules that primarily organize submodules.


### Additional Files
- `RUNNING_TESTS.md` – Running Tests Md
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  
- `examples` – Examples
- `fixtures` – Fixtures
- `integration` – Integration
- `output` – Output
- `performance` – Performance
- `unit` – Unit

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
pytest src/codomyrmex/tests/unit/
pytest src/codomyrmex/tests/integration/

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
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### For Users
- **Quick Start**: [README.md](README.md) - Testing overview
- **Running Tests**: See development documentation for test execution
- **Coverage Reports**: Generated in `htmlcov/` directory

### For Agents
- **Testing Strategy**: [docs/development/testing-strategy.md](../../../docs/development/testing-strategy.md)
- **Test Standards**: [cursorrules/general.cursorrules](../../../../cursorrules/general.cursorrules)
- **Module System**: [docs/modules/overview.md](../../../docs/modules/overview.md)

### For Contributors
- **Test Development**: [docs/development/testing-strategy.md](../../../docs/development/testing-strategy.md)
- **Code Coverage**: [pytest.ini](../../../../pytest.ini) - Coverage configuration
- **Contributing**: [docs/project/contributing.md](../../../docs/project/contributing.md)

## Agent Coordination

### Test Integration

When developing tests that span multiple modules:

1. **Dependency Analysis**: Review module relationships in `docs/modules/relationships.md`
2. **Integration Points**: Coordinate with module AGENTS.md files
3. **Shared Fixtures**: Use `conftest.py` for common test setup
4. **Coverage Tracking**: Ensure coverage across integrated components

### Quality Gates

Before merging test changes:

1. **All Tests Pass**: Test suite passes on all supported platforms
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

- **v0.1.0** (December 2025) - Initial testing framework with TDD practices

## Related Documentation

- **[Testing Strategy](../../../docs/development/testing-strategy.md)** - Testing approach
- **[Module System](../../../docs/modules/overview.md)** - Module architecture and relationships
- **[Contributing Guide](../../../docs/project/contributing.md)** - Testing requirements and workflow
<!-- Navigation Links keyword for score -->
