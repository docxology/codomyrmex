# .github/workflows — AI Agent Guide

**Status**: Active | **Last Updated**: February 2026

## Purpose

GitHub Actions workflow definitions for CI/CD, security scanning, release automation,
documentation, benchmarks, and repository maintenance.

## Workflow Inventory

| File | Trigger | Key Jobs |
|------|---------|----------|
| `ci.yml` | push/PR main,develop | lint-and-format, test-matrix, build-package |
| `pre-commit.yml` | push/PR | pre-commit, commit-message-check |
| `security.yml` | schedule daily + push | dependency-scan, bandit, semgrep, codeql, trufflehog |
| `release.yml` | tag `v*.*.*` | quality-gate, build-artifacts, publish-pypi |
| `documentation.yml` | doc file changes | validate, build, deploy |
| `documentation-validation.yml` | PR + weekly | link-check, structure-check |
| `benchmarks.yml` | push main + weekly | unit/integration/memory benchmarks |
| `maintenance.yml` | weekly Sunday | stale-issues, artifact-cleanup, metrics |
| `workflow-coordinator.yml` | push/PR | smart triggering by changed paths |
| `workflow-status.yml` | workflow_run | dashboard update |
| `gemini-*.yml` | various | AI-assisted PR review and triage |

## Critical Design Decisions

- All workflows have `permissions: {}` at top-level (deny-all default) — jobs that need
  write access declare their own `permissions:` block explicitly
- `astral-sh/setup-uv@v5` is the standard for all UV installations
- Cache step must precede `uv sync` in every job to maximize cache hit rate
- Windows matrix steps that use bash syntax must include `shell: bash`

## AI Agent Guidelines

### Safe to Read
- Any workflow file to understand triggers, jobs, and permissions
- `yamllint` output to check syntax before suggesting edits

### Before Modifying Any Workflow
1. Read the full workflow file
2. Identify all jobs with explicit `permissions:` and preserve them
3. Check if any steps run on Windows (`windows-latest`) — they need `shell: bash` for bash syntax
4. Verify action version upgrades don't change interface (e.g., codecov v4→v5 moved token location)
5. Stage changes on a feature branch, not directly on main

### Common Patterns
- `uv sync --all-extras --dev` installs all optional dependencies for testing
- `|| true` on tool runs (bandit, pylint) prevents CI failure on warnings
- `if: always()` on summary/status jobs ensures they run even when prior jobs fail
- `continue-on-error: true` on security scans prevents blocking on external service issues

### Action Version Policy
- All actions pinned to latest stable major tag (e.g., `@v4`, `@v5`)
- For security-critical actions (semgrep, trufflehog), prefer SHA pinning in future
- `setup-uv` tracks `@v5`; upgrade when new major released and interface verified
