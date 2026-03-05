---
task: Desloppify deep fix loop — strict score improvement
slug: 20260305-103000_desloppify-deep-fix
effort: Deep
phase: observe
progress: 0/40
mode: ALGORITHM
started: 2026-03-05T10:30:00Z
updated: 2026-03-05T10:30:00Z
---

## Context

User requested "ultrathink /desloppify" — a deep codebase health improvement pass. Current state: strict 73.4/100, target 95.0 (+21.6 needed). 5618 open issues across T1:5, T2:1400, T3:4186, T4:37.

Biggest weighted drags:
- Elegance (65-72%): -11.63 pts total
- Test health (21.9%): -5.21 pts
- Design coherence (66%): -2.34 pts

Strategy: Fix T1 elegance issues first (highest ROI), then T2 unused imports + schema drifts, then run subjective review for stale dimensions to push overall score.

### Risks
- data_visualization scatter consolidation may break callers using plots/scatter.py
- APIAgentSpec refactor is a large structural change — scope carefully
- desloppify `issues list` re-imports sessions and resets wontfix states — patch state-python.json directly for wontfix
- Subjective review stale dimensions won't update without re-running review

## Criteria

- [ ] ISC-1: T1 HE-EL-01 fixed — ScatterPlot alias removed from plots/scatter.py
- [ ] ISC-2: T1 HE-EL-01 resolved in desloppify with concrete attestation
- [ ] ISC-3: T1 HE-EL-02 investigated — plots/ duplicate chart types removed or redirected
- [ ] ISC-4: T1 HE-EL-02 resolved in desloppify with concrete attestation
- [ ] ISC-5: T1 ME-EL-01 fixed — analyzer.py imports from _compat.py, removes inline flag
- [ ] ISC-6: T1 ME-EL-01 resolved in desloppify with concrete attestation
- [ ] ISC-7: T1 LL-EL-01 assessed — APIAgentBase 10-param constructor scoped
- [ ] ISC-8: T1 LL-EL-01 resolved (fixed or scoped wontfix) in desloppify
- [ ] ISC-9: T2 unused import pytest removed from examples/test_fastapi_endpoint.py
- [ ] ISC-10: T2 unused import resolved in desloppify
- [ ] ISC-11: T2 schema drift — codex_integration.py tokens_used key investigated
- [ ] ISC-12: T2 schema drift — analyzer.py risk_level key investigated
- [ ] ISC-13: T2 schema drift — metrics.py total_lines key investigated
- [ ] ISC-14: T2 schema drift — orchestrator/thin.py execution_time key investigated
- [ ] ISC-15: All investigated schema drift items resolved (fixed or justified wontfix)
- [ ] ISC-16: T2 duplication — scripts/llm get_api_key dupe investigated
- [ ] ISC-17: T2 duplication resolved (extracted shared helper or wontfix scripts/)
- [ ] ISC-18: desloppify scan run after fixes to capture cascade effects
- [ ] ISC-19: Stale subjective dimensions reviewed — ai_generated_debt refreshed
- [ ] ISC-20: Stale subjective dimensions reviewed — abstraction_fitness refreshed
- [ ] ISC-21: Stale subjective dimensions reviewed — cross_module_architecture refreshed
- [ ] ISC-22: Stale subjective dimensions reviewed — dependency_health refreshed
- [ ] ISC-23: Stale subjective dimensions reviewed — error_consistency refreshed
- [ ] ISC-24: Elegance open review findings (4 items) investigated via desloppify issues
- [ ] ISC-25: Elegance open review findings actioned (fixed or resolved)
- [ ] ISC-26: Post-fix strict score >= 74.0 (minimum measurable gain)
- [ ] ISC-27: Post-fix strict score >= 75.0 (meaningful gain over 73.4 baseline)
- [ ] ISC-28: No new ruff violations introduced (ruff check src/ passes clean)
- [ ] ISC-29: No test regressions (test count same or higher)
- [ ] ISC-30: T2 auto-fixer checked for unused imports batch
- [ ] ISC-31: T2 dict_keys schema drift batch — all 4 files investigated
- [ ] ISC-32: Additional T2 issues from next --count 20 checked and triaged
- [ ] ISC-33: desloppify plan reviewed for cluster opportunities
- [ ] ISC-34: scripts/ zone confirmed as out-of-scope or set correctly
- [ ] ISC-35: projects/test_project zone confirmed as out-of-scope or set correctly
- [ ] ISC-36: data_visualization plots/ directory assessed for public API callers
- [ ] ISC-37: Review: 4 uninvestigated elegance findings actioned via desloppify issues
- [ ] ISC-38: Final desloppify status shows score improvement
- [ ] ISC-39: Memory updated with new score and key findings
- [ ] ISC-40: Strict score gap (lenient vs strict) < 1.0 (no wontfix abuse)

## Decisions

## Verification
