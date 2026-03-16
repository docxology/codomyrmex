# SAIR Mathematics Distillation Challenge — Script Specification

**Module**: `scripts/sair` | **Version**: v0.2.0 | **Status**: Active

## Overview

This module provides production-grade infrastructure for the SAIR Mathematics Distillation Challenge
(Stage 1 & 2: Equational Theories). It enables:
- Local replication of the official evaluation playground ([playground.sair.foundation](https://playground.sair.foundation/playground/mathematics-distillation-challenge-equational-theories-stage1))
- Iterative cheat sheet optimization via performance analytics
- Complete run telemetry and structured logging
- Stage 2 Log-Loss scoring configuration Support (`--stage2`)

**Submission Deadline**: April 20, 2026.

## Evaluation Template (Official Jinja2)

```jinja2
You are a mathematician specializing in equational theories of magmas.
Your task is to determine whether Equation 1 ({{ equation1 }}) implies Equation 2 ({{ equation2 }}) over all magmas.
{% if cheatsheet is defined and cheatsheet %}
{{ cheatsheet }}
{% endif %}
Output format (use exact headers without any additional text or formatting):
VERDICT: must be exactly TRUE or FALSE (in the same line).
REASONING: must be non-empty.
PROOF: required if VERDICT is TRUE, empty otherwise.
COUNTEREXAMPLE: required if VERDICT is FALSE, empty otherwise.
```

If `--stage2` is passed, the template injects an additional instruction:
`CONFIDENCE: a probability between 0.0 and 1.0 that VERDICT is TRUE (for log-loss scoring).`

## Output Parsing Rules

LLM output is parsed by header:
- `VERDICT:` — must be exactly `TRUE` or `FALSE` (in the same line)
- `REASONING:` — must be non-empty
- `PROOF:` — required if VERDICT is TRUE
- `COUNTEREXAMPLE:` — required if VERDICT is FALSE

Ground-truth field from SAIR dataset: `answer` (str: `"TRUE"` or `"FALSE"`).
Fallback fields: `expected_verdict`, `is_true` for compatibility.

## Telemetry & Run Log Schema

Every evaluation run produces:

### Auto-saved run: `output/runs/run_<TIMESTAMP>_<run_id>.json`

```json
{
  "summary": {
    "run_id": "str (8-char UUID fragment)",
    "correlation_id": "str (cid-...)",
    "model": "str",
    "dataset": "str (path)",
    "cheatsheet_path": "str | null",
    "cheatsheet_hash": "str (12-char SHA-256) | null",
    "timestamp_start": "ISO‑8601 UTC",
    "timestamp_end": "ISO‑8601 UTC",
    "wall_time_sec": "float",
    "accuracy": "float (0–1)",
    "correct": "int",
    "evaluated": "int",
    "errors": "int",
    "true_accuracy": "float | null",
    "false_accuracy": "float | null",
    "avg_latency_sec": "float",
    "avg_log_loss": "float | null (Stage 2 only)",
    "total_tokens": "int",
    "missed_problems": ["str"]
  },
  "results": [
    {
      "problem_id": "str",
      "equation1": "str",
      "equation2": "str",
      "ground_truth": "TRUE | FALSE | null",
      "verdict": "TRUE | FALSE | UNKNOWN",
      "confidence": "float | null (Stage 2 only)",
      "is_correct": "bool | null",
      "log_loss": "float | null (Stage 2 only)",
      "parsed": {"VERDICT": "", "CONFIDENCE": "", "REASONING": "", "PROOF": "", "COUNTEREXAMPLE": ""},
      "raw_response": "str",
      "latency": "float (seconds)",
      "memory_delta_mb": "float",
      "usage": {"total_tokens": "int"},
      "model": "str",
      "cheatsheet_hash": "str | null",
      "timestamp": "ISO‑8601 UTC",
      "attempts": "int"
    }
  ]
}
```

### Appended telemetry log: `output/logs/telemetry.ndjson`

One NDJSON line per run containing summary-level metrics for trend analysis.

## Iterative Refinement Loop

1. `run_sair.py evaluate` → auto-saves `output/runs/run_<ts>_<id>.json`
2. `run_sair.py generate --refine-from <run_file>` → analyses failures, activates targeted strategies
3. Repeat with refined cheatsheet, compare runs with `run_sair.py compare`

## API Surface

### `evaluate.py`
- `parse_llm_response(text) -> dict` — Parse VERDICT/REASONING/PROOF/COUNTEREXAMPLE
- `evaluate_problem(provider, model, problem, cheatsheet, cheatsheet_hash) -> dict`
- `run_evaluation(dataset_path, model, ...) -> dict` — Full batch with auto-save & telemetry

### `generate_cheatsheet.py`

- `build_cheatsheet(techniques, rules, bundles, additional_context) -> str`
- `validate_size(content) -> bool` — 10KB check
- `trim_to_budget(content) -> str` — Safe truncation
- `save_cheatsheet(content, filepath) -> dict` — Returns metadata
- `refine_from_results(results_file, ...) -> str` — Iterative refinement

### `utils.py`

- `load_jsonl(path) / save_jsonl(data, path)` — JSONL I/O
- `load_json(path) / save_json(data, path)` — JSON I/O
- `compute_hash(content) -> str` — 12-char SHA-256 fingerprint
- `summarize_results(results) -> dict` — Rich accuracy/latency/token summary
- `compare_runs(run_a, run_b) -> dict` — Delta between two runs
- `load_run_history(run_dir) -> list` — Load all run JSONs
- `format_timestamp() -> str` — Filesystem-safe ISO timestamp

### `download_data.py`

- `download_sair_datasets(output_dir)` — HuggingFace download + integrity check
- `verify_dataset_integrity(path) -> bool` — JSONL validation
- `list_local_datasets(data_dir) -> dict` — Local dataset registry

### `analyze_results.py`

- `analyze_run(run_data, verbose) -> str` — Rich report with BenchmarkResult latency percentiles and generated visualizations payload.
- `analyze_trend(runs) -> str` — Multi-run trend table and accuracy/latency plot.
- `compare_two_runs(path_a, path_b) -> str` — Side-by-side comparison

### `run_sair.py` — Unified Orchestrator

Modes: `evaluate`, `generate`, `refine`, `analyze`, `full`, `compare`

## Cheatsheet Constraint

The cheatsheet must be **≤ 10,240 bytes** (10KB UTF-8). The `save_cheatsheet` function will auto-trim to budget.

## Dependencies

- `jinja2` — Template rendering
- `huggingface_hub` — Dataset download
- `requests` — HTTP (ETP graph download)
- `codomyrmex.llm` — Provider abstraction (Gemini, OpenRouter)
- `codomyrmex.logging_monitoring` — Structured logging + correlation IDs
- `codomyrmex.performance` — `BenchmarkResult`, `profile_function`

## Signposting

- **Parent**: [scripts/README.md](../README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **PAI Bridge**: [PAI.md](PAI.md)
