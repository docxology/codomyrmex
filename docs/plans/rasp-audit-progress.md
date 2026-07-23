# RASP audit progress (AGENTS.md / README.md)

Tracks the repo-wide documentation audit. Gap report: [agents-readme-gap-report.md](agents-readme-gap-report.md).

Measured on 2026-07-22 with `uv run python scripts/rasp_gap_report.py`: **0
gaps across the six configured roots**. This is a structural signpost result,
not a claim that every document is semantically complete; `make docs-check`
remains the content/link quality gate.

| Wave | Scope | Status |
| --- | --- | --- |
| Gap scan | `scripts/rasp_gap_report.py` + report | Done — 0 gaps on 2026-07-22 |
| `.github` | Workflow count + AGENTS alignment | Done (see commit) |
| Inventory | `doc_inventory.py` workflow metric | Done |
| A | `src/codomyrmex/` nested `.github` dirs from gap report | Done |
| B | `docs/`, `projects/` | Done — no gaps after asset/generated exclusions |
| C | `scripts/`, `config/` | Done — no gaps after output/embedded exclusions |
| Verify | `uv run pytest --collect-only`, `test_doc_inventory_metrics.py`, `ruff` | Done |

**Excluded from the gap scan** (not first-party documentation targets):
`.benchmarks/`, `scripts/output/`, `scripts/agents/hermes/output/`,
`scripts/sair/output/`, the embedded `src/codomyrmex/agents/hermes/evolution/`
checkout, generated documentation under `src/codomyrmex/documentation/docs/`,
upstream/custom skill trees, empty LLM output directories, the skills cache,
and the image-only `docs/assets/demo_stills/` tree. The exact list is kept in
`scripts/rasp_gap_report.py` and is intentionally narrower than a blanket
vendor exclusion.

**Wave B/C**: Under current exclusion rules, `docs/`, `projects/`, `scripts/`,
`config/`, and `.github/` report zero gaps. Real first-party gaps in the
embodiment subpackages, module documentation signposts, and memory probe were
documented rather than excluded.

**Wave A**: Eight nested `.github` directories under `src/codomyrmex/` now have `AGENTS.md` and `README.md`.
