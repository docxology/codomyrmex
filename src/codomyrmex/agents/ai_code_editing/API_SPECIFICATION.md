# AI Code Editing - API Specification

## Introduction

This API specification documents the programmatic interfaces for the AI Code Editing module of Codomyrmex. The module provides AI-powered code generation, refactoring, analysis, comparison, and documentation using multiple LLM providers (OpenAI, Anthropic, Google, Ollama).

All functions are importable from `codomyrmex.agents.ai_code_editing`.

## Functions

### Function: `generate_code_snippet(prompt: str, language: str, provider: str = "google", model_name: str | None = None, context: str | None = None, max_length: int | None = None, temperature: float = 0.7, **kwargs) -> dict[str, Any]`

- **Description**: Generate code in the requested language using the configured LLM provider.
- **Parameters**:
    - `prompt` (str): Natural language description of the desired code. Cannot be empty.
    - `language` (str): Target programming language (e.g., `"python"`, `"javascript"`).
    - `provider` (str, optional): LLM provider identifier (`"openai"`, `"anthropic"`, `"google"`, `"ollama"`). Default: `"google"`.
    - `model_name` (str | None, optional): Model override. Default: provider-specific (see Default Models below).
    - `context` (str | None, optional): Supplemental context appended to the prompt.
    - `max_length` (int | None, optional): Token limit for the response.
    - `temperature` (float, optional): Sampling temperature (0.0 to 1.0). Default: `0.7`.
    - `**kwargs`: Provider-specific overrides forwarded to the underlying SDK.
- **Return Value**:
    ```python
    {
        "generated_code": str,
        "language": str,
        "provider": str,
        "model": str,
        "execution_time": float,
        "tokens_used": int | None,
        "metadata": {
            "prompt": str,
            "context": str | None,
            "temperature": float,
            "max_length": int | None
        }
    }
    ```
- **Errors**: Raises `RuntimeError` wrapping `ValueError` for invalid input, `ImportError` for missing SDKs, or provider API errors.

### Function: `refactor_code_snippet(code: str, refactoring_type: str, language: str, provider: str = "google", model_name: str | None = None, context: str | None = None, preserve_functionality: bool = True, **kwargs) -> dict[str, Any]`

- **Description**: Refactor existing code according to the requested refactoring type.
- **Parameters**:
    - `code` (str): Source code to refactor. Cannot be empty.
    - `refactoring_type` (str): Instruction such as `"optimize"`, `"simplify"`, or `"add_error_handling"`.
    - `language` (str): Programming language of the code snippet.
    - `provider` (str, optional): LLM provider identifier. Default: `"google"`.
    - `model_name` (str | None, optional): Model override.
    - `context` (str | None, optional): Additional context for the LLM.
    - `preserve_functionality` (bool, optional): When `True`, instructs the LLM to maintain behavior. Default: `True`.
    - `**kwargs`: Provider-specific overrides forwarded to the SDK.
- **Return Value**:
    ```python
    {
        "original_code": str,
        "refactored_code": str,
        "refactoring_type": str,
        "language": str,
        "provider": str,
        "model": str,
        "execution_time": float,
        "tokens_used": int | None,
        "metadata": {
            "context": str | None,
            "preserve_functionality": bool
        }
    }
    ```
- **Errors**: Raises `RuntimeError` wrapping `ValueError` for invalid input or provider API errors.

### Function: `analyze_code_quality(code: str, language: str, analysis_type: str = "comprehensive", provider: str = "google", model_name: str | None = None, context: str | None = None, **kwargs) -> dict[str, Any]`

- **Description**: Analyze code quality using an LLM. Supports multiple analysis types.
- **Parameters**:
    - `code` (str): The code to analyze. Cannot be empty.
    - `language` (str): Programming language of the code.
    - `analysis_type` (str, optional): Type of analysis (`"comprehensive"`, `"security"`, `"performance"`, `"maintainability"`). Default: `"comprehensive"`.
    - `provider` (str, optional): LLM provider identifier. Default: `"google"`.
    - `model_name` (str | None, optional): Model override.
    - `context` (str | None, optional): Additional context for analysis.
    - `**kwargs`: Provider-specific overrides.
