---
task: Write comprehensive zero-mock tests for agents/droid module
slug: 20260307-120000_agents-droid-zero-mock-tests
effort: Advanced
phase: execute
progress: 0/24
mode: ALGORITHM
started: 2026-03-07T12:00:00
updated: 2026-03-07T12:05:00
---

## Context

The agents/droid module has 0% coverage. An existing test_run_todo_droid.py covers run_todo_droid.py extensively (68 pass/1 skip), but controller.py, todo.py, tasks.py, and generators/documentation.py are NOT covered. The new test_droid_full.py must cover: DroidConfig validation/from_dict/from_env/with_overrides/to_dict, DroidMetrics snapshot/reset, DroidController lifecycle (start/stop/execute_task/heartbeat/permissions), TodoManager validate/migrate_to_three_columns, all 4 task handlers directly, and documentation generators (assess_readme_quality, assess_agents_quality, assess_technical_accuracy, _compute_overall_score).

Zero-mock policy: no mocks, MagicMock, monkeypatch. LLM/API calls get @pytest.mark.skipif guards. All tests use real objects.

### Risks
- DroidConfig is a frozen dataclass — replace() used by with_overrides
- DroidController.execute_task calls performance_context which may have side effects
- generators/documentation.py has file I/O in assess_documentation_coverage — test pure scoring functions only
- from_env reads os.environ — tests must set real env vars

## Criteria

- [ ] ISC-1: test_droid_full.py exists and is importable without errors
- [ ] ISC-2: DroidMode enum all 4 values are tested
- [ ] ISC-3: DroidStatus enum all 4 values are tested
- [ ] ISC-4: _to_bool() converts all truthy/falsy string inputs correctly
- [ ] ISC-5: DroidConfig.validate() raises ValueError on invalid max_parallel_tasks
- [ ] ISC-6: DroidConfig.validate() raises ValueError on negative max_retry_attempts
- [ ] ISC-7: DroidConfig.validate() raises ValueError on zero heartbeat_interval_seconds
- [ ] ISC-8: DroidConfig.validate() raises ValueError on negative retry_backoff_seconds
- [ ] ISC-9: DroidConfig.from_dict() creates valid config from dict with mode string
- [ ] ISC-10: DroidConfig.from_json() parses JSON string correctly
- [ ] ISC-11: DroidConfig.from_env() reads DROID_IDENTIFIER env var
- [ ] ISC-12: DroidConfig.with_overrides() returns new config with changed field
- [ ] ISC-13: DroidConfig.to_dict() serialises mode as string value
- [ ] ISC-14: DroidConfig.allowed and .blocked properties return frozenset or None
- [ ] ISC-15: DroidMetrics.snapshot() returns dict with all expected keys
- [ ] ISC-16: DroidMetrics.reset() zeros all counters and clears last_error
- [ ] ISC-17: DroidController.start() transitions status from STOPPED to IDLE
- [ ] ISC-18: DroidController.stop() transitions status to STOPPED
- [ ] ISC-19: DroidController.execute_task() calls handler and increments tasks_executed
- [ ] ISC-20: DroidController.execute_task() raises RuntimeError when status is STOPPED
- [ ] ISC-21: TodoManager.validate() returns True for valid file
- [ ] ISC-22: TodoManager.migrate_to_three_columns() returns count of changed lines
- [ ] ISC-23: tasks.py handlers (all 4) callable with real keyword args
- [ ] ISC-24: documentation.py assess_readme_quality/assess_agents_quality/assess_technical_accuracy return int 0-100

## Decisions

- Target file: src/codomyrmex/tests/unit/agents/test_droid_full.py (new file, does not overlap test_run_todo_droid.py)
- DroidController tests use create_default_controller() helper
- from_env tests: set os.environ keys directly, clean up in finally
- Generators tests: call pure scoring functions with synthetic content strings (no file I/O)
- save_config_to_file / load_config_from_file: use tmp_path for real file I/O

## Verification

