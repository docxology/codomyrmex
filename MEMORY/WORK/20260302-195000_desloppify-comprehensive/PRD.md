---
task: Comprehensively desloppify codomyrmex codebase
slug: 20260302-195000_desloppify-comprehensive
effort: Comprehensive
phase: observe
progress: 0/18
mode: algorithm
started: 2026-03-02
updated: 2026-03-02
---

## Context

Full desloppify run on codomyrmex. Starting strict score: **62.8/100**. Target: 95.0 (+32.2 needed).

**Score breakdown:**
- Overall: 62.8/100 | Objective: 78.1/100 | Strict: 62.8/100
- Mechanical pool: 78.1% (40% weight)
- Subjective pool: 52.6% (60% weight) — this is the main lever

**Mechanical dimensions:**
- File health: 88.9% | Code quality: 96.0% | Duplication: 89.6%
- Test health: **6.8%** ← biggest mechanical drag (-6.21 pts)
- Security: 98.5%

**Subjective dimensions (all need work):**
- AI generated debt: 38.0% | Dep health: 44.0% | Error consistency: 45.0%
- Cross-module arch: 48.0% [stale] | Design coherence: 52.0% [stale]
- Abstraction fit: 52.0% [stale] | Elegance: 53.0% (multiple tiers)
- Test strategy: 58.0% | Structure nav: 60.0% | Convention drift: 62.0% [stale]

**Top 5 T1 issues (high confidence):**
1. 901 identical `"""Initialize this instance."""` docstrings — ai_001
2. camelCase placeholder docstrings (is Running., from Dict.) — ai_002
3. logging_monitoring ↔ validation circular import — arch_002
4. git_operations silent fallback for performance decorators — arch_003
5. LLM provider SDKs as hard (non-optional) deps — dep_001

**Open items:** T1:206 | T2:10664 | T3:17729 | T4:8811 | Total: 37,400

### Risks
- Test health at 6.8% (18,803 items) — likely measuring test coverage patterns, not fixable in one pass
- 4 stale subjective dimensions need holistic re-review
- 901 docstring replacements require fix_docstrings_v2.py or per-file edits
- Circular import fix (arch_002) requires creating a new types module

## Criteria

### Subjective Review (60% of score)
- [ ] ISC-1: Holistic review run for all stale dimensions (abstraction_fitness, convention_outlier, cross_module_architecture, design_coherence)
- [ ] ISC-2: Full subjective review run for ai_generated_debt, dependency_health, error_consistency
- [ ] ISC-3: All 10 subjective dimension scores refreshed (no [stale] markers)
- [ ] ISC-4: Strict score improves after review import

### T1 High-Confidence Fixes
- [ ] ISC-5: ai_001 resolved — 901 identical "Initialize this instance." docstrings replaced
- [ ] ISC-6: ai_002 resolved — camelCase placeholder docstrings replaced or deleted
- [ ] ISC-7: arch_002 resolved — logging_monitoring ↔ validation circular import broken
- [ ] ISC-8: arch_003 resolved — git_operations silent performance fallback removed
- [ ] ISC-9: dep_001 resolved — LLM provider SDKs moved to optional extras in pyproject.toml

### Top T2 Mechanical Fixes
- [ ] ISC-10: Top T2 file health items fixed (large files, god classes identified by next)
- [ ] ISC-11: Top T2 code quality items fixed
- [ ] ISC-12: Top T2 duplication items resolved

### Process Verification
- [ ] ISC-13: `desloppify scan --path .` re-run after fixes
- [ ] ISC-14: Strict score higher than 62.8 after rescan
- [ ] ISC-15: T1 open count lower than 206 after fixes
- [ ] ISC-16: Subjective pool average higher than 52.6% after review
- [ ] ISC-17: AI generated debt dimension above 38.0% after fixes
- [ ] ISC-18: No new security issues introduced by changes

## Decisions

## Verification
```bash
desloppify status
desloppify next --count 5
```
