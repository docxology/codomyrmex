# AI Code Editing - Test Suite

This directory contains the test suite for the AI Code Editing module of the Codomyrmex project.

## Test Organization

The tests are organized into two main categories:

- **Unit Tests**: Located in `unit/`. These tests focus on testing individual functions in isolation, with dependencies mocked.
- **Integration Tests**: Located in `integration/`. These tests verify the interaction between different components or with real LLM APIs (when enabled).

## Running Tests

### Prerequisites

- Python 3.8 or higher
- All development dependencies installed:
  ```bash
  pip install -r ai_code_editing/requirements.txt
  pip install -r requirements.txt  # Root project requirements
  pip install pytest pytest-mock  # Test dependencies
  ```

### Running Unit Tests

From the project root:

```bash
# Run all unit tests
pytest ai_code_editing/tests/unit/

# Run a specific test file
pytest ai_code_editing/tests/unit/test_ai_code_helpers.py

# Run a specific test class
pytest ai_code_editing/tests/unit/test_ai_code_helpers.py::TestGenerateCodeSnippet

# Run a specific test
pytest ai_code_editing/tests/unit/test_ai_code_helpers.py::TestGenerateCodeSnippet::test_generate_code_success_openai
```

### Running Integration Tests

**Note**: Integration tests may connect to actual LLM APIs and consume API quota if environment variables are configured.

```bash
# Run integration tests (only when you're ready to test with real APIs)
pytest ai_code_editing/tests/integration/

# To run integration tests with external API calls disabled
MOCK_LLM_API=true pytest ai_code_editing/tests/integration/
```

## Writing New Tests

### Unit Tests

- Each function should have at least one corresponding test.
- Use `unittest.mock` to mock external dependencies.
- Test both success and failure cases.
- Pay special attention to edge cases.
- Example:

```python
from unittest.mock import patch, MagicMock

@patch('module_path.dependency')
def test_my_function(mock_dependency):
    mock_dependency.return_value = "mocked result"
    result = my_function()
    assert result == "expected result"
```

### Integration Tests

- Integration tests should verify that components interact correctly.
- Consider using environment variables to toggle between real and mock services.
- Document any resources created during tests and ensure they are cleaned up properly.
- Example:

```python
import os
import pytest

@pytest.mark.skipif(os.environ.get("MOCK_LLM_API") == "true", 
                   reason="Skipping test that calls real API")
def test_integration_with_real_api():
    # Test that calls a real API
```

## Test Coverage

To generate a coverage report:

```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
pytest --cov=ai_code_editing ai_code_editing/tests/

# Generate an HTML report
pytest --cov=ai_code_editing --cov-report=html ai_code_editing/tests/
``` 