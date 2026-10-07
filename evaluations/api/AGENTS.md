# AGENTS.md — `codomyrmex/evaluations/api`

## Purpose

JSON evaluation records for the `api` module scripts (orchestrate, basic usage,
api_tester, advanced workflow, webhooks, pagination, circuit breaker, mocking
demo) plus a roll-up report. Each record is Hermes's thin-orchestrator verdict
for one script under `scripts/api/`.

## Key Files

- `orchestrate_eval.json` — `scripts/api/orchestrate.py`.
- `api_tester_eval.json` — `scripts/api/api_tester.py`; records a Hermes parse
  failure (`Malformed response from Hermes`), not a real assessment.
- `basic_usage_eval.json`, `advanced_workflow_eval.json` — `scripts/api/examples/`.
- `webhooks_demo_eval.json`, `pagination_demo_eval.json`,
  `circuit_breaker_demo_eval.json`, `mocking_demo_eval.json` — the demos in
  `scripts/api/{webhooks,pagination,circuit_breaker,mocking}/`.
- [`overall_evaluation_report.md`](overall_evaluation_report.md) — header-only
  rollup (generated 2026-03-11): the last run produced no assessments, so the
  per-script JSONs are the only verdicts here.
- [`README.md`](README.md) — human signpost.

## Dependencies

- Written by [`evaluate_orchestrators.py`](../../scripts/agents/hermes/evaluate_orchestrators.py)
  `--target api`; the `target_overrides.api` block in
  [`config/agents/hermes.yaml`](../../config/agents/hermes.yaml) sets
  `output_dir: evaluations/api`, executes every script, and injects
  `CODOMYRMEX_TEST_MODE=1`.
- Evaluated sources: [`scripts/api/`](../../scripts/api/README.md).
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Generated artifacts: regenerate via the evaluation harness instead of editing.
- Regenerate with `uv run python scripts/agents/hermes/evaluate_orchestrators.py --target api`.
- Treat `adheres: false` together with `Malformed response from Hermes` as a
  failed run, not a compliance finding; re-run before dispatching fixes for
  `api_tester.py`.
- A successful re-run rewrites the rollup and the JSONs it assesses; JSONs for
  scripts it skips remain from earlier runs.
