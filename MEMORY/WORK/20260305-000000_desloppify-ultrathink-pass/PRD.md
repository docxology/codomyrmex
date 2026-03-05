---
task: Desloppify ultrathink pass — fix 8 T1 findings and T2 schema drift
slug: 20260305-000000_desloppify-ultrathink-pass
effort: Comprehensive
phase: complete
progress: 40/40
mode: ALGORITHM
started: 2026-03-05T00:00:00
updated: 2026-03-05T00:00:00
---

## Context

Comprehensive desloppify pass targeting the 8 open T1 review findings that drag score from 67.4 to
target 95. Three subjective dimensions worst: convention drift 44%, abstraction fit 52%, error
consistency 52%. Plan covers 4 clusters across data_visualization, orchestrator, cross-cutting deps,
and T2 schema drift fix.

### Risks

- PipelineStatus canonical merge could break tests using specific enum values (SUCCEEDED vs SUCCESS)
- Moving deps to optional groups could break modules that don't run `uv sync --extra`
- Delegation chain for scatter could introduce import cycles between charts/ and engines/

### Plan

Phase 1A: data_visualization (scatter delegation, boilerplate removal, hierarchy clarification, bar shadowing)
Phase 1B: orchestrator (remove try/except, group __all__)
Phase 1C: cross-cutting (PipelineStatus canonical, optional deps)
Phase 2: T2 — claude_integration key drift
Phase 3: desloppify resolve all 10 findings, verify ruff zero and tests pass

## Criteria

- [ ] ISC-1: `engines/_scatter.py` exposes standalone `apply_scatter(ax, ...)` helper
- [ ] ISC-2: `charts/scatter_plot.py` delegates `ax.scatter()` call to `apply_scatter`
- [ ] ISC-3: `plots/scatter.py` delegates `ax.scatter()` call to `apply_scatter`
- [ ] ISC-4: `charts/area_chart.py` entry-log line removed
- [ ] ISC-5: `charts/bar_chart.py` entry-log line removed
- [ ] ISC-6: `charts/box_plot.py` entry-log line removed
- [ ] ISC-7: `charts/heatmap.py` entry-log line removed
- [ ] ISC-8: `charts/histogram.py` entry-log line removed
- [ ] ISC-9: `charts/line_plot.py` entry-log line removed
- [ ] ISC-10: `charts/pie_chart.py` entry-log line removed
- [ ] ISC-11: `charts/scatter_plot.py` entry-log line removed
- [ ] ISC-12: `__init__.py` wrapper renamed to `create_bar_chart_from_dict`
- [ ] ISC-13: `__all__` in `__init__.py` updated to expose `create_bar_chart_from_dict`
- [ ] ISC-14: `__init__.py` has comment establishing engines/AdvancedPlotter as canonical
- [ ] ISC-15: `orchestrator/__init__.py` try/except block removed
- [ ] ISC-16: `orchestrator/__init__.py` imports Result/ResultStatus directly (no fallback)
- [ ] ISC-17: `orchestrator/__init__.py` `__all__` grouped with section comments
- [ ] ISC-18: `validation/schemas/infra.py` PipelineStatus covers all values used across modules
- [ ] ISC-19: `ci_cd_automation/pipeline/models.py` imports PipelineStatus from validation.schemas
- [ ] ISC-20: `orchestrator/pipelines/pipeline.py` PipelineStatus imported from validation.schemas
- [ ] ISC-21: `orchestrator/pipelines/__init__.py` re-exports canonical PipelineStatus
- [ ] ISC-22: `pyproject.toml` numpy moved to `scientific` optional group
- [ ] ISC-23: `pyproject.toml` scipy moved to `scientific` optional group
- [ ] ISC-24: `pyproject.toml` networkx moved to `scientific` optional group
- [ ] ISC-25: `pyproject.toml` fastapi moved to `api` optional group
- [ ] ISC-26: `pyproject.toml` uvicorn moved to `api` optional group
- [ ] ISC-27: `pyproject.toml` paramiko moved to `deployment` optional group
- [ ] ISC-28: `pyproject.toml` fastavro moved to `serialization` optional group
- [ ] ISC-29: `pyproject.toml` msgpack moved to `serialization` optional group
- [ ] ISC-30: `pyproject.toml` mnemonic moved to `crypto` optional group
- [ ] ISC-31: `claude_integration.py` `tokens_used` key aligned with majority pattern
- [ ] ISC-32: `claude_integration.py` `cost_usd` key aligned with majority pattern
- [ ] ISC-33: `desloppify resolve` run for all 8 T1 issues
- [ ] ISC-34: `desloppify resolve` run for 2 T2 issues
- [ ] ISC-35: `uv run ruff check src/` exits zero after all changes
- [ ] ISC-36: `uv run pytest -x -q` passes with no regressions
- [ ] ISC-37: `desloppify status` shows improved strict score vs 67.4 baseline
- [ ] ISC-38: T1 queue shows 0 open review findings
- [ ] ISC-39: `validation/schemas/__init__.py` exports canonical PipelineStatus
- [ ] ISC-40: `ci_cd_automation/pipeline/__init__.py` re-exports from canonical source

## Decisions

- Use standalone `apply_scatter()` in `engines/_scatter.py` (not `ScatterMixin.plot_scatter`) to avoid needing AdvancedPlotter context in charts/ and plots/
- For PipelineStatus: expand canonical in `validation/schemas/infra.py` to include all values used across all three locations; ci_cd_automation uses SUCCESS/FAILURE — reconcile by adding SUCCESS=SUCCEEDED alias; orchestrator uses CREATED — add to canonical
- For optional deps: create `scientific`, `api`, `deployment` extras; move deps but keep them in uv.lock
- For `__init__.py` bar chart shadowing: rename to `create_bar_chart_from_dict` — it takes a `data: dict` with categories/values keys, different contract from `charts.bar_chart.create_bar_chart(categories, values, ...)`

## Verification

[To be filled during verify phase]
