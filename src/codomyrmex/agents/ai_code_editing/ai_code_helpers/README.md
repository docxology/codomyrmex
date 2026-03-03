# AI Code Helpers
**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `ai_code_helpers` subpackage provides multi-provider LLM-powered code generation, analysis, refactoring, and documentation utilities. It supports OpenAI, Anthropic, Google Gemini, and Ollama as LLM providers, with a unified interface for code operations across all backends. The package includes typed request/result models, batch generation with optional parallelism, and environment validation utilities.

## PAI Integration

| PAI Phase | Function | Usage |
|-----------|----------|-------|
| BUILD | `generate_code_snippet` | Generate code from natural language prompts |
| BUILD | `generate_code_batch` | Batch code generation with parallel execution |
| BUILD | `generate_code_documentation` | Auto-generate docs for existing code |
| VERIFY | `analyze_code_quality` | LLM-powered quality, security, performance analysis |
| VERIFY | `compare_code_versions` | Diff analysis between two code versions |
| BUILD | `refactor_code_snippet` | AI-guided code refactoring |

## Key Exports

| Export | Type | Source File |
|--------|------|-------------|
| `CodeLanguage` | Enum | `models.py` |
| `CodeComplexity` | Enum | `models.py` |
| `CodeStyle` | Enum | `models.py` |
| `CodeGenerationRequest` | dataclass | `models.py` |
| `CodeRefactoringRequest` | dataclass | `models.py` |
| `CodeAnalysisRequest` | dataclass | `models.py` |
| `CodeGenerationResult` | dataclass | `models.py` |
| `get_llm_client` | function | `config.py` |
| `DEFAULT_LLM_PROVIDER` | str (`"google"`) | `config.py` |
| `DEFAULT_LLM_MODEL` | dict | `config.py` |
| `MAX_RETRIES` | int (`3`) | `config.py` |
| `RETRY_DELAY` | float (`1.0`) | `config.py` |
| `generate_code_snippet` | function | `generation.py` |
| `generate_code_batch` | function | `generation.py` |
| `generate_code_documentation` | function | `generation.py` |
| `analyze_code_quality` | function | `analysis.py` |
| `compare_code_versions` | function | `analysis.py` |
| `refactor_code_snippet` | function | `refactoring.py` |
| `get_supported_languages` | function | `utils.py` |
| `get_supported_providers` | function | `utils.py` |
| `get_available_models` | function | `utils.py` |
| `validate_api_keys` | function | `utils.py` |
| `setup_environment` | function | `utils.py` |

## Quick Start

```python
from codomyrmex.agents.ai_code_editing.ai_code_helpers import (
    generate_code_snippet,
    analyze_code_quality,
    refactor_code_snippet,
    get_supported_providers,
    validate_api_keys,
)

# Check available providers
providers = get_supported_providers()  # ["openai", "anthropic", "google", ...]
keys = validate_api_keys()             # {"openai": True, "google": False, ...}

# Generate code
result = generate_code_snippet(
    prompt="Binary search function",
    language="python",
    provider="google",
    temperature=0.5,
)
print(result["generated_code"])

# Analyze code quality
analysis = analyze_code_quality(
    code="def f(x): return x*2",
    language="python",
    analysis_type="comprehensive",
)

# Refactor code
refactored = refactor_code_snippet(
    code="def f(x): return x*2",
    refactoring_type="add_error_handling",
    language="python",
)
```

## Architecture

```
agents/ai_code_editing/ai_code_helpers/
    __init__.py        # Re-exports all public API
    models.py          # CodeLanguage, CodeComplexity, CodeStyle, request/result dataclasses
    config.py          # LLM provider initialization, defaults, retry settings
    generation.py      # generate_code_snippet, generate_code_batch, generate_code_documentation
    analysis.py        # analyze_code_quality, compare_code_versions
    refactoring.py     # refactor_code_snippet
    utils.py           # get_supported_languages/providers/models, validate_api_keys, setup_environment
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/agents/ -k "ai_code" -v
```

## Navigation

- Parent: [`agents/ai_code_editing/`](../README.md)
- Grandparent: [`agents/`](../../README.md)
- Project root: [`/`](../../../../../README.md)
