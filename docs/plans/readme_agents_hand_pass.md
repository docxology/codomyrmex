# README / AGENTS hand-pass tracker

**Status:** Active freeze; package-wide integrity audited, bounded hub review in
progress. **Last measured:** August 30, 2026.

## 2026-08-30 fleet-pass stub resolution

The 2026-08-30 fleet pass left 198 placeholder stubs
(`SKELETON (auto-generated 2026-08-30)`). All 198 have been replaced with
content derived from on-disk reality:

- 130 module `README.md` files under
  `src/codomyrmex/documentation/docs/modules/<module>/` — generated from each
  module's `__init__.py` docstring, `__all__` exports, and submodule inventory;
  SPEC links omitted where no `SPEC.md` exists in the bundle. Marked
  `<!-- readme: generated -->`.
- 68 hand-verified docs across `.agent/`, `.agents/`, `.cursor/skills/`,
  runtime-config dirs, `.devcontainer/`, `.jules/`,
  `.pipelines/`, `data/sair/`, `docs/assets/demo_stills/`, `evaluations/`,
  `tests/` subdirs, and 3 module `AGENTS.md` files (config_audits,
  config_monitoring, manuscript).
- Post-pass strict audit: 1,557 directories / 3,114 files, **0 errors,
  0 warnings** (receipt: `output/readme_agents_audit.json`, 2026-08-30).

## Current receipt

The read-only package audit currently covers the repository root, six RASP
roots, and test directories that already carry at least one README/AGENTS pair.

| Measure | Current result |
| :--- | ---: |
| Governed directories | 1,550 |
| README files | 1,550 |
| AGENTS files | 1,550 |
| Blocking errors | 0 |
| Non-blocking generated-punctuation warnings | 916 |
| Files matching generic-boilerplate inventory signals | 2,006 |
| Files carrying a legacy `v0.1.0` label | 2,625 |
| Files under 15 lines | 25 |
| Curated-marker files | 153 |

Receipt:
`output/readme_agents_audit.json` and
`output/readme_agents_audit.md`.

The metrics overlap. A generic signpost or old label is not automatically a
false behavioral claim, but it identifies a candidate for human review.
Blocking validation covers missing pair members, headings, relative links,
documented Python entry points, and repository-local skill references.

The narrower RASP scan reports zero gaps across `src/codomyrmex/`, `docs/`,
`projects/`, `scripts/`, `config/`, and `.github/`.

## Freeze policy

- Do not run broad bootstrap, module enrichment, placeholder repair, or
  missing-file generators in apply mode.
- Use dry-run and audit receipts for discovery, then make bounded hand edits.
- Preserve all concurrent dirty-worktree content and submodule state.
- Put `<!-- agents: curated -->` or `<!-- readme: curated -->` near the start of
  reviewed files so supported generators preserve them.
- Do not label thousands of files curated merely to silence an inventory
  metric; a marker means the content was actually reviewed.
- Re-run the package audit and strict documentation gate after every batch.

## Commands

```bash
# Presence only; no report write
uv run --locked python scripts/rasp_gap_report.py --repo-root . --check

# Package-wide pair, link, command, and skill audit
uv run --locked python scripts/documentation/audit_readme_agents.py \
  --repo-root . --strict

# Preview one module mirror
uv run --locked python scripts/documentation/enrich_module_docs.py \
  --repo-root . --dry-run --module <module>

# Authoritative composed validation
make docs-check
```

The module enricher requires explicit `--apply`. Existing unmarked files also
require the corresponding `--force-readmes`, `--force-agents`, or
`--force-specs` flag. Curated README/AGENTS files remain protected under force.

## Completed in the current batch

- Added package-wide README/AGENTS auditing with portable receipts and
  zero-mock regression tests.
- Restored README/AGENTS parity for `tests/unit/colony_kernel/`.
- Corrected broken repository, source-module, and test navigation links.
- Corrected stale documented Python entry points and added a bounded local qmd
  skill with an `rg` fallback.
- Replaced obsolete OpenGauss wrapper documentation with the actual Git
  submodule, installer, and console-entry-point boundary.
- Made module enrichment and placeholder repair fail closed.
- Hardened RASP `--help` and added a read-only `--check` mode.
- Curated the central documentation-package and tooling README/AGENTS hubs.
- Replaced the Git core leaf inventories of transient metadata backups with
  reviewed runtime-state, packaging, and test-isolation contracts.
- Added the pair and command/link audits to Makefile and justfile parity.

## Remaining hand-pass debt

The 916 duplicated periods are a known artifact of an older generic-placeholder
repair. The producer is fixed, but changing roughly nine hundred otherwise
clean leaf files would violate the active bounded-edit policy. Retire this debt
in reviewed batches after the freeze decision, not through an unreviewed global
replacement.

Prioritize:

1. high-traffic root, `src/`, `docs/`, `scripts/`, and `tests/` hubs;
2. modules whose runtime or public interface changed without documentation;
3. the 25 thin files;
4. generic leaf pairs, grouped by owning module;
5. legacy version labels that imply an incorrect behavioral version.

For each batch, record the paths reviewed, why prose changed, validation
results, and whether the source/API/MCP/PAI/security/changelog surfaces remain
aligned.

## Historical batch record

An earlier broad bootstrap wrote thousands of files and then applied curated
markers widely. Those counts are historical evidence, not instructions to
repeat the operation. Repository root files remain hand-maintained, and
`docs/modules/<package>/` mirrors are outside bootstrap ownership when a
matching `src/codomyrmex/<package>/` exists.

## Navigation

- [Documentation maintenance guide](../development/documentation.md)
- [Generated RASP gap report](agents-readme-gap-report.md)
- [Repository agent contract](../../AGENTS.md)
