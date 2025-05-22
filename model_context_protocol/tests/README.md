# Testing the Model Context Protocol Module

This document describes how to run tests for the `model_context_protocol` module.

## Overview

Tests for this module primarily focus on validating the Pydantic models for MCP message structures (`MCPToolCall`, `MCPToolResult`, `MCPErrorDetail`) defined in `model_context_protocol/mcp_schemas.py`.

As this module's main role is to define a protocol and provide schema utilities, the tests ensure that these schemas correctly parse valid data, reject invalid data, and enforce the defined constraints (e.g., error object presence on failure).

## Prerequisites

1.  **Python Environment**: A Python 3.8+ environment is recommended.
2.  **Dependencies**: Ensure all dependencies for this module and the project root are installed. From the project root directory (`codomyrmex/`):
    ```bash
    pip install -r requirements.txt
    pip install -r model_context_protocol/requirements.txt 
    # (Ensure pytest is installed, typically via the root requirements.txt or a dev requirements file)
    ```
    Specifically, `pytest` and `pydantic` are required to run these tests.

## Running Tests

All tests for this module are unit tests and can be run using `pytest`.

### From the Project Root Directory (`codomyrmex/`):

To run all tests within the `model_context_protocol` module:
```bash
pytest model_context_protocol/tests/
```

To run tests in a specific file (e.g., `test_mcp_schemas.py`):
```bash
pytest model_context_protocol/tests/unit/test_mcp_schemas.py
```

To run a specific test class or function using the `-k` flag:
```bash
pytest model_context_protocol/tests/unit/test_mcp_schemas.py -k TestMCPToolResult
pytest model_context_protocol/tests/unit/test_mcp_schemas.py -k "TestMCPToolResult and test_valid_success_result"
```

### From the Module Directory (`codomyrmex/model_context_protocol/`):

If your current directory is `model_context_protocol/`:
```bash
pytest tests/
# or
python -m pytest tests/
```

## Test Structure

-   **`tests/unit/`**: Contains unit tests.
    -   `test_mcp_schemas.py`: Unit tests for the Pydantic models in `model_context_protocol.mcp_schemas`.
-   **`tests/integration/`**: Currently, no integration tests are defined for this module, as its primary components are schema definitions and Pydantic models. Future integration tests might involve testing a reference MCP tool implementation or a validator tool if developed.
    -   `.gitkeep`: Placeholder file.

## Writing New Tests

-   **Location**: New unit tests for Pydantic models or other Python utilities should be added to `tests/unit/`.
-   **Framework**: Use `pytest` for writing tests.
-   **Conventions**:
    -   Test filenames should start with `test_`.
    -   Test functions should start with `test_`.
    -   Use descriptive names for test functions and classes.
    -   Organize tests into classes (e.g., `TestMCPToolCall`) for better structure.
-   **Assertions**: Use standard `assert` statements.
-   **Testing Exceptions**: Use `pytest.raises(ExceptionType)` to test for expected exceptions (e.g., `pydantic.ValidationError`).
-   **Coverage**: Aim for comprehensive coverage of the Pydantic model validations, including valid cases, invalid cases for each field, and custom validator logic.

## Troubleshooting Failed Tests

-   **Import Errors (`ModuleNotFoundError`)**: 
    -   Ensure you are running `pytest` from the project root directory (`codomyrmex/`) or that your Python path is correctly set up so that the `model_context_protocol` package and its modules are importable.
    -   Verify that all dependencies, especially `pydantic`, are installed in your active Python environment.
-   **Validation Errors (`pydantic.ValidationError`)**: 
    -   Carefully examine the error output from `pytest`. Pydantic provides detailed information about which field failed validation and why.
    -   Compare the test input data with the Pydantic model definitions in `mcp_schemas.py` and the expected behavior (including custom validators).
-   **Assertion Errors**: Review the assertion that failed and the values involved to understand the discrepancy. 