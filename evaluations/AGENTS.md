# AGENTS.md — `codomyrmex/evaluations`

## Purpose

Stored evaluation runs of the agent-script orchestration surfaces
(`scripts/agents/hermes` dispatch/observe/run/setup, API and CLI scripts, and a
Gemini dispatch demo). Hermes grades each script against the "thin
orchestrator" pattern; each folder holds per-script JSON eval records plus an
`overall_evaluation_report.md` rollup.

## Key Files

- [`api/`](api/AGENTS.md) — evaluations of `scripts/api` (orchestrate, webhooks,
  pagination, circuit breaker, …).
- [`cli/`](cli/AGENTS.md) — evaluations of `scripts/cli` (basic usage, utils, orchestrate).
- [`gemini/`](gemini/AGENTS.md) — evaluations of the `scripts/agents/gemini` demos.
- `dispatch_hermes_eval.json`, `evaluate_orchestrators_eval.json`,
  `observe_hermes_eval.json`, `prompt_context_eval.json`, `run_hermes_eval.json`,
  `setup_hermes_eval.json` — `scripts/agents/hermes` evaluations; each has
  `adherence_assessment` (`adheres`, `reasoning`), `technical_debt`, and
  `underlying_improvements`.
- [`overall_evaluation_report.md`](overall_evaluation_report.md) — rollup
  generated 2026-03-12: 2 of 6 scripts STRICT ADHERENCE, 4 NON-COMPLIANT
  (mostly legacy `Optional[...]` typing).
- [`README.md`](README.md) — human signpost.

## Dependencies

- Written by [`scripts/agents/hermes/evaluate_orchestrators.py`](../scripts/agents/hermes/evaluate_orchestrators.py)
  (`--target <dir under scripts/>`); the output folder and run environment per
  target come from `evaluator` and `target_overrides` in
  [`config/agents/hermes.yaml`](../config/agents/hermes.yaml).
- Read by [`scripts/agents/hermes/dispatch_hermes.py`](../scripts/agents/hermes/dispatch_hermes.py)
  (`--eval-dir`, default `evaluations`), which turns NON-COMPLIANT verdicts into
  Hermes improvement dispatches.
- Parent: [../README.md](../README.md) · Root contract: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- These are generated evaluation artifacts with a point-in-time verdict —
  re-run the evaluator rather than editing scores; keep the generated date in
  mind when citing compliance.
- The 2026-03-12 report marks several scripts NON-COMPLIANT (legacy
  `Optional[...]` typing); check the current source before treating any verdict
  as current.
- The rollup is rewritten on every run from that run's assessments only, while
  per-script JSONs persist until overwritten; a `--dry-run` or a run with no
  successful assessments leaves a header-only report.
- JSON names are `<script stem>_eval.json`, so same-named scripts in different
  subfolders of one target overwrite each other.
- Regenerate with, for example:

  ```bash
  uv run python scripts/agents/hermes/evaluate_orchestrators.py --target agents/hermes
  ```
