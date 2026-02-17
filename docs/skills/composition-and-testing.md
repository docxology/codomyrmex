# Building Jigs and Quality Control

In a craftsperson's workshop, a jig is a device that holds a workpiece in
a fixed position while tools are applied to it. Jigs enforce repeatability:
the same operation produces the same result every time. The composition
subsystem serves this role -- it assembles individual skills into repeatable
pipelines. Testing is the quality control station where every tool and every
jig is verified before it reaches production.

## Composition Patterns

The `SkillComposer` class provides three patterns for combining skills. Each
pattern returns a composite object that can be executed like a single skill.

### Chain (Sequential)

A chain passes the output of each skill as `input` to the next. This is the
most common pattern: parse, transform, write.

```python
from codomyrmex.skills.composition import SkillComposer

composer = SkillComposer()
pipeline = composer.chain(parse_skill, transform_skill, write_skill)
result = pipeline.execute(source="raw data")
```

Internally, `ComposedSkill` with `mode="chain"` calls each skill in order.
The first skill receives the original keyword arguments; subsequent skills
receive only `input=<previous_result>`.

### Parallel (Concurrent)

A parallel group runs all skills concurrently with the same input, using a
`ThreadPoolExecutor`. Results are collected into a dictionary keyed by skill
name.

```python
group = composer.parallel(lint_skill, type_check_skill, security_scan_skill)
results = group.execute(file_path="/src/main.py")
# results == {"lint": ..., "type_check": ..., "security_scan": ...}
```

### Conditional (Branching)

A conditional skill evaluates a predicate and routes execution to one of two
branches.

```python
branch = composer.conditional(
    condition=lambda file_path, **kw: file_path.endswith(".py"),
    if_skill=python_linter,
    else_skill=generic_linter,
)
result = branch.execute(file_path="/src/main.py")
```

The `ConditionalSkill` class accepts any callable that returns `bool`. If
`else_skill` is `None` and the condition is `False`, execution returns `None`.

## SkillComposer API Summary

| Method | Returns | Description |
|---|---|---|
| `chain(*skills)` | `ComposedSkill` | Sequential pipeline |
| `parallel(*skills)` | `ComposedSkill` | Concurrent execution group |
| `conditional(cond, if_skill, else_skill)` | `ConditionalSkill` | Branching logic |

## Testing Framework

The workshop quality control station is `SkillTestRunner`. It supports three
inspection modes.

### Test Cases

Each test case is a dictionary with `name`, `inputs`, and an optional
`expected` value. If `expected` is provided, the runner checks equality. If
omitted, any non-raising execution counts as a pass.

```python
from codomyrmex.skills.testing import SkillTestRunner

runner = SkillTestRunner()
results = runner.test_skill(my_skill, [
    {"name": "basic input", "inputs": {"source": "x = 1"}, "expected": "x = 1\n"},
    {"name": "empty input", "inputs": {"source": ""}},
])

for r in results:
    status = "PASS" if r.passed else "FAIL"
    print(f"  [{status}] {r.name}")
```

### Metadata Validation

`validate_skill()` inspects a skill for structural completeness: presence of
`metadata`, `execute`, and `validate_params`. It returns a dictionary with
`valid` (bool) and `issues` (list of strings).

```python
report = runner.validate_skill(my_skill)
if not report["valid"]:
    for issue in report["issues"]:
        print(f"  Issue: {issue}")
```

### Benchmarking

`benchmark_skill()` runs a skill N times and reports timing statistics.

```python
bench = runner.benchmark_skill(my_skill, iterations=500, source="x = 1")
print(f"Average: {bench['avg_time']:.4f}s, Min: {bench['min_time']:.4f}s")
```

## Quality Assurance Philosophy

Testing skills follows the same principle as testing workshop tools: verify
the tool works correctly in isolation, then verify it works correctly in the
jig. Composition tests should exercise the full pipeline, not just individual
skills. The `SkillTestRunner` handles isolation; combining it with
`SkillExecutor.execute_chain` tests the assembled workflow.

## Key Source Paths

- `src/codomyrmex/skills/composition/__init__.py` -- `SkillComposer`,
  `ComposedSkill`, `ConditionalSkill`
- `src/codomyrmex/skills/testing/__init__.py` -- `SkillTestRunner`,
  `SkillTestResult`

## Cross-References

- For the full API specification, see the
  [Module Documentation](../modules/skills/README.md).
- For how skills are sourced, versioned, and governed, continue to
  [Marketplace and Governance](./marketplace-and-governance.md).
- Return to the [Workshop Overview](./index.md) for the full reading guide.
