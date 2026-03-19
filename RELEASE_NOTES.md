# Codomyrmex v1.2.3 — "Coherence Release"

## Overview

This release locks down repo-wide structural coherence: 39 missing modules registered, version skew resolved across 7 files, coverage gate unified to 40%, and spurious root files purged. The ecosystem is now a clean single-source-of-truth at v1.2.3 with 129 registered modules.

## Key Advancements

- **Version Coherence**: Reconciled `pyproject.toml` (1.2.2), `__init__.py` (1.1.9), `README.md` (1.1.9), and `SPEC.md` (1.1.9) — all aligned to **v1.2.3** across 7 files.
- **Module Registration**: 39 modules existed on disk but were absent from `__init__.py` `_submodules` and `__all__` — all 129 now registered and lazy-importable.
- **Coverage Gate Unified**: Contradictory `fail_under` values (75, 40, 33%, 35%) consolidated to **40%** across all config locations.
- **Python Classifier Fix**: Removed misleading `Python :: 3.10` classifier (project requires `>=3.11`).
- **Spurious File Removal**: 3 git-tracked junk files at repo root (`Any`, `dict[str,`) created by buggy type-annotation script — deleted.
- **Sub-level Version Sync**: `src/README.md` (v0.1.0 → v1.2.3) and `src/codomyrmex/AGENTS.md` (v0.1.0 → v1.2.3) updated.

## Metrics Snapshot

| Metric | Before | v1.2.3 |
|--------|--------|---------|
| Registered modules | 90 | **129** (+39) |
| Version files synced | 1 | **7** |
| Coverage gate | 75/40/33% (inconsistent) | **40%** (unified) |
| Spurious root files | 3 | **0** |
| Tests collected | 21,000+ | **21,000+** |
| Ruff violations | 0 | **0** ✅ |

## Previous Release

See [v1.1.9 CHANGELOG entry](CHANGELOG.md#119---2026-03-07---multimodal--streaming) for the Multimodal & Streaming release details.
