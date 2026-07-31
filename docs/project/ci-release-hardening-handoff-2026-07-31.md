# CI and Release Hardening Handoff

**Date**: 2026-07-31
**Repository**: `docxology/codomyrmex`
**Baseline**: `909213733` (`main`)
**Status**: Published baseline; ready for the next review and extension pass

## Purpose

This handoff records the reproducibility, test-environment, release-verification,
and workflow hardening completed in the previous pass. It is the starting point
for the next agent or maintainer. The source of truth is always the current
`main` and `origin/main`, not a copied commit hash in this document.

## Completed work

| Area | Completed change | Primary locations |
| --- | --- | --- |
| Locked environments | CI and contributor test paths use the committed lock; test jobs explicitly include the `docs` group required by MkDocs-hook tests. | `.github/workflows/`, `Makefile`, `justfile`, `README.md`, `tests/RUNNING_TESTS.md` |
| Pre-commit contract | `pre-commit` is declared in the `dev` dependency group and locked; CI uses the declared package instead of installing it ad hoc. | `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml`, `.github/workflows/pre-commit.yml` |
| Release verification | Published-package checks use an explicit UV-created virtual environment for each Python version. | `.github/workflows/release.yml` |
| Release documentation | Stable releases create a reviewable documentation-update PR with job-scoped write permission. | `.github/workflows/release.yml` |
| Workflow maintenance | Stale UV pins, unlocked sync commands, malformed `.gitignore` globs, and workflow documentation drift were corrected. | `.github/workflows/`, `.gitignore`, `.github/` |

## Evidence from the completed pass

The following gates passed on the published baseline:

- Release unit tests: 46 passed.
- MkDocs hook tests: 8 passed.
- Changed-file pre-commit suite: passed, including lock, secrets, YAML,
  dependency, documentation-link, placeholder, and AGENTS structure hooks.
- Ruff check, Ruff format check, ty, dependency validation, lock validation,
  Python compilation, and parsing of all 37 workflow YAML files: passed.
- Documentation gates: 0 broken links, 99.2/100 average content quality,
  1,339/1,339 valid `AGENTS.md` files, and zero triple-check issues; strict
  MkDocs build passed.
- GitNexus impact analysis: low risk, zero affected execution processes.

The pulled-baseline full suite recorded 34,149 passed, 1,064 skipped, 60
deselected, and 23 failed. That run was completed before the configuration-only
hardening changes and should not be presented as a clean full-suite result.

## Unresolved follow-up

The 23 baseline failures cluster into separate workstreams:

1. PAI bridge tests assume local PAI skill, memory-store, and environment state.
2. CLI/orchestrator process tests fail in the local Python 3.14 environment,
   including multiprocessing startup and import-shadowing behavior.
3. Coding sandbox tests require a Docker daemon.
4. Manuscript inventory and figure tests report snapshot/provenance drift.

Investigate these in dedicated changes with real fixtures and environment
contracts. Do not weaken assertions or convert them into mocks. A separate
repository-wide dependency analysis also reported pre-existing circular-import
warnings; avoid a broad refactor until an individual cycle has a validated
owner, path, and regression probe.

## Next operator checklist

1. Confirm the working tree and remote alignment before editing:

   ```bash
   cd /home/trim/Documents/Git/HumOS/projects/platform/hum-docxology/repos/public/codomyrmex
   git fetch --prune origin
   git status --short --branch
   git diff --quiet HEAD origin/main
   ```

2. Re-run the focused gates after any refinement:

   ```bash
   UV_CACHE_DIR=/tmp/codomyrmex-uv-cache uv lock --check
   UV_CACHE_DIR=/tmp/codomyrmex-uv-cache uv run --locked pre-commit run --all-files
   UV_CACHE_DIR=/tmp/codomyrmex-uv-cache uv run --locked --group docs pytest tests/unit/release -q --no-cov
   UV_CACHE_DIR=/tmp/codomyrmex-uv-cache make docs-check
   ```

3. For the unresolved tests, first establish the exact environment contract
   and failure reproduction, then add or repair real fixtures and targeted
   acceptance tests.

4. For release automation, verify the generated documentation PR behavior in
   a controlled workflow run before relying on a production tag. Do not publish
   a package merely to test workflow wiring.

5. Before publication, run `git diff --check`, inspect the staged diff, commit
   with a Conventional Commit message, push `main`, and verify that local
   `HEAD` equals `origin/main`.

## Important files

- [Release workflow](../../.github/workflows/release.yml)
- [CI workflow](../../.github/workflows/ci.yml)
- [Pre-commit workflow](../../.github/workflows/pre-commit.yml)
- [Dependency declaration](../../pyproject.toml)
- [Locked dependency graph](../../uv.lock)
- [Test-running guide](../modules/tests/RUNNING_TESTS.md)
