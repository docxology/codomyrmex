# .github -- AI Agent Guide

**Status**: Active | **Last Updated**: February 2026

## Purpose

This directory holds GitHub-specific configuration: CI/CD workflows, issue/PR templates,
Dependabot config, CODEOWNERS, and Gemini AI command configs. This document tells AI
agents what they need to know to operate safely within this directory.

## Directory Contents

| Path | Purpose |
|------|---------|
| `workflows/ci.yml` | Continuous integration: lint, test matrix, security scan, build |
| `workflows/pre-commit.yml` | Pre-commit hook validation and commit message checks |
| `workflows/security.yml` | Daily + push-triggered security scanning (6 scanners) |
| `workflows/release.yml` | Tag-triggered release: quality gate, build, PyPI publish |
| `workflows/documentation.yml` | Doc build and deploy on doc-file changes |
| `workflows/documentation-validation.yml` | Link checking, structure validation (PR + weekly) |
| `workflows/benchmarks.yml` | Performance regression tracking (push main + weekly) |
| `workflows/maintenance.yml` | Stale issue handling, cleanup, metrics (weekly Sunday) |
| `workflows/workflow-coordinator.yml` | Smart path-based selective workflow triggering |
| `workflows/workflow-status.yml` | Aggregated status dashboard after workflow completions |
| `workflows/gemini-*.yml` | Gemini AI-assisted review, triage, dispatch (5 workflows) |
| `ISSUE_TEMPLATE/` | Structured issue forms (bug, feature, docs) with RASP docs |
| `commands/` | Gemini AI command `.toml` configs for PR review and triage |
| `CODEOWNERS` | Code ownership mapping for automatic review requests |
| `dependabot.yml` | Automated dependency update configuration (3 ecosystems) |
| `PULL_REQUEST_TEMPLATE.md` | Standard PR description template |

## Safe Operations

These operations are always safe and require no special authorization:

- Read any file in `.github/` to understand CI/CD structure and triggers
- Read workflow files to understand pipeline logic before modifying source code
- Run `yamllint .github/workflows/*.yml` to validate YAML syntax
- Use `gh run list` and `gh run view` to check workflow status
- Use `gh pr list` and `gh issue list` to review open items
- Read `CODEOWNERS` to understand review assignment rules
- Read `dependabot.yml` to understand dependency update cadence

## Caution Required

These operations have side effects and demand careful handling:

- **Workflow edits take effect immediately on the next trigger** -- always test on a branch
- **CODEOWNERS changes affect review requests** for every future PR
- **dependabot.yml changes affect automated PR frequency** and ecosystem coverage
- **Never remove `permissions: {}` blocks** -- they enforce least-privilege tokens
- **Never remove `concurrency:` blocks** -- they prevent duplicate workflow runs

## CODEOWNERS Reference

The current CODEOWNERS file assigns `@docxology/codomyrmex-maintainers` as the default
owner for all paths. Key ownership sections:

| Path Pattern | Owner |
|-------------|-------|
| `*` (global default) | `@docxology/codomyrmex-maintainers` |
| `/.github/` | `@docxology/codomyrmex-maintainers` |
| `/src/` | `@docxology/codomyrmex-maintainers` |
| `/docs/` | `@docxology/codomyrmex-maintainers` |
| `/pyproject.toml`, `/uv.lock` | `@docxology/codomyrmex-maintainers` |
| `/scripts/` | `@docxology/codomyrmex-maintainers` |

When creating a PR, agents should expect reviews from the matching CODEOWNERS team.

## Dependabot Configuration

Dependabot monitors three ecosystems on a weekly schedule (Mondays 09:00 UTC):

| Ecosystem | Directory | PR Limit | Grouping | Notes |
|-----------|-----------|----------|----------|-------|
| `github-actions` | `/` | 10 | All action updates grouped into one PR | Patterns: `actions/*`, `astral-sh/*`, `github/*`, `semgrep/*`, `pypa/*`, `peter-evans/*`, `trufflesecurity/*` |
| `pip` | `/` | 5 | Direct deps only | Major version bumps ignored (require manual review) |
| `npm` | `/src/codomyrmex/documentation` | 5 | Per-package | For documentation build tooling |

All Dependabot PRs are labeled `dependencies` + `automated` and assigned to
`@docxology/codomyrmex-maintainers` for review.

## Modifying Workflows -- Checklist

1. Read the target workflow file fully before editing
2. Understand which jobs have explicit `permissions:` -- do not remove them
3. Keep `permissions: {}` at the workflow top level (deny-all default)
4. When adding new action versions, pin to the latest stable tag (e.g., `@v4`)
5. When adding bash steps that run on the Windows matrix, include `shell: bash`
6. Test workflow changes on a feature branch before merging to main
7. Verify `concurrency:` groups are preserved to prevent duplicate runs
8. Ensure new jobs use `uv` (not pip/poetry) for Python dependency management

## Verifying CI Status -- Quick Commands

```bash
# List recent CI runs
gh run list --workflow=ci.yml --limit=5

# Check the latest run status
gh run list --workflow=ci.yml --limit=1 --json status,conclusion

# View logs for a specific run
gh run view <run-id> --log

# Download test artifacts
gh run download <run-id> --name=test-results-ubuntu-latest-3.11

# Check security workflow status
gh run list --workflow="Security Scanning and Dependency Management" --limit=3

# List open Dependabot PRs
gh pr list --label=dependencies --state=open

# View workflow-status dashboard (latest)
gh run list --workflow="Workflow Status Dashboard" --limit=1
```

## Operating Contracts

| Contract | Requirement |
|----------|-------------|
| Workflow top-level permissions | Must be `permissions: {}` (deny-all) |
| Job-level permissions | Grant only what the job needs (e.g., `contents: read`) |
| Action pinning | Pin to specific tags, never `@main` or `@latest` |
| Concurrency | Every workflow must have a `concurrency:` block |
| Python tooling | Use `uv` for all dependency management |
| Test coverage | CI enforces 70% minimum; release gate enforces 80% |
| Security scanning | 6 independent scanners must remain active |

## Gemini Commands

The `commands/` directory holds `.toml` configs for Gemini AI-assisted PR review,
dispatch, triage, and scheduled operations. These are separate from the main CI system
and are triggered by their own `gemini-*.yml` workflows. Agents should treat these
configs as read-only references.

## Navigation

- [PAI.md](PAI.md) | [SPEC.md](SPEC.md)
- [Root AGENTS](../AGENTS.md) | [Root PAI](../PAI.md)
