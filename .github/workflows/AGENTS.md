# .github/workflows — AI Agent Guide

**Status**: Active | **Last Updated**: March 2026

## Purpose

GitHub Actions workflow definitions for CI/CD, security, multi-agent infrastructure,
documentation, benchmarks, PR automation, and repository maintenance. 33 workflows total.

## Workflow Inventory

### Core CI/CD

| File | Trigger | Key Jobs |
|------|---------|----------|
| `ci.yml` | push/PR main,develop | lint, `coverage-gate`, test-matrix (slim for PRs), build |
| `pre-commit.yml` | push/PR | pre-commit, commit-message-check and repository consistency checks |
| `security.yml` | schedule daily + push | dependency-scan, bandit, semgrep, codeql, trufflehog |
| `release.yml` | tag `v*.*.*` | quality-gate (60% cov), build, PyPI publish |

### Agent & PR Infrastructure

| File | Trigger | Purpose |
|------|---------|---------|
| `auto-merge.yml` | check_suite, label | Squash-merge PRs with `jules`/`auto-merge` labels |
| `pr-labeler.yml` | PR opened/sync | Auto-label by paths, branch, size, module |
| `pr-title-check.yml` | PR open/edit/sync | Enforce Semantic/Conventional Commits for PR titles |
| `auto-assign.yml` | PR opened | Auto-assign PR creator as assignee |
| `pr-conflict-check.yml` | push main, every 6h | Detect + label conflicting PRs |
| `pr-linter-comments.yml`| PR opened/sync | Post inline Ruff linter comments on changed files |
| `pr-coverage-comment.yml`| CI complete | Post coverage delta and missing test lines |
| `agent-welcome.yml` | PR opened | Agent-specific welcome message + checklist |
| `agent-metrics.yml` | weekly Monday | Agent PR/issue/workflow health dashboard |
| `jules-dispatch.yml` | workflow_dispatch | Batch create Jules task issues |
| `dependabot-auto-approve.yml`| PR opened | Auto-approve Dependabot PRs to unblock auto-merge |

### Community & Release Automation

| File | Trigger | Purpose |
|------|---------|---------|
| `first-interaction.yml` | Issue/PR opened | Greet first-time contributors with helpful links |
| `first-pr-merged.yml` | PR closed (merged) | Post congratulatory welcome on first merged PR |
| `release-drafter.yml` | push main | Auto-draft release notes based on PR labels |

### Documentation

| File | Trigger | Purpose |
|------|---------|---------|
| `documentation.yml` | doc file changes | Build and deploy to GitHub Pages |
| `documentation-validation.yml` | PR + weekly | Link check, structure validation |

### Repository Health

| File | Trigger | Purpose |
|------|---------|---------|
| `code-health.yml` | push main, weekly Sunday | Coverage trends, ruff stats |
| `benchmarks.yml` | push main, weekly Wed | Performance regression tracking |
| `maintenance.yml` | weekly Sunday | Stale issues/PRs, artifact cleanup |
| `cleanup-branches.yml` | weekly | Delete merged + stale branches |
| `lock-threads.yml` | weekly Sunday | Lock 90d issues, 60d PRs |

### Orchestration

| File | Trigger | Purpose |
|------|---------|---------|
| `workflow-coordinator.yml` | push/PR | Smart path-based triggering |
| `workflow-status.yml` | workflow_run | Status dashboard |

### Gemini AI

| File | Trigger | Purpose |
|------|---------|---------|
| `gemini-dispatch.yml` | various | Route `@gemini-cli` commands |
| `gemini-review.yml` | PR opened | AI code review |
| `gemini-triage.yml` | issue opened | AI issue triage |
| `gemini-scheduled-triage.yml` | weekly | Batch triage unlabeled issues |
| `gemini-invoke.yml` | manual dispatch | On-demand Gemini analysis |

## Critical Design Decisions

- All workflows have `permissions: {}` at top-level (deny-all default)
- `astral-sh/setup-uv@v5` is the standard for all UV installations
- CI runs slim matrix (ubuntu/3.11 only) for PRs; full matrix on main push
- Ruff, ty, import layering, package build, dependency validation, and the
  primary test/coverage gates are authoritative. Optional PR commentary and
  benchmark/health reporting jobs remain informational.
- Documented coverage floor is **60%** (`fail_under` in `pyproject.toml`). CI unit matrix and **`coverage-gate`** jobs pass `--cov-fail-under=60` and fail on breach. `release.yml` uses `--cov-fail-under=60`. Default local `uv run pytest` omits `--cov` for speed.
- Jules PRs are exempt from stale closure (90d stale, 14d close)

## AI Agent Guidelines

### Safe to Read

- Any workflow file to understand triggers, jobs, and permissions
- `yamllint` output to check syntax before suggesting edits

### Before Modifying Any Workflow

1. Read the full workflow file
2. Preserve all `permissions:` blocks
3. Check Windows matrix — use `shell: bash` for bash syntax
4. Verify action versions don't change interface
5. Stage changes on a feature branch, not directly on main

### Common Patterns

- `uv sync --all-extras --dev` installs all optional dependencies
- `if: always()` is limited to report/status jobs; required checks must preserve
  the underlying failure result and be enforced by their final status job.
- `if: always()` on summary jobs ensures they run after failures
- `continue-on-error: true` on lint/format steps for agent flexibility
