# Prompt Engineering Module — Agent Coordination

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Prompt Engineering Module

Provides tools for prompt template management, version tracking,
optimization strategies, and evaluation scoring. Part of the
Codomyrmex modular development platform.

## Key Capabilities

- **`PromptTemplate`** -- Reusable prompt template with variable placeholders and rendering.
- **`TemplateRegistry`** -- Registry for managing collections of prompt templates.
- **`PromptVersion`** -- Versioned snapshot of a prompt template.
- **`VersionManager`** -- Version history tracking with diff and rollback.
- **`OptimizationStrategy`** -- Enum: CONCISE, DETAILED, CHAIN_OF_THOUGHT, FEW_SHOT.
- **`OptimizationResult`** -- Result of a prompt optimization with token reduction estimate.
- **`PromptOptimizer`** -- Applies optimization strategies to templates.
- **`EvaluationCriteria`** -- Single evaluation criterion with scorer function and weight.

## Agent Usage Patterns

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

## Key Components

| Export | Type |
|--------|------|
| `PromptTemplate` | Public API |
| `TemplateRegistry` | Public API |
| `get_default_registry` | Public API |
| `PromptVersion` | Public API |
| `VersionManager` | Public API |
| `OptimizationStrategy` | Public API |
| `OptimizationResult` | Public API |
| `PromptOptimizer` | Public API |
| `EvaluationCriteria` | Public API |
| `EvaluationResult` | Public API |
| `PromptEvaluator` | Public API |
| `get_default_criteria` | Public API |
| `score_relevance` | Public API |
| `score_response_length` | Public API |
| `score_structure` | Public API |

## Source Files

| File | Description |
|------|-------------|
| `evaluation.py` | Prompt Evaluation and Scoring |
| `optimization.py` | Prompt Optimization Utilities |
| `templates.py` | Prompt Template Management |
| `versioning.py` | Prompt Version Tracking |

## Internal Dependencies

- `codomyrmex.exceptions`
- `codomyrmex.schemas`

## Integration Points

- **Docs**: [Module Documentation](../../../docs/modules/prompt_engineering/README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k prompt_engineering -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, full API access | TRUSTED |
| **Architect** | Read + Design | API review, template system design, optimization strategy evaluation | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, prompt quality validation | OBSERVED |
| **Researcher** | Read-only | Query templates, evaluate quality scores, inspect version history | SAFE |

### Engineer Agent
**Use Cases**: Design and optimize prompts using `PromptTemplate`, `PromptOptimizer`, and `VersionManager`. Create templates, apply optimization strategies (CONCISE, CHAIN_OF_THOUGHT, FEW_SHOT), and track prompt versions.

### Architect Agent
**Use Cases**: Design prompt template systems, review `TemplateRegistry` organization, evaluate optimization strategy selection, plan versioning workflows.

### QATester Agent
**Use Cases**: Validate prompt effectiveness via `PromptEvaluator` and `EvaluationCriteria`. Test template rendering, round-trip version tracking, and optimization accuracy.

### Researcher Agent
**Use Cases**: Querying template registries, evaluating prompt quality scores, and inspecting version history for research analysis.
