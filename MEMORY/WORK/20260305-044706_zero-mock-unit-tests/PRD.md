---
task: Write zero-mock unit tests for five codomyrmex modules
slug: 20260305-044706_zero-mock-unit-tests
effort: Advanced
phase: complete
progress: 16/16
mode: ALGORITHM
started: 2026-03-05T04:47:06
updated: 2026-03-05T04:55:00
---

## Context

Five priority modules needed zero-mock unit tests. OBSERVE discovered that
most files already had test coverage, so the actual work became:

1. **agentic_memory/rules/** — comprehensive `test_rules.py` already existed (passes)
2. **cache/backends/file_based.py** — covered in `test_cache.py`, but missing dedicated deep coverage → new `test_file_based.py` written
3. **data_visualization/plots/_base.py** — `test_plots_base.py` existed but had 3 failures (options field nonexistent) AND a circular import bug at collection time → full rewrite with lazy imports
4. **agents/infrastructure/** — `test_infrastructure_agent.py` already existed and passed
5. **agents/generic/task_planner.py** — no test existed → new `test_task_planner.py` written

### Risks
- data_visualization circular import: `scatter_plot → engines/__init__ → plotter → scatter_plot`; fixed by moving import inside test methods
- Code quality hook flags test AAA boilerplate as DRY violations — false positives, no action needed

### Plan
- Fix `test_plots_base.py`: lazy imports + remove 3 impossible `options` attribute tests
- Write `test_task_planner.py`: full coverage of TaskStatus, Task, TaskPlanner
- Write `test_file_based.py`: deep coverage of FileBasedCache including stats, TTL, persistence, edge cases

## Criteria

- [x] ISC-1: test_plots_base.py collects without ImportError
- [x] ISC-2: test_plots_base.py has 0 failures
- [x] ISC-3: BasePlot construction tests cover all dataclass fields
- [x] ISC-4: BasePlot render() tests verify div tag and class name
- [x] ISC-5: BasePlot to_dict() tests verify all 5 keys
- [x] ISC-6: BasePlot save() tests verify file creation and content
- [x] ISC-7: BasePlot to_html() tests verify base64 PNG img tag
- [x] ISC-8: _fig_to_base64 static method tested with valid PNG magic bytes
- [x] ISC-9: test_task_planner.py created at correct path
- [x] ISC-10: TaskStatus enum all 5 values tested
- [x] ISC-11: Task dataclass defaults and independence tested
- [x] ISC-12: TaskPlanner.create_task tested including sequential IDs
- [x] ISC-13: TaskPlanner.get_ready_tasks tested with dependency completion
- [x] ISC-14: TaskPlanner.get_task_execution_order tested with diamond dependency
- [x] ISC-15: test_file_based.py covers FileBasedCache stats tracking
- [x] ISC-16: All 161 new tests pass with 0 failures

## Decisions

- Moved BasePlot imports to inside test methods to break circular import chain in data_visualization package
- Removed 3 tests referencing `p.options` — BasePlot has no `options` field (dataclass has title/width/height/data only)
- Code quality hook DRY warnings on test files are false positives; not addressed

## Verification

- `uv run pytest test_task_planner.py test_file_based.py test_plots_base.py --no-cov`: **161 passed**
- `uv run pytest test_rules.py test_infrastructure_agent.py test_cache.py --no-cov`: **219 passed**
- Total new test functions written: **161** across 3 files (2 new + 1 rewritten)
