---
description: Property-based testing using Hypothesis/similar. Use when writing tests for serialization, parsing, normalization, validators, data structures, or pure functions. Based on Trail of Bits skill.
---

# Property-Based Testing (Trail of Bits)

Crossover workflow from `property-based-testing@trailofbits` Claude Code skill.

Read the full skill:

```
view_file ~/.claude/plugins/cache/trailofbits/property-based-testing/1.1.0/skills/property-based-testing/SKILL.md
```

## Auto-Detection Triggers

Invoke when you see: `encode`/`decode`, `serialize`/`deserialize`, `normalize`, `validate`, `is_valid`, custom collections, pure functions, sorting/ordering.

## Property Catalog

| Property | Formula | When to Use |
|----------|---------|-------------|
| **Roundtrip** | `decode(encode(x)) == x` | Serialization pairs |
| **Idempotence** | `f(f(x)) == f(x)` | Normalization, formatting |
| **Invariant** | Property holds before/after | Any transformation |
| **Commutativity** | `f(a, b) == f(b, a)` | Binary/set operations |
| **Oracle** | `new_impl(x) == reference(x)` | Optimization, refactoring |
| **No Exception** | No crash on valid input | Baseline property |

**Strength hierarchy**: No Exception → Type Preservation → Invariant → Idempotence → Roundtrip

## Python Example (Hypothesis)

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_roundtrip(s):
    assert decode(encode(s)) == s

@given(st.text())
def test_normalize_idempotent(s):
    assert normalize(normalize(s)) == normalize(s)
```
