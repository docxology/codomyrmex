# AGENTS.md — `codomyrmex/evaluations/cli`

## Purpose

JSON evaluation records for CLI scripts (basic usage, CLI utils, orchestrate)
plus roll-up report. Each record is Hermes's thin-orchestrator verdict for one
script under `scripts/cli/`.

## Key Files

- `cli_utils_eval.json` — `scripts/cli/cli_utils.py` (STRICT ADHERENCE).
- `orchestrate_eval.json` — `scripts/cli/orchestrate.py` (STRICT ADHERENCE).
- `basic_usage_eval.json` — `scripts/cli/examples/basic_usage.py`
  (NON-COMPLIANT: hardcoded config path and display logic kept in the script).
- [`overall_evaluation_report.md`](overall_evaluation_report.md) — rollup for
  all three scripts, generated 2026-03-11.
- [`README.md`](README.md) — human signpost.

## Dependencies

- Written by [`evaluate_orchestrators.py`](../../scripts/agents/hermes/evaluate_orchestrators.py)
  `--target cli`; the `target_overrides.cli` block in
  [`config/agents/hermes.yaml`](../../config/agents/hermes.yaml) sets
  `output_dir: evaluations/cli`, executes every script, and injects
  `CODOMYRMEX_TEST_MODE=1`.
- Evaluated sources: [`scripts/cli/`](../../scripts/cli/README.md).
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Generated artifacts — regenerate, don't hand-edit.
- Regenerate with `uv run python scripts/agents/hermes/evaluate_orchestrators.py --target cli`.
- Verdicts are dated; check the current script source before citing one.
