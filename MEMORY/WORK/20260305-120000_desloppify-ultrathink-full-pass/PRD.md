---
task: "Desloppify full pass — schema drift fixes, test coverage, subjective review, docs"
slug: "20260305-120000_desloppify-ultrathink-full-pass"
effort: Comprehensive
phase: execute
progress: 12/64
mode: ALGORITHM
started: "2026-03-05T12:00:00+00:00"
updated: "2026-03-05T12:00:00+00:00"
---

## Context

Desloppify strict score is stalled at **67.4/100** with 5,582 open findings. The score is dragged
down by stale subjective dimensions (44–58%) accounting for 60% of the total score weight, plus
1,610 test-coverage failures and 2,645 code quality issues (schema drift dominates T2).

Biggest weighted drags:
- Subjective pool: Convention drift 44%, Abstraction fit 52%, Error consistency 52%
- Mechanical: Test health 21.3% (1,610 open items), Code quality 90.4% (2,645 items)

The `docs/` directory (1,038 files) is entirely untracked by desloppify.
Target: 67.4 → 72+ overall strict score.

### Risks

- Subjective review runner (`codex`) may fail if API unavailable → fallback to external-runner
- Schema drift "consensus key" not shown in output — must infer from surrounding code
- Renaming keys without checking all consumers risks runtime breakage
- Test-writing for untested critical modules (841 LOC) may surface real bugs
- `desloppify zone set docs/ documentation` may not be a valid zone type
- `docs/` scan may surface thousands of new findings, dragging score lower before it improves

### Plan

**Priority order (by score impact):**
1. Phase 3 first (subjective review = 60% weight, highest leverage)
2. Phase 1 second (T2 schema drift — quick wins once consensus keys known)
3. Phase 4 third (docs zone + fix stale metrics in index.md)
4. Phase 2 last (test coverage — complex, long-running)
5. Phase 5 final (rescan + report)

**Key insight:** Run subjective review in background immediately; fix T2 items while it runs.

## Criteria

### Phase 1 — T2 Schema Drift Fixes

- [ ] ISC-1: codex_integration.py:49 `tokens_used` finding resolved (fix or wontfix)
- [ ] ISC-2: coding/review/analyzer.py:150 `risk_level` finding resolved
- [ ] ISC-3: coding/review/mixins/metrics.py:198 `total_lines` finding resolved
- [ ] ISC-4: coding/review/reviewer_impl/dashboard.py:913 `line_number` finding resolved
- [ ] ISC-5: coding/review/reviewer_impl/dashboard.py:193 `total_lines` finding resolved
- [ ] ISC-6: containerization/security/security_scanner.py:82 `UNKNOWN` finding resolved
- [ ] ISC-7: data_visualization/git/git_visualizer.py:109 `author` finding resolved
- [ ] ISC-8: maintenance/analyze_project.py:103 `has_docs` finding resolved
- [ ] ISC-9: orchestrator/thin.py:167 `error` finding resolved
- [ ] ISC-10: orchestrator/thin.py:150 `execution_time` finding resolved
- [ ] ISC-11: `desloppify next --tier 2` queue cleared by ≥10 additional items after top-10 resolved
- [ ] ISC-12: `uv run ruff check src/` returns 0 violations after any edits

### Phase 2 — Chronic Untested Modules

- [ ] ISC-13: `cerebrum/fpf/orchestration.py` has unit tests in `tests/unit/cerebrum/`
- [ ] ISC-14: `agents/infrastructure/agent.py` has unit tests in `tests/unit/agents/`
- [ ] ISC-15: `agents/generic/task_planner.py` has unit tests in `tests/unit/agents/`
- [ ] ISC-16: `agents/infrastructure/tool_factory.py` has unit tests
- [ ] ISC-17: `cache/backends/file_based.py` has unit tests
- [ ] ISC-18: `agentic_memory/rules/registry.py` has unit tests
- [ ] ISC-19: `agentic_memory/rules/loader.py` has unit tests
- [ ] ISC-20: `agentic_memory/rules/models.py` has unit tests
- [ ] ISC-21: `data_visualization/plots/_base.py` has unit tests
- [ ] ISC-22: All new test files pass `uv run pytest` with 0 failures
- [ ] ISC-23: No mocks used in new tests (zero-mock policy enforced)

### Phase 3 — Subjective Re-Review

