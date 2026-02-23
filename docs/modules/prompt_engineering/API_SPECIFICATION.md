# Prompt Engineering API Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `prompt_engineering` module provides template management, version tracking, optimization strategies, and evaluation scoring for prompts. It covers the full lifecycle from authoring and versioning through optimization and quality assessment.

## Templates API

### PromptTemplate (dataclass)

A reusable prompt template with `{variable_name}` placeholders.

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `name` | `str` | (required) | Template name |
| `template_str` | `str` | (required) | Template string with `{var}` placeholders |
| `variables` | `list[str]` | auto-detected | Expected variable names |
| `version` | `str` | `"1.0.0"` | Version string |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

**Methods:**

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `render` | `(**kwargs: Any) -> str` | `str` | Render with variable values. Raises `KeyError` if missing |
| `validate` | `(**kwargs: Any) -> list[str]` | `list[str]` | List of missing variable names |
| `to_dict` | `() -> dict[str, Any]` | `dict` | Convert to dictionary |
| `from_dict` | `(data: dict) -> PromptTemplate` | `PromptTemplate` | Create from dictionary (classmethod) |

### TemplateRegistry

Registry for managing collections of prompt templates.

```python
TemplateRegistry(config: Any | None = None)
```

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `add` | `(template: PromptTemplate) -> None` | `None` | Register. Raises `ValueError` if name exists |
| `update` | `(template: PromptTemplate) -> None` | `None` | Add or replace |
| `get` | `(name: str) -> PromptTemplate` | `PromptTemplate` | Retrieve. Raises `KeyError` if not found |
| `remove` | `(name: str) -> PromptTemplate` | `PromptTemplate` | Remove and return. Raises `KeyError` if not found |
| `list` | `() -> list[str]` | `list[str]` | Sorted template names |
| `list_templates` | `() -> list[PromptTemplate]` | `list[PromptTemplate]` | All templates sorted by name |
| `render` | `(template_name, /, **kwargs) -> str` | `str` | Render template by name |
| `search` | `(query: str) -> list[PromptTemplate]` | `list[PromptTemplate]` | Search by name or metadata keyword |
| `export_all` | `() -> list[dict]` | `list[dict]` | Export all as dictionaries |
| `import_all` | `(data, overwrite=False) -> int` | `int` | Import from dicts; returns count imported |

**Properties:** `size` (number of templates).

### get_default_registry

```python
def get_default_registry() -> TemplateRegistry
```

Returns the module-level default template registry singleton.

---

## Versioning API

### PromptVersion (dataclass)

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `version` | `str` | (required) | Version string (e.g., "1.0.0") |
| `template` | `PromptTemplate` | (required) | The template at this version |
| `created_at` | `datetime` | now (UTC) | Creation timestamp |
| `changelog` | `str` | `""` | Description of changes |
| `author` | `str` | `""` | Who made the change |
| `metadata` | `dict[str, Any]` | `{}` | Additional metadata |

**Methods:** `to_dict()`, `from_dict()` (classmethod).

### VersionManager

Manages version history for prompt templates with diff and rollback.

```python
VersionManager()
```

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `create_version` | `(template, changelog, author, bump, version_override) -> PromptVersion` | `PromptVersion` | Create new version (auto-increments) |
| `get_version` | `(template_name, version=None) -> PromptVersion` | `PromptVersion` | Get specific or latest version |
| `list_versions` | `(template_name) -> list[PromptVersion]` | `list[PromptVersion]` | All versions chronologically |
| `list_template_names` | `() -> list[str]` | `list[str]` | All template names with versions |
| `diff` | `(template_name, version_a, version_b) -> str` | `str` | Unified diff between versions |
| `rollback` | `(template_name, target_version) -> PromptVersion` | `PromptVersion` | Create rollback version |
| `get_latest_version` | `(template_name) -> PromptVersion` | `PromptVersion` | Latest version shortcut |
| `version_count` | `(template_name) -> int` | `int` | Number of versions |
| `export_history` | `(template_name) -> list[dict]` | `list[dict]` | Export version history as dicts |

**`create_version()` parameters:**

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `template` | `PromptTemplate` | (required) | Template to version |
| `changelog` | `str` | `""` | Change description |
| `author` | `str` | `""` | Author name |
| `bump` | `str` | `"patch"` | Version bump level: "major", "minor", "patch" |
| `version_override` | `str \| None` | `None` | Explicit version (overrides auto-increment) |

