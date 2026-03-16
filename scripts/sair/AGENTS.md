# SAIR Submodule — Agent Coordination

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

This AGENTS.md coordinates AI agent operations within `scripts/sair/` — the SAIR Mathematics
Distillation Challenge infrastructure. It documents the module's operational contracts, active
components, and integration points with the broader Codomyrmex ecosystem.

## Active Components

| Script | Role | Integration |
| :--- | :--- | :--- |
| `run_sair.py` | Unified orchestrator (evaluate/generate/analyze/full/compare) | All others |
| `evaluate.py` | LLM evaluation engine with telemetry & auto-save | `codomyrmex.llm`, `codomyrmex.performance`, `codomyrmex.logging_monitoring` |
| `generate_cheatsheet.py` | Cheatsheet assembly + iterative refinement | `utils.py` |
| `analyze_results.py` | Post-hoc performance analysis (BenchmarkResult) | `codomyrmex.performance` |
| `download_data.py` | HuggingFace dataset download + integrity verification | `codomyrmex.logging_monitoring` |
| `utils.py` | Shared I/O, hashing, summarization, run-history helpers | — |

## Operating Contracts

1. **Zero-Mock Policy**: All tests use real components (real JSONL data, real SAIR API structures).
2. **Persistent Telemetry**: Every evaluation run auto-saves to `output/runs/` and appends to `output/logs/telemetry.ndjson`.
3. **Size Enforcement**: Cheatsheets must be ≤10,240 bytes; `save_cheatsheet` auto-trims to budget.
4. **Structured Logging**: All log calls use `codomyrmex.logging_monitoring.get_logger()` with correlation IDs.
5. **Modular Orchestration**: Use `run_sair.py` as the primary entry point; avoid calling sub-scripts directly.

## Key Files

- `run_sair.py` — Primary entry point for all operations
- `evaluate.py` — Evaluation engine (Jinja2 template, retries, profiling)
- `generate_cheatsheet.py` — Cheatsheet builder with iterative refinement
- `analyze_results.py` — Post-hoc analysis with latency percentiles
- `download_data.py` — Data acquisition and validation
- `utils.py` — Shared utilities
- `SPEC.md` — Full technical specification
- `PAI.md` — PAI bridge documentation

## Dependencies

- `codomyrmex.llm` — Provider abstraction (Gemini 2.5 Flash, OpenRouter)
- `codomyrmex.logging_monitoring` — Logging with correlation IDs
- `codomyrmex.performance` — `profile_function`, `BenchmarkResult`
- `jinja2`, `huggingface_hub`, `requests`

## Signposting

- **Parent**: [scripts/AGENTS.md](../AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
- **PAI Bridge**: [PAI.md](PAI.md)
- **Tests**: [tests/scripts/sair/](../../src/codomyrmex/tests/scripts/sair/)
