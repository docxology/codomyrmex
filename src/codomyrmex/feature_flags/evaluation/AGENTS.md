# Codomyrmex Agents — src/codomyrmex/feature_flags/evaluation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Stateless feature flag evaluation engine. Resolves flag on/off state for a given
`EvaluationContext` by applying a three-stage pipeline: global kill-switch →
targeting rules (OR logic) → percentage rollout via deterministic SHA-256 hash.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `FlagEvaluator` | Stateless evaluator; entry point for all flag resolution |
| `__init__.py` | `FlagEvaluator.evaluate()` | Run full 3-stage pipeline, return `EvaluationResult` |
| `__init__.py` | `FlagEvaluator.evaluate_targeting_rules()` | OR-logic scan across `TargetingRule` list |
| `__init__.py` | `FlagEvaluator.evaluate_percentage_rollout()` | Deterministic SHA-256 bucket check (0.01% granularity via mod 10000) |
| `__init__.py` | `FlagDefinition` | Dataclass: `name`, `enabled`, `percentage` (0.0–100.0), `targeting_rules` |
| `__init__.py` | `TargetingRule` | Dataclass: `attribute`, `operator` (eq/neq/in/contains/gt/lt/gte/lte), `value`; `.matches(context)` |

## Operating Contracts

- `FlagEvaluator` is stateless — safe to instantiate once and reuse across all evaluations.
- Percentage rollout uses `sha256(f"{flag.name}:{user_id}") % 10000` — same user always gets same result for a given flag.
- Targeting rules use OR semantics: at least one rule must match for evaluation to proceed to percentage rollout.
- Unknown operators in `TargetingRule.matches()` return `False` and log a warning — not an error.
- `EvaluationResult.reason` always identifies the stage that stopped evaluation: `flag_disabled`, `targeting_rules_no_match`, `percentage_rollout:N%`, or `enabled`.

## Integration Points

- **Depends on**: `feature_flags.strategies` (`EvaluationContext`, `EvaluationResult`, `EvaluationStrategy`)
- **Used by**: `feature_flags.core.manager` (flag resolution), `feature_flags.rollout` (percentage-based deploys)

## Navigation

- **📁 Parent**: [feature_flags](../README.md)
- **🏠 Root**: ../../../../README.md
