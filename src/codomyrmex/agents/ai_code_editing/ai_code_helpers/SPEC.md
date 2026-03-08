# AI Code Helpers - Specification
**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Technical specification for the `ai_code_helpers` subpackage, which provides multi-provider LLM-powered code generation, analysis, refactoring, and documentation through a unified Python API. All functions delegate to external LLM providers and return structured dictionaries with results and metadata.

## Design Principles

- **Zero-Mock Policy**: No mocks, stubs, or fake data. Functions raise `RuntimeError` or `ValueError` on failure; they never return placeholder results.
- **Explicit Failure**: All provider errors are caught, logged, and re-raised as `RuntimeError` with the original message. No silent fallbacks.
- **Multi-Provider Abstraction**: A single `get_llm_client(provider, model_name)` factory initializes any supported provider. Provider-specific logic is encapsulated within each function.
- **Typed Models**: Request and result structures use dataclasses with enum fields for compile-time safety (`CodeLanguage`, `CodeComplexity`, `CodeStyle`).

## Architecture

```
ai_code_helpers/
    __init__.py        # Public API surface (21 exports)
    models.py          # Enums: CodeLanguage (23 langs), CodeComplexity, CodeStyle
                       # Dataclasses: CodeGenerationRequest, CodeRefactoringRequest,
                       #              CodeAnalysisRequest, CodeGenerationResult
    config.py          # get_llm_client(), DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL,
                       #   MAX_RETRIES, RETRY_DELAY
    generation.py      # generate_code_snippet(), generate_code_batch(),
                       #   generate_code_documentation()
    analysis.py        # analyze_code_quality(), compare_code_versions()
    refactoring.py     # refactor_code_snippet()
    utils.py           # get_supported_languages(), get_supported_providers(),
                       #   get_available_models(), validate_api_keys(), setup_environment()
```

## Functional Requirements

### FR-1: Code Generation
- `generate_code_snippet(prompt, language, provider, ...)` returns `dict` with `generated_code`, `language`, `provider`, `model`, `execution_time`, `tokens_used`, `metadata`.
- `generate_code_batch(requests, parallel, max_workers)` returns `list[CodeGenerationResult]` preserving input order.
- `generate_code_documentation(code, language, doc_type, ...)` supports doc_type values: `"comprehensive"`, `"api"`, `"inline"`, `"readme"`.

### FR-2: Code Analysis
- `analyze_code_quality(code, language, analysis_type, ...)` supports analysis_type values: `"comprehensive"`, `"security"`, `"performance"`, `"maintainability"`.
- `compare_code_versions(code1, code2, language, ...)` returns `dict` with `comparison`, `language`, `provider`, `model`, `execution_time`, `tokens_used`.

### FR-3: Code Refactoring
- `refactor_code_snippet(code, refactoring_type, language, preserve_functionality, ...)` returns `dict` with `original_code`, `refactored_code`, `refactoring_type`, `language`, `execution_time`.

### FR-4: Provider Management
- `get_llm_client(provider, model_name)` returns `tuple[Any, str]` (client instance, resolved model name).
- Supported providers: `"openai"`, `"anthropic"`, `"google"`, `"ollama"`.
- Missing SDK raises `ImportError`; missing API key raises `ValueError`.

## Interface Contracts

```python
# Provider initialization
def get_llm_client(provider: str, model_name: str | None = None) -> tuple[Any, str]: ...

# Generation
def generate_code_snippet(
    prompt: str, language: str, provider: str = "google",
    model_name: str | None = None, context: str | None = None,
    max_length: int | None = None, temperature: float = 0.7, **kwargs
) -> dict[str, Any]: ...

def generate_code_batch(
    requests: list[CodeGenerationRequest], provider: str = "google",
    model_name: str | None = None, parallel: bool = False,
    max_workers: int = 4, **kwargs
) -> list[CodeGenerationResult]: ...

def generate_code_documentation(
    code: str, language: str, doc_type: str = "comprehensive",
    provider: str = "google", model_name: str | None = None, **kwargs
) -> dict[str, Any]: ...

# Analysis
def analyze_code_quality(
    code: str, language: str, analysis_type: str = "comprehensive",
    provider: str = "google", model_name: str | None = None, **kwargs
) -> dict[str, Any]: ...

def compare_code_versions(
    code1: str, code2: str, language: str,
    provider: str = "google", **kwargs
) -> dict[str, Any]: ...

# Refactoring
def refactor_code_snippet(
    code: str, refactoring_type: str, language: str,
    provider: str = "google", preserve_functionality: bool = True, **kwargs
) -> dict[str, Any]: ...
```

## Dependencies

- `codomyrmex.logging_monitoring.core.logger_config` (structured logging)
- `codomyrmex.performance` (optional performance monitoring decorator)
- `codomyrmex.llm.providers.ollama_manager` (optional Ollama backend)
- External SDKs (optional, guarded by `try/except ImportError`):
  - `openai` (OpenAI provider)
  - `anthropic` (Anthropic provider)
  - `google.genai` (Google Gemini provider)

## Constraints

- All provider calls require valid API keys in environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` or `GOOGLE_API_KEY`).
- Batch parallel execution uses `ThreadPoolExecutor` -- not async.
- `CodeLanguage` enum defines 23 supported languages; unsupported languages may still work but are not validated.
- Default provider is `"google"` (Gemini); callers must explicitly pass `provider` to use other backends.

## Navigation

- Parent: [`agents/ai_code_editing/`](../README.md)
- Grandparent: [`agents/`](../../README.md)
