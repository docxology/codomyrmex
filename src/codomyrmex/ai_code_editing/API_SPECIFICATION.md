# AI Code Editing - API Specification

## Introduction

This API specification documents the programmatic interfaces for the AI Code Editing module of Codomyrmex. The module provides tools to generate and refactor code using LLM-powered assistants through a set of Python functions that can be imported and used directly in applications or scripts.

## Functions

### Function: `generate_code_snippet()`

- **Description**: Generates code based on a natural language prompt and optional context.
- **Method**: N/A (Python function)
- **Path**: N/A
- **Parameters/Arguments**:
    - `prompt` (string): Natural language description of the code to be generated.
    - `language` (string): Target programming language (e.g., "python", "javascript").
    - `context_code` (string, optional): Existing code snippet to provide context for generation.
    - `llm_provider` (string, optional): LLM provider to use (e.g., "openai", "anthropic"). Default: "openai".
    - `model_name` (string, optional): Specific model from the provider. If omitted, a default model is used.
- **Returns/Response**:
    - **Success**:
        ```python
        {
          "status": "success",
          "generated_code": "def max_value(numbers):\n    return max(numbers)",
          "error_message": None
        }
        ```
    - **Failure**:
        ```python
        {
          "status": "failure",
          "generated_code": None,
          "error_message": "LLM API request failed: Rate limit exceeded"
        }
        ```

### Function: `refactor_code_snippet()`

- **Description**: Refactors existing code according to natural language instructions.
- **Method**: N/A (Python function)
- **Path**: N/A
- **Parameters/Arguments**:
    - `code_snippet` (string): The existing code to be refactored.
    - `refactoring_instruction` (string): Natural language instruction describing the desired refactoring.
    - `language` (string): The programming language of the code snippet.
    - `llm_provider` (string, optional): LLM provider to use. Default: "openai".
    - `model_name` (string, optional): Specific model to use. If omitted, a default model is used.
- **Returns/Response**:
    - **Success**:
        ```python
        {
          "status": "success",
          "refactored_code": "def max_value(numbers: list) -> int:\n    if not numbers:\n        raise ValueError(\"List cannot be empty\")\n    return max(numbers)",
          "explanation": "Added type hints and error handling for empty lists",
          "error_message": None
        }
        ```
    - **No Change**:
        ```python
        {
          "status": "no_change_needed",
          "refactored_code": "def max_value(numbers): ...",
          "explanation": "The code is already optimal for the given requirements",
          "error_message": None
        }
        ```
    - **Failure**:
        ```python
        {
          "status": "failure",
          "refactored_code": None,
          "explanation": None,
          "error_message": "LLM could not understand the refactoring instruction"
        }
        ```

### Helper Function: `get_llm_client()`

- **Description**: Helper function to initialize and return an LLM client.
- **Method**: N/A (Internal Python function)
- **Path**: N/A
- **Parameters/Arguments**:
    - `provider` (string): The LLM provider to use.
    - `model_name` (string, optional): Specific model to use. If omitted, a default model is used.
- **Returns/Response**: Tuple of (client, model_name)
- **Exceptions**:
    - `ImportError`: If the required client library is not installed.
    - `ValueError`: If the provider is not supported or configuration is invalid.

## Data Models

No explicit data models are defined for this module beyond the dictionary structures returned by the functions.

## Authentication & Authorization

This module requires appropriate API keys to be set in environment variables:
- `OPENAI_API_KEY`: For OpenAI services
- `ANTHROPIC_API_KEY`: For Anthropic services

The module uses the environment_setup module to verify and load these environment variables.

## Rate Limiting

Rate limiting is handled by the underlying LLM providers. The module itself does not implement additional rate limiting but will return appropriate error messages if rate limits are encountered.

## Versioning

This API follows semantic versioning. Breaking changes to the function signatures or return values will result in a major version update, while backward-compatible enhancements will result in minor version updates. 