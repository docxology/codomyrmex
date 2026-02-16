# Prompt Engineering Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive prompt template management, version tracking, optimization strategies, and evaluation scoring. Provides tools for the full prompt lifecycle from authoring through optimization and quality assessment.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **`PromptTemplate`** -- Reusable templates with variable placeholders and rendering.
- **`TemplateRegistry`** -- Registry for managing collections of prompt templates.
- **`VersionManager`** -- Version history tracking with diff and rollback.
- **`PromptOptimizer`** -- Strategy-based prompt optimization (CONCISE, DETAILED, CHAIN_OF_THOUGHT, FEW_SHOT).
- **`PromptEvaluator`** -- Multi-criteria evaluation of prompt-response pairs.

## Quick Start

```python
from codomyrmex.prompt_engineering import PromptTemplate, PromptOptimizer, OptimizationStrategy

# Create a template
template = PromptTemplate(
    name="summarize",
    template_str="Summarize the following {content_type}: {text}",
)
rendered = template.render(content_type="article", text="Machine learning is...")

# Optimize a prompt
optimizer = PromptOptimizer()
result = optimizer.optimize(template, OptimizationStrategy.CONCISE)
print(f"Token reduction: {result.token_reduction_estimate:.0%}")
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `PromptTemplate` | Template with variable placeholders |
| `TemplateRegistry` | Template collection management |
| `PromptVersion` | Versioned template snapshot |
| `VersionManager` | Version history with diff/rollback |
| `OptimizationStrategy` | Enum: CONCISE, DETAILED, CHAIN_OF_THOUGHT, FEW_SHOT |
| `PromptOptimizer` | Strategy-based prompt optimizer |
| `EvaluationCriteria` | Criterion with scorer and weight |
| `PromptEvaluator` | Multi-criteria evaluator |

### Functions

| Function | Description |
|----------|-------------|
| `list_templates()` | List templates in the default registry |
| `list_strategies()` | List available optimization strategies |
| `quick_evaluate()` | Quick evaluation with default criteria |
| `score_relevance()` | Keyword overlap scorer |
| `score_completeness()` | Completeness scorer |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k prompt_engineering -v
```

## Related Modules

- [Model Evaluation](../model_evaluation/README.md)
- [LLM](../llm/README.md)

## Navigation

- **Source**: [src/codomyrmex/prompt_engineering/](../../../src/codomyrmex/prompt_engineering/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/prompt_engineering/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/prompt_engineering/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)