---

## Optimization API

### OptimizationStrategy (Enum)

| Value | Description |
|:------|:------------|
| `CONCISE` | Reduce verbosity, remove filler phrases |
| `DETAILED` | Add structure with role, task, constraints, output format sections |
| `CHAIN_OF_THOUGHT` | Add step-by-step reasoning scaffold |
| `FEW_SHOT` | Inject examples before the prompt |

### OptimizationResult (dataclass)

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `original` | `PromptTemplate` | (required) | Original template |
| `optimized` | `PromptTemplate` | (required) | Optimized template |
| `strategy` | `OptimizationStrategy` | (required) | Strategy used |
| `changes` | `list[str]` | `[]` | Description of changes made |
| `metadata` | `dict[str, Any]` | `{}` | Additional metadata |

**Properties:**

| Property | Type | Description |
|:---------|:-----|:------------|
| `token_reduction_estimate` | `float` | Ratio of optimized/original word count (< 1.0 = shorter) |

### PromptOptimizer

```python
PromptOptimizer()
```

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `optimize` | `(template, strategy, **kwargs) -> OptimizationResult` | `OptimizationResult` | Optimize with strategy. Raises `ValueError` for unknown strategy |
| `bulk_optimize` | `(templates, strategy, **kwargs) -> list[OptimizationResult]` | `list[OptimizationResult]` | Optimize multiple templates |
| `available_strategies` | `() -> list[str]` | `list[str]` | Sorted strategy value strings |
| `set_few_shot_examples` | `(examples: list[dict[str, str]]) -> None` | `None` | Set examples for FEW_SHOT strategy |

---

## Evaluation API

### EvaluationCriteria (dataclass)

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `name` | `str` | (required) | Criterion name |
| `weight` | `float` | (required) | Weight for weighted average |
| `scorer_fn` | `Callable[[str, str], float]` | (required) | Takes (prompt, response), returns 0.0-1.0 |
| `description` | `str` | `""` | Human-readable description |

**Methods:**

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `score` | `(prompt: str, response: str) -> float` | `float` | Run scorer, clamped to 0.0-1.0 |

### EvaluationResult (dataclass)

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `prompt` | `str` | (required) | The evaluated prompt |
| `response` | `str` | (required) | The evaluated response |
| `scores` | `dict[str, float]` | `{}` | Per-criterion scores |
| `weighted_score` | `float` | `0.0` | Weighted total score |
| `details` | `dict[str, Any]` | `{}` | Additional details |

### Built-in Scorer Functions

```python
score_response_length(prompt: str, response: str) -> float  # Length appropriateness
score_relevance(prompt: str, response: str) -> float         # Keyword overlap
score_structure(prompt: str, response: str) -> float         # Formatting quality
score_completeness(prompt: str, response: str) -> float      # Addresses intent
```

### get_default_criteria

```python
def get_default_criteria() -> list[EvaluationCriteria]
```

Returns: relevance (0.35), completeness (0.30), structure (0.20), length (0.15).

### PromptEvaluator

```python
PromptEvaluator(criteria: list[EvaluationCriteria] | None = None)
```

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `evaluate` | `(prompt, response, criteria=None) -> EvaluationResult` | `EvaluationResult` | Evaluate a pair |
| `evaluate_batch` | `(pairs: list[tuple[str, str]]) -> list[EvaluationResult]` | `list[EvaluationResult]` | Evaluate multiple pairs |
| `compare_responses` | `(prompt, responses) -> dict` | `dict` | Compare responses with rankings and stats |
| `add_criteria` | `(criteria: EvaluationCriteria) -> None` | `None` | Add a criterion |
| `remove_criteria` | `(name: str) -> bool` | `bool` | Remove by name |
| `criteria_names` | `() -> list[str]` | `list[str]` | Sorted criterion names |

**Properties:** `criteria` (list copy).

## Error Handling

| Exception | Raised When |
|:----------|:------------|
| `KeyError` | Template not found in registry; missing render variables; version not found |
| `ValueError` | Duplicate template name in registry (use update instead); unknown optimization strategy |
| `PromptEngineeringError` | Module-level operation failures |

## Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **Parent Directory**: [codomyrmex](../README.md)
