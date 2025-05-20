# Build Synthesis - Test Suite

This directory contains the test suite for the Build Synthesis module of the Codomyrmex project.

## Test Organization

The tests are organized into two main categories:

- **Unit Tests**: Located in `unit/`. These tests focus on testing individual functions or classes in isolation, such as template processing logic or build script parsing, with dependencies mocked.
- **Integration Tests**: Located in `integration/`. These tests verify the interaction between different components or with actual build tools on small, controlled examples. For example, testing the `trigger_build` MCP tool with a mock project structure.

## Running Tests

### Prerequisites

- Python 3.8 or higher
- All development dependencies installed:
  ```bash
  # Ensure you are in the project root directory
  pip install -r build_synthesis/requirements.txt
  pip install -r requirements.txt  # Root project requirements
  pip install pytest pytest-mock  # Test dependencies
  ```
- Any build tools that the module itself might invoke (e.g., `make`, `docker`, Python's `build` module) should be available in the system PATH if tests rely on them.

### Running Unit Tests

From the project root:

```bash
# Run all unit tests for build_synthesis
pytest build_synthesis/tests/unit/

# Run a specific test file (replace with actual file name)
# pytest build_synthesis/tests/unit/test_orchestrator.py

# Run a specific test class (replace with actual names)
# pytest build_synthesis/tests/unit/test_orchestrator.py::TestBuildOrchestrator

# Run a specific test (replace with actual names)
# pytest build_synthesis/tests/unit/test_orchestrator.py::TestBuildOrchestrator::test_some_specific_logic
```

### Running Integration Tests

**Note**: Integration tests might perform actual build operations on mock projects or synthesize code structures, which could create temporary files or directories. These should be cleaned up by the tests.

```bash
# Run all integration tests for build_synthesis
pytest build_synthesis/tests/integration/

# Example: Run a specific integration test for triggering a build
# pytest build_synthesis/tests/integration/test_trigger_build_integration.py
```

## Writing New Tests

### Unit Tests

- Each core piece of logic (e.g., functions for parsing build files, generating parts of a synthesized module, utility functions) should have corresponding unit tests.
- Use `unittest.mock` to mock external system calls (e.g., `subprocess.run` if calling build tools directly) or dependencies on other Codomyrmex modules.
- Test for various inputs, including edge cases and expected failure conditions.

### Integration Tests

- Integration tests should verify the end-to-end flow of MCP tools like `trigger_build` and `synthesize_code_component`.
- For `trigger_build`, set up a minimal, mock project structure (e.g., in a temporary directory) with a simple build script (e.g., a Makefile or `pyproject.toml`) and verify that the build is invoked and expected artifacts are (notionally) produced or logs indicate success.
- For `synthesize_code_component`, provide a specification and verify that the generated directory structure and key files match expectations based on `template/module_template/`.
- Ensure tests clean up any files or directories they create.

## Test Coverage

To generate a coverage report (ensure `pytest-cov` is installed):

```bash
# Run tests with coverage for the build_synthesis module
pytest --cov=build_synthesis build_synthesis/tests/

# Generate an HTML report (output will be in an htmlcov/ directory)
pytest --cov=build_synthesis --cov-report=html build_synthesis/tests/
```

## Test Structure

(Briefly describe how the tests are organized within this `tests/` directory, e.g., by feature, by type (unit, integration), etc.)

- `unit/`: Contains unit tests.
- `integration/`: Contains integration tests.
- `fixtures/` or `data/`: Contains test data or fixtures.

## Writing Tests

(Provide guidelines or link to resources on how to write new tests for this module.)

- Follow the existing testing patterns and frameworks.
- Ensure tests are independent and can be run in any order.
- Mock external dependencies for unit tests where appropriate.
- Aim for good test coverage.

## Troubleshooting Failed Tests

(Offer advice on how to debug or troubleshoot failing tests.)

- Check logs for detailed error messages.
- Ensure all prerequisites are met and the environment is correctly configured. 