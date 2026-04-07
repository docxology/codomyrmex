# RASP audit progress (AGENTS.md / README.md)

Tracks the repo-wide documentation audit. Gap report: [agents-readme-gap-report.md](agents-readme-gap-report.md).

| Wave | Scope | Status |
| --- | --- | --- |
| Gap scan | `scripts/rasp_gap_report.py` + report | Done |
| `.github` | Workflow count + AGENTS alignment | Done (see commit) |
| Inventory | `doc_inventory.py` workflow metric | Done |
| A | `src/codomyrmex/` nested `.github` dirs from gap report | Done |
| B | `docs/`, `projects/` | No gaps after exclusions (ephemeral dirs excluded) |
| C | `scripts/`, `config/` | No gaps after exclusions |
| Verify | `uv run pytest --collect-only`, `test_doc_inventory_metrics.py`, `ruff` | Done |

**Ephemeral paths excluded from gap scan** (not RASP targets): `.benchmarks/`, `scripts/output/`, `scripts/agents/hermes/output/`, `scripts/sair/output/`.

**Wave B/C**: Under current exclusion rules, `docs/`, `projects/`, `scripts/`, `config/`, `.github/` report zero gaps; no new README/AGENTS required beyond nested `src/` fixes above.

**Wave A**: Eight nested `.github` directories under `src/codomyrmex/` now have `AGENTS.md` and `README.md`.
