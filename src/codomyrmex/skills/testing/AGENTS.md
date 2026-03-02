# Testing - Agent Coordination

## Purpose

Skill testing framework providing test execution, metadata validation, and performance benchmarking for Codomyrmex skill instances.

## Key Components

| Component | Role |
|-----------|------|
| `SkillTestRunner` | Runs test cases, validates skill metadata, and benchmarks skill performance |
| `SkillTestResult` | Dataclass: name, passed, expected, actual, error |

## Operating Contracts

- `test_skill(skill, test_cases)` accepts test case dicts with keys: `name`, `inputs` (kwargs dict), `expected` (optional).
- If `expected` is provided, the test passes when `actual == expected`. If omitted, the test passes if no exception is raised.
- `validate_skill(skill)` checks for `metadata` attribute (with `name`, `description`, `id` fields) and `execute`/`validate_params` methods.
- `benchmark_skill(skill, iterations, **kwargs)` runs the skill `iterations` times (default 100) and returns min/max/avg/total times and error count.
- Skill instances must have an `execute(**kwargs)` method.

## Integration Points

- **Parent module**: `skills/` provides skill discovery and invocation management.
- **Skill interface**: Tested skills must implement `execute()`, `validate_params()`, and expose a `metadata` attribute with `name`, `description`, `id`.

## Navigation

- **Parent**: [skills/](../README.md)
- **Sibling**: [SPEC.md](SPEC.md)
- **Root**: [/README.md](../../../../README.md)
