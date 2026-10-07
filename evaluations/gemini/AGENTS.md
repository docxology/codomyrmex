# AGENTS.md — `codomyrmex/evaluations/gemini`

## Purpose

Evaluation records for the Gemini dispatch demo (`demo_gemini_dispatch_eval.json`,
`gemini_example_eval.json`) and a roll-up report. Each record is Hermes's
thin-orchestrator verdict for one script under `scripts/agents/gemini/`.

## Key Files

- `demo_gemini_dispatch_eval.json` — `scripts/agents/gemini/demo_gemini_dispatch.py`
  (NON-COMPLIANT: test-mode handling and result printing kept in the script).
- `gemini_example_eval.json` — `scripts/agents/gemini/gemini_example.py`
  (NON-COMPLIANT: inline configuration and API-key handling, exit code 1 at
  evaluation time).
- [`overall_evaluation_report.md`](overall_evaluation_report.md) — rollup for
  both scripts, generated 2026-03-11.
- [`README.md`](README.md) — human signpost.

## Dependencies

- Written by [`evaluate_orchestrators.py`](../../scripts/agents/hermes/evaluate_orchestrators.py)
  `--target agents/gemini`; the `target_overrides` entry for `agents/gemini` in
  [`config/agents/hermes.yaml`](../../config/agents/hermes.yaml) sets
  `output_dir: evaluations/gemini`, executes both scripts, and injects
  `CODOMYRMEX_TEST_MODE=1` so no live Gemini call is made.
- Evaluated sources: [`scripts/agents/gemini/`](../../scripts/agents/gemini/README.md).
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Generated artifacts — regenerate via the evaluation harness.
- Regenerate with `uv run python scripts/agents/hermes/evaluate_orchestrators.py --target agents/gemini`.
- Never put a real `GEMINI_API_KEY` into `--run-env` or `hermes.yaml`; the
  evaluation relies on test mode, and each script's stdout/stderr is sent to
  Hermes and can be quoted in these records.
