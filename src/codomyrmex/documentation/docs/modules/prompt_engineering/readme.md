# Prompt Engineering Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

Comprehensive prompt template management, version tracking, optimization strategies, and evaluation scoring. Provides tools for the full prompt lifecycle from authoring through optimization and quality assessment.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **THINK** | Construct optimized prompts for LLM capability selection | Direct Python import |
| **BUILD** | Generate structured prompts for Engineer agent code generation tasks | Direct Python import |
| **EXECUTE** | Dynamic prompt construction for agent-to-agent communication | Direct Python import |

PAI agents use prompt engineering during THINK to craft high-quality LLM queries. The Fabric pattern system (240+ patterns) is accessible here; Engineer agents use prompt templates during BUILD for code generation. Prompt optimization improves ISC achievement across all Algorithm phases.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes

- **`PromptTemplate`** -- Reusable prompt template with variable placeholders and rendering.
- **`TemplateRegistry`** -- Registry for managing collections of prompt templates.
- **`PromptVersion`** -- Versioned snapshot of a prompt template.
- **`VersionManager`** -- Version history tracking with diff and rollback.
- **`OptimizationStrategy`** -- Enum: CONCISE, DETAILED, CHAIN_OF_THOUGHT, FEW_SHOT.
- **`OptimizationResult`** -- Result of a prompt optimization with token reduction estimate.
- **`PromptOptimizer`** -- Applies optimization strategies to templates.
- **`EvaluationCriteria`** -- Single evaluation criterion with scorer function and weight.
- **`EvaluationResult`** -- Complete evaluation result for a prompt-response pair.
- **`PromptEvaluator`** -- Evaluates prompt-response pairs against configurable criteria.

### Functions

- **`get_default_registry()`** -- Get the module-level default template registry.
- **`get_default_criteria()`** -- Get default evaluation criteria set.
- **`score_relevance()`** -- Keyword overlap scorer.
- **`score_response_length()`** -- Response length scorer.
- **`score_structure()`** -- Response structure scorer.
- **`score_completeness()`** -- Response completeness scorer.
- **`list_templates()`** -- List templates in the default registry.
- **`list_strategies()`** -- List available optimization strategies.
- **`quick_evaluate()`** -- Quick evaluation with default criteria.

## Quick Start

### Create and Render Templates

```python
from codomyrmex.prompt_engineering import PromptTemplate, TemplateRegistry

template = PromptTemplate(
    name="summarize",
    template_str="Summarize the following {content_type}: {text}",
)
print(template.variables)  # ['content_type', 'text']

rendered = template.render(content_type="article", text="Machine learning is...")
print(rendered)

# Use a registry
registry = TemplateRegistry()
registry.add(template)
output = registry.render("summarize", content_type="paper", text="Deep learning...")
```

### Track Template Versions

```python
from codomyrmex.prompt_engineering import PromptTemplate, VersionManager

vm = VersionManager()

v1 = PromptTemplate(name="qa", template_str="Answer: {question}")
vm.create_version(v1, changelog="Initial version")

v2 = PromptTemplate(name="qa", template_str="Please answer: {question}\nBe concise.")
vm.create_version(v2, changelog="Added politeness and conciseness instruction")

# View diff
print(vm.diff("qa", "1.0.0", "1.0.1"))

# Rollback
vm.rollback("qa", "1.0.0")
```

### Optimize Prompts

```python
from codomyrmex.prompt_engineering import (
    PromptTemplate, PromptOptimizer, OptimizationStrategy
)

optimizer = PromptOptimizer()
template = PromptTemplate(
    name="verbose",
    template_str="I would like you to please explain {topic} in detail",
)

result = optimizer.optimize(template, OptimizationStrategy.CONCISE)
print(result.optimized.template_str)
print(f"Token reduction: {result.token_reduction_estimate:.0%}")
print(f"Changes: {result.changes}")
```

### Evaluate Prompt-Response Quality

```python
from codomyrmex.prompt_engineering import PromptEvaluator

evaluator = PromptEvaluator()
result = evaluator.evaluate(
    prompt="Explain the benefits of test-driven development",
    response="TDD improves code quality by writing tests first. "
             "It catches bugs early and provides living documentation.",
)
print(f"Weighted score: {result.weighted_score:.2f}")
print(f"Per-criterion: {result.scores}")

# Compare multiple responses
comparison = evaluator.compare_responses(
    prompt="What is Python?",
    responses=[
        "Python is a programming language.",
        "Python is a high-level, interpreted programming language known for readability. "
        "It supports multiple paradigms including OOP and functional programming.",
    ],
)
print(f"Best response index: {comparison['best_index']}")
```

## CLI Commands

```bash
# List registered templates
codomyrmex prompt_engineering templates

# List optimization strategies
codomyrmex prompt_engineering strategies

# Evaluate a prompt-response pair
echo '{"prompt": "Explain AI", "response": "AI is..."}' | codomyrmex prompt_engineering evaluate
```

## Directory Structure

- `templates.py` -- PromptTemplate dataclass and TemplateRegistry
- `versioning.py` -- PromptVersion and VersionManager
- `optimization.py` -- OptimizationStrategy, PromptOptimizer
- `evaluation.py` -- EvaluationCriteria, PromptEvaluator, scorer functions
- `__init__.py` -- Public API re-exports, convenience functions, CLI commands

## Exports

| Export | Type | Description |
| :--- | :--- | :--- |
| `PromptTemplate` | Dataclass | Template with variable placeholders |
| `TemplateRegistry` | Class | Template collection management |
| `get_default_registry` | Function | Module-level default registry |
| `PromptVersion` | Dataclass | Versioned template snapshot |
| `VersionManager` | Class | Version history with diff/rollback |
| `OptimizationStrategy` | Enum | CONCISE, DETAILED, CHAIN_OF_THOUGHT, FEW_SHOT |
| `OptimizationResult` | Dataclass | Optimization result with token estimate |
| `PromptOptimizer` | Class | Strategy-based prompt optimizer |
| `EvaluationCriteria` | Dataclass | Criterion with scorer and weight |
| `EvaluationResult` | Dataclass | Evaluation result with scores |
| `PromptEvaluator` | Class | Multi-criteria evaluator |
| `get_default_criteria` | Function | Default criteria preset |
| `score_relevance` | Function | Keyword overlap scorer |
| `score_response_length` | Function | Length appropriateness scorer |
| `score_structure` | Function | Response structure scorer |
| `score_completeness` | Function | Completeness scorer |
| `list_templates` | Function | List default registry templates |
| `list_strategies` | Function | List optimization strategies |
| `quick_evaluate` | Function | Quick evaluation shortcut |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/unit/prompt_engineering/ -v
```

## Consolidated Sub-modules

The following modules have been consolidated into this module as sub-packages:

| Sub-module | Description |
|------------|-------------|
| **`testing/`** | Prompt evaluation, A/B testing, and quality scoring |

Original standalone modules remain as backward-compatible re-export wrappers.

## Navigation

- **Extended Docs**: [docs/modules/prompt_engineering/](../../../docs/modules/prompt_engineering/)
- [API_SPECIFICATION](API_SPECIFICATION.md) | [PAI](PAI.md) | [MCP_TOOL_SPECIFICATION](MCP_TOOL_SPECIFICATION.md)