- **Return Value**:
    ```python
    {
        "code": str,
        "analysis": str,
        "analysis_type": str,
        "language": str,
        "provider": str,
        "model": str,
        "execution_time": float,
        "tokens_used": int | None,
        "metadata": {
            "context": str | None
        }
    }
    ```
- **Errors**: Raises `RuntimeError` wrapping `ValueError` for invalid input or provider API errors.

### Function: `generate_code_batch(requests: list[CodeGenerationRequest], provider: str = "google", model_name: str | None = None, parallel: bool = False, max_workers: int = 4, **kwargs) -> list[CodeGenerationResult]`

- **Description**: Generate multiple code snippets in batch, optionally in parallel using a thread pool.
- **Parameters**:
    - `requests` (list[CodeGenerationRequest]): List of code generation requests. Cannot be empty.
    - `provider` (str, optional): LLM provider identifier. Default: `"google"`.
    - `model_name` (str | None, optional): Model override.
    - `parallel` (bool, optional): Whether to process requests in parallel. Default: `False`.
    - `max_workers` (int, optional): Maximum number of parallel workers. Default: `4`.
    - `**kwargs`: Provider-specific overrides.
- **Return Value**: List of `CodeGenerationResult` dataclass instances. Failed requests return results with empty `generated_code` and an `error` key in `metadata`.
- **Errors**: Raises `ValueError` if `requests` list is empty.

### Function: `compare_code_versions(code1: str, code2: str, language: str, provider: str = "google", model_name: str | None = None, context: str | None = None, **kwargs) -> dict[str, Any]`

- **Description**: Compare two versions of code and provide analysis covering functional differences, performance implications, code quality, maintainability, and best practices.
- **Parameters**:
    - `code1` (str): First version of code. Cannot be empty.
    - `code2` (str): Second version of code. Cannot be empty.
    - `language` (str): Programming language of the code.
    - `provider` (str, optional): LLM provider identifier. Default: `"google"`.
    - `model_name` (str | None, optional): Model override.
    - `context` (str | None, optional): Additional context for comparison.
    - `**kwargs`: Provider-specific overrides.
- **Return Value**:
    ```python
    {
        "code1": str,
        "code2": str,
        "comparison": str,
        "language": str,
        "provider": str,
        "model": str,
        "execution_time": float,
        "tokens_used": int | None,
        "metadata": {
            "context": str | None
        }
    }
    ```
- **Errors**: Raises `RuntimeError` wrapping `ValueError` for invalid input or provider API errors.

### Function: `generate_code_documentation(code: str, language: str, doc_type: str = "comprehensive", provider: str = "google", model_name: str | None = None, context: str | None = None, **kwargs) -> dict[str, Any]`

- **Description**: Generate documentation for code using an LLM.
- **Parameters**:
    - `code` (str): The code to document. Cannot be empty.
    - `language` (str): Programming language of the code.
    - `doc_type` (str, optional): Type of documentation (`"comprehensive"`, `"api"`, `"inline"`, `"readme"`). Default: `"comprehensive"`.
    - `provider` (str, optional): LLM provider identifier. Default: `"google"`.
    - `model_name` (str | None, optional): Model override.
    - `context` (str | None, optional): Additional context for documentation.
    - `**kwargs`: Provider-specific overrides.
- **Return Value**:
    ```python
    {
        "code": str,
        "documentation": str,
        "doc_type": str,
        "language": str,
        "provider": str,
        "model": str,
        "execution_time": float,
        "tokens_used": int | None,
        "metadata": {
            "context": str | None
        }
    }
    ```
- **Errors**: Raises `RuntimeError` wrapping `ValueError` for invalid input or provider API errors.

### Function: `get_llm_client(provider: str, model_name: str | None = None) -> tuple[Any, str]`

- **Description**: Initialize and return the provider client together with the resolved model name.
- **Parameters**:
    - `provider` (str): LLM provider identifier (`"openai"`, `"anthropic"`, `"google"`, `"ollama"`).
    - `model_name` (str | None, optional): Specific model override.
- **Return Value**: Tuple of `(client, resolved_model_name)`.
- **Errors**: Raises `ImportError` when provider SDKs are missing, `ValueError` for unsupported providers or missing API keys, `RuntimeError` for client initialization failures.

### Function: `get_supported_languages() -> list[CodeLanguage]`

- **Description**: Get list of all supported programming languages.
- **Return Value**: List of `CodeLanguage` enum members.

