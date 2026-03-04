---
description: Systematic debugging following Superpowers methodology. Use for any bug, test failure, or unexpected behavior. Iron law — no fixes without root cause investigation first.
---

# Systematic Debugging (Superpowers)

Crossover workflow from `superpowers@superpowers-marketplace` Claude Code skill.

Read the full skill:

```
view_file ~/.claude/plugins/cache/superpowers-marketplace/superpowers/4.3.1/skills/systematic-debugging/SKILL.md
```

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

## Four Phases

### Phase 1: Root Cause Investigation

1. Read error messages carefully (stack traces, line numbers)
2. Reproduce consistently
3. Check recent changes (`git diff`)
4. Gather evidence at component boundaries
5. Trace data flow backward to source

### Phase 2: Pattern Analysis

1. Find working examples in same codebase
2. Compare against references (read completely, don't skim)
3. Identify every difference, however small

### Phase 3: Hypothesis and Testing

1. Form single hypothesis: "I think X because Y"
2. Test with SMALLEST possible change
3. One variable at a time

### Phase 4: Implementation

1. Create failing test case
2. Implement single fix for root cause
3. Verify fix
4. **If 3+ fixes failed**: STOP — question the architecture

## Red Flags — Return to Phase 1

- "Quick fix for now, investigate later"
- "Just try changing X and see"
- "I don't fully understand but this might work"
- Proposing solutions before tracing data flow
- Each fix reveals new problem in different place
