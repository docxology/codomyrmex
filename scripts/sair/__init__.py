"""
SAIR Mathematics Distillation Challenge — `scripts/sair` package.

Thin-orchestrator scripts for the SAIR competition:

    run_sair.py          Unified entry point (evaluate/generate/analyze/full/compare)
    download_data.py     HuggingFace dataset download + integrity verification
    evaluate.py          Local evaluation engine (Jinja2 template, LLM providers, telemetry)
    generate_cheatsheet.py  Cheatsheet builder + iterative refinement from run results
    analyze_results.py   Post-hoc performance analysis (latency percentiles, trends)
    utils.py             Shared utilities (I/O, hashing, summarization, run comparison)

All outputs are persisted:
    data/public/         Public datasets downloaded from HuggingFace
    output/runs/         Per-run JSON (problem-level detail + summary)
    output/logs/         Appended NDJSON telemetry line per run
    output/cheatsheets/  Generated cheatsheet text files
    output/visualizations/ Matplotlib analysis charts

Quick start:
    python scripts/sair/run_sair.py full --limit 20 --model gemini-2.5-flash

See SPEC.md for full API surface and telemetry schema.
See AGENTS.md for operational contracts.
"""

from .utils import (
    compute_hash,
    compare_runs,
    ensure_dir,
    format_timestamp,
    load_json,
    load_jsonl,
    load_run_history,
    save_json,
    save_jsonl,
    summarize_results,
)

__version__ = "0.2.0"

__all__ = [
    "compute_hash",
    "compare_runs",
    "ensure_dir",
    "format_timestamp",
    "load_json",
    "load_jsonl",
    "load_run_history",
    "save_json",
    "save_jsonl",
    "summarize_results",
]
