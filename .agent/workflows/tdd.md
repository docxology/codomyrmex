---
description: Test-Driven Development following Superpowers methodology. Use when implementing features, fixing bugs, or refactoring. Iron law — no production code without a failing test first.
---

# Test-Driven Development (Superpowers)

Crossover workflow from `superpowers@superpowers-marketplace` Claude Code skill.

Read the full skill:

```
view_file ~/.claude/plugins/cache/superpowers-marketplace/superpowers/4.3.1/skills/test-driven-development/SKILL.md
```

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over. No exceptions.

## Red-Green-Refactor Cycle

### RED — Write Failing Test

- One behavior, clear name, real code (no mocks)
- **Run test, verify it fails for expected reason**

### GREEN — Minimal Code

- Write simplest code to pass the test
- Don't add features, don't "improve" beyond the test

### REFACTOR — Clean Up

- Only after green: remove duplication, improve names, extract helpers
- Keep tests green, don't add behavior

## Rationalizations to Reject

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "TDD will slow me down" | TDD faster than debugging. |
| "Need to explore first" | Fine. Throw away exploration, start with TDD. |

## Verification Checklist

- [ ] Every new function has a test
- [ ] Watched each test fail before implementing
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass, output pristine
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered
