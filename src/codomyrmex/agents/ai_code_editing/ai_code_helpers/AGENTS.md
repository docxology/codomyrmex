# AI Code Helpers - Agent Coordination
**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `ai_code_helpers` subpackage provides agent-consumable functions for LLM-powered code generation, analysis, refactoring, and documentation. Agents use these helpers to delegate code-level tasks to external LLM providers (OpenAI, Anthropic, Google Gemini, Ollama) through a unified interface.

## Key Files

| File | Purpose |
|------|---------|
| `config.py` | Provider initialization via `get_llm_client()`, default model/provider settings |
| `models.py` | Typed request/result dataclasses: `CodeGenerationRequest`, `CodeGenerationResult`, enums |
| `generation.py` | `generate_code_snippet`, `generate_code_batch` (parallel), `generate_code_documentation` |
| `analysis.py` | `analyze_code_quality` (comprehensive/security/performance/maintainability), `compare_code_versions` |
| `refactoring.py` | `refactor_code_snippet` with configurable refactoring type and functionality preservation |
| `utils.py` | `get_supported_languages`, `get_supported_providers`, `validate_api_keys`, `setup_environment` |

## MCP Tools Available

No MCP tools defined in this subpackage. Code helpers are consumed directly by agent code, not exposed as MCP tools.

## Agent Instructions

1. **Always validate API keys** before invoking generation/analysis functions -- call `validate_api_keys()` to confirm the target provider has a key set.
2. **Use typed request models** (`CodeGenerationRequest`, `CodeRefactoringRequest`, `CodeAnalysisRequest`) for batch operations; they enforce valid `CodeLanguage` enum values.
3. **Handle RuntimeError** -- all functions raise `RuntimeError` on LLM failures (wrapping `ValueError`, `ImportError`, and API errors).
4. **Batch generation** supports parallel execution via `generate_code_batch(requests, parallel=True, max_workers=4)` using ThreadPoolExecutor.
5. **Provider selection** defaults to `"google"` (Gemini); override with the `provider` parameter on every call.

## Operating Contracts

- All functions raise `ValueError` for empty or invalid inputs (never silently degrade).
- All functions raise `RuntimeError` when LLM provider calls fail (no fallback to stubs).
- `get_llm_client` raises `ImportError` if the required SDK is not installed.
- Return dictionaries always include `execution_time`, `tokens_used`, `provider`, `model` keys.
- Batch results preserve input order even when processed in parallel.

## Common Patterns

```python
from codomyrmex.agents.ai_code_editing.ai_code_helpers import (
    generate_code_snippet,
    analyze_code_quality,
    CodeGenerationRequest,
    CodeLanguage,
    generate_code_batch,
)

# Single generation
result = generate_code_snippet(
    prompt="Fibonacci with memoization",
    language="python",
    provider="anthropic",
)

# Batch generation (parallel)
requests = [
    CodeGenerationRequest(prompt="merge sort", language=CodeLanguage.PYTHON),
    CodeGenerationRequest(prompt="binary tree", language=CodeLanguage.PYTHON),
]
results = generate_code_batch(requests, parallel=True, max_workers=2)

# Quality analysis
analysis = analyze_code_quality(
    code="def add(a, b): return a + b",
    language="python",
    analysis_type="security",
)
```

## PAI Agent Role Access Matrix

| Role | Access Level | Typical Usage |
|------|-------------|---------------|
| Engineer | Full | Code generation, refactoring, analysis |
| Architect | Read | Code analysis, version comparison |
| QATester | Read | Quality analysis, test suggestion via parent module |

## Navigation

- Parent: [`agents/ai_code_editing/`](../README.md)
- Grandparent: [`agents/`](../../README.md)
