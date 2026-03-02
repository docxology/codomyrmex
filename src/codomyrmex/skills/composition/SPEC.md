# Skill Composition -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides patterns for composing skills into higher-order constructs: sequential chaining (output of one feeds into the next), parallel execution (all skills run concurrently with the same input), and conditional branching (execute one skill or another based on a predicate).

## Architecture

Builder pattern via `SkillComposer` which creates `ComposedSkill` or `ConditionalSkill` instances. `ComposedSkill` dispatches to chain or parallel mode at execution time. Parallel execution uses `ThreadPoolExecutor`.

## Key Classes

### `ComposedSkill`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `name: str, skills: list, mode: str` | `None` | Create composed skill; mode is `"chain"` or `"parallel"` |
| `execute` | `**kwargs` | `Any` | Chain: pipe output sequentially; Parallel: run all concurrently, return dict |

Chain mode: first skill receives `**kwargs`, subsequent skills receive `input=previous_result`.
Parallel mode: all skills receive `**kwargs`, results keyed by skill metadata name or index.

### `ConditionalSkill`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `condition: Callable, if_skill, else_skill` | `None` | Create conditional with optional else branch |
| `execute` | `**kwargs` | `Any` | Evaluate condition; execute matching branch; returns `None` if no else and condition is False |

### `SkillComposer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `chain` | `*skills` | `ComposedSkill` | Create sequential chain |
| `parallel` | `*skills` | `ComposedSkill` | Create parallel group |
| `conditional` | `condition, if_skill, else_skill` | `ConditionalSkill` | Create conditional branch |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `concurrent.futures.ThreadPoolExecutor` (stdlib)

## Constraints

- Skills must implement an `execute(**kwargs)` method.
- Parallel mode uses an unbounded `ThreadPoolExecutor`; caller should limit the number of skills if resource-constrained.
- Chain mode assumes each skill returns a value that can be passed as `input=` to the next skill.
- Unknown composition modes raise `ValueError`.
- Zero-mock: real skill execution only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Exceptions from individual skills propagate without wrapping.
- `ThreadPoolExecutor` exceptions are raised via `future.result()`.
- All errors logged before propagation.