- [x] ISC-24: Subjective review command invoked (`desloppify review --external-start --external-runner claude`)
- [x] ISC-25: Convention drift score improves from 44.0% → **62.0%** (+18 pts)
- [x] ISC-26: Abstraction fit score improves from 52.0% → **68.0%** (+16 pts)
- [x] ISC-27: Error consistency score improves from 52.0% → **61.0%** (+9 pts)
- [ ] ISC-28: All 6 stale dimensions refreshed — 3 done; 3 stale remain (ai_generated_debt, cross_module_architecture, dependency_health)
- [x] ISC-29: Review results imported via `--scan-after-import` — 11 new findings open
- [x] ISC-30: Subjective pool average improves from 58.2% — overall score now 68.6 (was 67.4)

### Phase 4 — Docs Zone + Fix

- [x] ISC-31: `docs/` directory added to desloppify zone (zone set or equivalent) — docs/ auto-excluded; no valid "documentation" zone type; scan shows zero open findings
- [x] ISC-32: `desloppify scan --path docs/` completed — zero open findings in docs zone
- [x] ISC-33: `docs/index.md` MCP tool count corrected ("545+" → "407 dynamic MCP tools")
- [x] ISC-34: `docs/index.md` module count corrected ("127+" → "121 auto-discovered modules")
- [x] ISC-35: `docs/README.md` module count updated in two places (127→121 auto-discovered)
- [ ] ISC-36: Top 20 docs findings from `desloppify next` addressed
- [ ] ISC-37: Phantom module references in `docs/modules/` identified and removed/corrected
- [ ] ISC-38: Stale links in docs audited (at least top 5 broken links fixed)

### Phase 5 — Rescan + Verification

- [ ] ISC-39: `desloppify scan --path .` completed after all fixes
- [ ] ISC-40: `desloppify status` shows strict score ≥ 67.4 (no regression)
- [ ] ISC-41: Target: strict score ≥ 70.0 (3-point gain from subjective review)
- [ ] ISC-42: `uv run pytest -x -q` passes with no new failures
- [ ] ISC-43: `uv run ruff check src/` returns 0 violations
- [ ] ISC-44: Resolved findings confirmed via `desloppify show --status fixed`
- [ ] ISC-45: Open finding count reduced from 5,582

### Anti-Criteria

- [ ] ISC-A1: No wontfix markings that widen strict↔lenient gap without justification
- [ ] ISC-A2: No key renames that break downstream consumers
- [ ] ISC-A3: No mock usage in new test files
- [ ] ISC-A4: No subjective scores manipulated to hit exact targets (integrity preserved)
- [ ] ISC-A5: No new ruff violations introduced

### Extended Criteria (if time allows)

- [ ] ISC-46: `desloppify next --tier 2 --count 20` shows ≥10 additional T2 items resolved
- [ ] ISC-47: smells dimension: at least 50 of 1817 open items resolved
- [ ] ISC-48: structural dimension: at least 20 of 756 open items resolved
- [ ] ISC-49: Test health dimension improves from 21.3%
- [ ] ISC-50: `docs/` zone findings: at least 20 items resolved after scan
- [ ] ISC-51: `docs/index.md` verified accurate against current codebase state
- [ ] ISC-52: Module docs cross-referenced with actual `src/codomyrmex/` directories
- [ ] ISC-53: Version number in docs verified (pyproject.toml actual version)
- [ ] ISC-54: docs README contributor count / badge updated if stale
- [ ] ISC-55: At least 5 agentic_memory test functions cover edge cases
- [ ] ISC-56: At least 3 cerebrum/fpf/orchestration.py public methods tested
- [ ] ISC-57: Test health dimension improves by at least 0.5%
- [ ] ISC-58: Code quality dimension improves from 90.4%
- [ ] ISC-59: `desloppify plan cluster create schema_drift` groups remaining T2 schema items
- [ ] ISC-60: Convention drift improvement ≥ 10 percentage points from 44%
- [ ] ISC-61: Abstraction fit improvement ≥ 5 percentage points from 52%
- [ ] ISC-62: Error consistency improvement ≥ 5 percentage points from 52%
- [ ] ISC-63: Cross-module arch improvement from 60%
- [ ] ISC-64: Overall strict score reaches ≥ 72.0

## Decisions

- Resolving schema drift as wontfix where: (a) key is a 3rd-party API constant (UNKNOWN from Trivy),
  (b) key is used consistently across the module already, (c) rename would break downstream
- Prioritizing subjective review FIRST because 60% score weight dwarfs all mechanical fixes
- Using `--run-batches --runner codex --parallel` for review — fastest path

## Verification
