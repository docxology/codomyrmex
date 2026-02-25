# .github/workflows — Specification

**Status**: Active | **Last Updated**: February 2026

## Design Principles

1. **Deny-all permissions by default**: `permissions: {}` at top level; jobs grant only what they need
2. **Reproducible builds**: `uv.lock` pinned; `setup-uv@v5` pinned to stable major
3. **Fast feedback**: cache restore before `uv sync`; `fail-fast: false` on matrices
4. **Security coverage**: SAST (bandit, semgrep), SCA (safety scan), secrets (trufflehog)
5. **Observability**: all workflow runs update the status dashboard

## Workflow Contracts

### ci.yml
- Triggers: push/PR to `main`, `develop`
- Gates: ruff, black, mypy, pytest (matrix: 3.10, 3.11, 3.12 × ubuntu/windows/macos)
- Artifacts: coverage.xml, junit-*.xml
- Codecov upload: `codecov/codecov-action@v5` with OIDC token

### security.yml
- Triggers: daily schedule + push to `main`/`develop` when `pyproject.toml` or `uv.lock` changes
- Scans: bandit (SAST), safety scan (SCA), semgrep (SAST), trufflehog (secrets), license check
- Auto-PR: opens PR for dependency updates via `peter-evans/create-pull-request@v7`
- TruffleHog scan range: push → `event.before`..`sha`; PR → base.sha..head.sha

### release.yml
- Triggers: `v*.*.*` tag push
- Flow: quality-gate → build-artifacts → publish-pypi → verify-install (retry loop 10×) → GitHub Release
- Git identity: `github-actions[bot]` for automated version bumps

### benchmarks.yml
- Triggers: push to `main` + weekly schedule
- Baselines stored as workflow artifacts for regression comparison

## Action Version Policy

| Action | Version | Notes |
|--------|---------|-------|
| `astral-sh/setup-uv` | `@v5` | Upgrade from v3 — all workflows |
| `actions/checkout` | `@v4` | Standard across all jobs |
| `codecov/codecov-action` | `@v5` | Token in `with:`, not `env:` |
| `peter-evans/create-pull-request` | `@v7` | For automated dependency PRs |
| `actions/setup-python` | `@v5` | Only in release verify job |
