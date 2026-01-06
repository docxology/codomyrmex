# AI Code Editing - API Specification

## Introduction

This API specification documents the programmatic interfaces for the AI Code Editing module of Codomyrmex. The module provides tools to generate and refactor code using LLM-powered assistants through a set of Python functions that can be imported and used directly in applications or scripts.

## Functions

### Function: `generate_code_snippet(prompt: str, language: str, provider: str = "openai", model_name: Optional[str] = None, context: Optional[str] = None, max_length: Optional[int] = None, temperature: float = 0.7, **kwargs) -> dict`

- **Description**: Generate code in the requested language using the configured LLM provider.
- **Parameters**:
    - `prompt`: Natural language description of the desired code.
    - `language`: Target programming language.
    - `provider`: LLM provider identifier (`"openai"`, `"anthropic"`, or `"google"`).
    - `model_name`: Optional model override.
    - `context`: Optional supplemental context appended to the prompt.
    - `max_length`: Optional token limit for the response (provider specific).
    - `temperature`: Sampling temperature passed to the provider.
    - `**kwargs`: Provider specific overrides forwarded to the underlying SDK.
- **Return Value**:
    ```python
    {
        "generated_code": <str>,
        "language": <str>,
        "provider": <str>,
        "model": <str>,
        "execution_time": <float>,
        "tokens_used": <int | None>,
        "metadata": {
            "prompt": <str>,
            "context": <str | None>,
            "temperature": <float>,
            "max_length": <int | None>
        }
    }
    ```
- **Errors**: Raises `ValueError` for invalid input and `RuntimeError` when provider calls fail.

### Function: `refactor_code_snippet(code: str, refactoring_type: str, language: str, provider: str = "openai", model_name: Optional[str] = None, context: Optional[str] = None, preserve_functionality: bool = True, **kwargs) -> dict`

- **Description**: Refactor existing code according to the requested refactoring type.
- **Parameters**:
    - `code`: Source code to refactor.
    - `refactoring_type`: High level instruction such as `"optimize"`, `"simplify"`, or `"add_error_handling"`.
    - `language`: Programming language of the code snippet.
    - `provider`: LLM provider identifier.
    - `model_name`: Optional model override.
    - `context`: Additional context for the LLM.
    - `preserve_functionality`: When `True`, instructs the LLM to maintain behavior.
    - `**kwargs`: Provider specific overrides forwarded to the SDK.
- **Return Value**:
    ```python
    {
        "original_code": <str>,
        "refactored_code": <str>,
        "refactoring_type": <str>,
        "language": <str>,
        "provider": <str>,
        "model": <str>,
        "execution_time": <float>,
        "tokens_used": <int | None>,
        "metadata": {
            "context": <str | None>,
            "preserve_functionality": <bool>
        }
    }
    ```
- **Errors**: Raises `ValueError` for invalid input and `RuntimeError` when provider calls fail.

### Helper Function: `get_llm_client(provider: str, model_name: Optional[str] = None) -> tuple`

- **Description**: Initialize and return the provider client together with the resolved model name.
- **Returns**: A tuple `(client, resolved_model_name)` ready for requests.
- **Raises**: `ImportError` when provider SDKs are missing, `ValueError` for unsupported providers or missing API keys.

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
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
