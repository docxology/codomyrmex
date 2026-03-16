# SAIR Mathematics Distillation

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Infrastructure for the [SAIR Mathematics Distillation Challenge (Stage 1)](https://competition.sair.foundation/competitions/mathematics-distillation-challenge-equational-theories-stage1/overview).
**Deadline**: April 20, 2026.

Distill universal algebra knowledge from the Equational Theories Project into a ≤10KB "cheat sheet" injected into each LLM prompt at evaluation time.
Official competition playground for testing: [playground.sair.foundation](https://playground.sair.foundation/playground/mathematics-distillation-challenge-equational-theories-stage1)

## Architecture vs Competition Format

- **Stage 1**: Goal is raw accuracy on TRUE/FALSE implications. The cheatsheet is injected as *user content*.
- **Stage 2**: (Top 1000) Requires log-loss scoring (Confidence interval) + structural Proofs/Counterexamples natively. Supported here via the `--stage2` flag.

## Directory Contents

| Script | Purpose |
| :--- | :--- |
| `run_sair.py` | **Unified orchestrator** — `evaluate`, `generate`, `analyze`, `full`, `compare` |
| `evaluate.py` | Local evaluation engine (Jinja2 template, retries, full telemetry) |
| `generate_cheatsheet.py` | Build and iteratively refine cheatsheets from run results |
| `analyze_results.py` | Post-hoc analysis: accuracy, latency percentiles, trend table |
| `download_data.py` | HuggingFace download + JSONL integrity verification |
| `utils.py` | Shared I/O, hashing, summarization, run history & comparison |

## Saved Outputs

| Path | Content |
| :--- | :--- |
| `data/` | Root for public and ETP datasets |
| `output/runs/*.json` | Per-run JSON with full problem-level detail and summary |
| `output/logs/telemetry.ndjson` | Appended NDJSON line per run (model, accuracy, tokens, latency) |
| `output/cheatsheets/*.txt` | Generated cheatsheet text files (≤10KB enforced) |
| `output/visualizations/*.png` | **[NEW]** Matplotlib analysis charts (latency distributions, trends) |

## Quick Start

```bash
# 1. Download competition data
python scripts/sair/run_sair.py evaluate --type list   # see what's cached
python scripts/sair/download_data.py --type public

# 2. Generate baseline cheatsheet
python scripts/sair/run_sair.py generate --bundle baseline structural \
  --output scripts/sair/output/cheatsheets/v1.txt

# 3. Evaluate (auto-saves run + telemetry)
python scripts/sair/run_sair.py evaluate \
  --dataset scripts/sair/data/public/data/normal.jsonl \
  --cheatsheet scripts/sair/output/cheatsheets/v1.txt --limit 20

# 4. Analyze results
python scripts/sair/run_sair.py analyze --run-dir scripts/sair/output/runs/

# 5. Refine cheatsheet from run failures
python scripts/sair/run_sair.py generate \
  --refine-from scripts/sair/output/runs/run_<id>.json \
  --output scripts/sair/output/cheatsheets/v2.txt

# 6. Full pipeline in one command
python scripts/sair/run_sair.py full --limit 20 --model gemini-2.5-flash

# 7. Compare two runs
python scripts/sair/run_sair.py compare scripts/sair/output/runs/run_A.json scripts/sair/output/runs/run_B.json

# 8. Stage 2 (Log-loss Confidence Scoring)
python scripts/sair/run_sair.py evaluate \
  --dataset scripts/sair/data/public/data/hard.jsonl \
  --model gemini-2.5-flash --stage2
```

## Navigation

- **Parent**: [scripts/README.md](../README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **Agent Coordination**: [AGENTS.md](AGENTS.md)
- **PAI Bridge**: [PAI.md](PAI.md)
- **Tests**: [tests/scripts/sair/](../../src/codomyrmex/tests/scripts/sair/)