### Function: `get_supported_providers() -> list[str]`

- **Description**: Get list of supported LLM providers. Returns `["openai", "anthropic", "google"]` plus `"ollama"` if the Ollama integration is available.
- **Return Value**: List of provider name strings.

### Function: `get_available_models(provider: str) -> list[str]`

- **Description**: Get list of known models for a given provider.
- **Parameters**:
    - `provider` (str): Provider name (case-insensitive).
- **Return Value**: List of model name strings. Returns empty list for unknown providers.

### Function: `validate_api_keys() -> dict[str, bool]`

- **Description**: Check which LLM providers have API keys configured in environment variables.
- **Return Value**: Dictionary mapping provider name to `True` (key present) or `False` (key missing).

### Function: `setup_environment() -> bool`

- **Description**: Set up environment variables and check dependencies. Calls `check_and_setup_env_vars()` if available, then validates API keys.
- **Return Value**: `True` if at least one provider has a valid API key, `False` otherwise.

## Data Models

### Enums

#### `CodeLanguage(Enum)`
Supported programming languages:
- `PYTHON`, `JAVASCRIPT`, `TYPESCRIPT`, `JAVA`, `CPP`, `CSHARP`, `GO`, `RUST`, `PHP`, `RUBY`, `SWIFT`, `KOTLIN`, `SCALA`, `R`, `MATLAB`, `SHELL`, `SQL`, `HTML`, `CSS`, `XML`, `YAML`, `JSON`, `MARKDOWN`

#### `CodeComplexity(Enum)`
Code complexity levels:
- `SIMPLE = "simple"`
- `INTERMEDIATE = "intermediate"`
- `COMPLEX = "complex"`
- `EXPERT = "expert"`

#### `CodeStyle(Enum)`
Code style preferences:
- `CLEAN = "clean"`
- `VERBOSE = "verbose"`
- `CONCISE = "concise"`
- `FUNCTIONAL = "functional"`
- `OBJECT_ORIENTED = "object_oriented"`
- `PROCEDURAL = "procedural"`

### Dataclasses

#### `CodeGenerationRequest`
```python
@dataclass
class CodeGenerationRequest:
    prompt: str
    language: CodeLanguage
    complexity: CodeComplexity = CodeComplexity.INTERMEDIATE
    style: CodeStyle = CodeStyle.CLEAN
    context: str | None = None
    requirements: list[str] | None = None
    examples: list[str] | None = None
    max_length: int | None = None
    temperature: float = 0.7
```

#### `CodeRefactoringRequest`
```python
@dataclass
class CodeRefactoringRequest:
    code: str
    language: CodeLanguage
    refactoring_type: str
    context: str | None = None
    preserve_functionality: bool = True
    add_tests: bool = False
    add_documentation: bool = False
```

#### `CodeAnalysisRequest`
```python
@dataclass
class CodeAnalysisRequest:
    code: str
    language: CodeLanguage
    analysis_type: str
    context: str | None = None
    include_suggestions: bool = True
```

#### `CodeGenerationResult`
```python
@dataclass
class CodeGenerationResult:
    generated_code: str
    language: CodeLanguage
    metadata: dict[str, Any]
    execution_time: float
    tokens_used: int | None = None
    confidence_score: float | None = None
```

## Default Models

| Provider | Default Model |
|----------|--------------|
| `openai` | `gpt-3.5-turbo` |
| `anthropic` | `claude-instant-1` |
| `google` | `gemini-flash-latest` |
| `ollama` | `llama3.1:latest` |

The default provider for all functions is `"google"`.

## Authentication & Authorization

This module requires appropriate API keys to be set in environment variables:
- `OPENAI_API_KEY`: For OpenAI services
- `ANTHROPIC_API_KEY`: For Anthropic services
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`: For Google Gemini services (either variable is accepted)
- Ollama: No API key required (local server)

Use `validate_api_keys()` to check which providers are configured, or `setup_environment()` to perform a full environment check.

## Rate Limiting

Rate limiting is handled by the underlying LLM providers. The module itself does not implement additional rate limiting. `generate_code_batch()` with `parallel=True` uses a `ThreadPoolExecutor` with a configurable `max_workers` limit (default 4).

## Versioning

This API follows semantic versioning. Breaking changes to function signatures or return values will result in a major version update.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
