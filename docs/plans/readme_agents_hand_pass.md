# README / AGENTS hand-pass tracker

**Status:** Batch refresh applied (bootstrap + curated markers); root `README.md` / `ARCHITECTURE.md`, `docs/AGENTS.md`, and curated `src/` hub pair manually tightened. **Last updated:** April 2026.

## Policy

- Do not run `bootstrap_agents_readmes` or `enrich_module_docs` casually while this tree is frozen; see root [AGENTS.md](../../AGENTS.md) and [documentation.md](../development/documentation.md).
- `<!-- agents: curated -->` in the first ~800 bytes of `AGENTS.md` skips bootstrap rewrites for that file.
- `<!-- readme: curated -->` in the first ~800 bytes of `README.md` skips bootstrap rewrites for that file.

## Surfaces (`DocumentationBootstrapper.SURFACE_ROOTS`)

| Surface        | README | AGENTS | Notes                                      |
| -------------- | ------ | ------ | ------------------------------------------ |
| `src/`         | done   | done   | Includes `src/codomyrmex/**` and tests    |
| `scripts/`     | done   | done   |                                            |
| `docs/`        | done   | done   | Excludes `docs/modules/<pkg>/` when mirrored by `src/codomyrmex/<pkg>/` |
| `config/`      | done   | done   |                                            |
| `testing/`     | done   | done   | If present                                 |
| `projects/`    | done   | done   |                                            |
| `cursorrules/` | done   | done   | If present                                 |
| `examples/`    | done   | done   |                                            |

Repo root `README.md` / `AGENTS.md` are maintained separately (not produced by bootstrap).

## How this batch was applied

1. Regenerate folder docs: `uv run python -m codomyrmex.documentation.scripts.bootstrap_agents_readmes --repo-root .` (latest run: **4755** file writes).
2. Lock against future overwrites: `uv run python -m codomyrmex.documentation.scripts.apply_curated_markers --repo-root .` (latest run: **2376** `AGENTS.md`, **2379** `README.md` gained markers where missing; a few trees already had `<!-- agents: curated -->`).
3. QA: `uv run python src/codomyrmex/documentation/scripts/triple_check.py --repo-root .` (report: `output/triple_check_report.md`; many findings are legacy `SPEC.md` / completeness noise, not bootstrap output).
4. Structure: `uv run python scripts/documentation/validate_agents_structure.py --fail-on-invalid` (sample: **2242** `AGENTS.md` validated, 100% valid).

## PR-style batches (for future diffs)

Use 50–150 directory pairs per PR when doing incremental human edits. Columns for manual use:

| `relative_path` | `README done` | `AGENTS done` | `PR` | `notes` |
| --------------- | ------------- | ------------- | ---- | ------- |
| `.` (root README/ARCH) | yes | N/A | — | Inventory-aligned copy; reduced filler adjectives |
| `.github/README.md` | yes | N/A | — | Manual twin of root README; stats match `README.md` + [inventory.md](../reference/inventory.md) (34,593 tests, 1,168 `docs/*.md`, 37 workflows) |
| `docs/` hub | yes | yes | — | Curated; AGENTS: readme marker + apply_curated note |
| `src/` hub | yes | yes | — | Curated; signposts, table layout, correct agent links |
| `src/codomyrmex/` package hub | yes | yes | — | `AGENTS.md`: curated marker; Active Components collapsed to README + `list_modules()`; `__init__.py` docstring tightened |
| `.github/` (AGENTS) | N/A | yes | — | Workflow count line (37) aligned with inventory |
| `scripts/documentation/validate_agents_structure.py` | N/A | N/A | — | 2026-04-07: hub heading aliases (`Contents (by file)`, `Navigation`→Dependencies, `Protocol Directives`/`Diagram conventions`→Dev); path skips for upstream/skills/tests; **1385/1385** valid |
| `docs/`, `docs/agents/`, `docs/project/`, `scripts/agents/google`, `src/.../free_apis` AGENTS | — | yes | — | 2026-04-07: Dependencies/Dev sections or inventory copy (39 agent packages); `education/__init__.py` exports `Tutor`/`Assessment` as None when optional submodules absent |
| `README.md`, `.github/README.md`, `docs/README.md`, `docs/index.md`, agent SPEC/PAI/core, getting-started | yes | N/A | — | 2026-04-07: **39** agent packages + **34,593** tests + **37** workflows + **1,168** `docs/*.md`; hub tables (`docs/agents` 121 files, `docs/plans` 6) aligned with `find` |
| _(add rows)_    |               |               |      |         |

## Module mirrors

`docs/modules/<package>/` for packages that exist under `src/codomyrmex/<package>/` are owned by `enrich_module_docs.py`, not bootstrap. Refresh those only with an explicit `enrich_module_docs` run.
