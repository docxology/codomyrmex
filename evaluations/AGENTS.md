# AGENTS.md — `codomyrmex/evaluations`

## Purpose
Stored evaluation runs of the agent-script orchestration surfaces
(`scripts/agents/hermes` dispatch/observe/run/setup, API and CLI scripts, and a
Gemini dispatch demo). Each subfolder holds per-script JSON eval records plus an
`overall_evaluation_report.md` rollup.

## Layout
- `api/` — evaluations of `api` module scripts (orchestrate, webhooks, pagination, circuit breaker, …).
- `cli/` — evaluations of CLI scripts (basic usage, utils, orchestrate).
- `gemini/` — Gemini dispatch demo evaluations.
- Top-level `*_eval.json` — hermes orchestration script evaluations (dispatch/observe/run/setup/prompt-context).
- `overall_evaluation_report.md` — evaluator-orchestrations report (2026-03-12), flags legacy-typing violations.

## Gotchas
- These are generated evaluation artifacts with a point-in-time verdict —
  re-run the evaluator rather than editing scores; keep the generated date in mind when citing compliance.
- The 2026-03-12 report marks several scripts NON-COMPLIANT (legacy `Optional[...]` typing); check git history before treating any verdict as current.

## Key Files
- `README.md`: Readme file

## Dependencies
- None

## Development Guidelines
- Follow standard practices
