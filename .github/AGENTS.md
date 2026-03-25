# .github -- AI Agent Guide

**Status**: Active | **Last Updated**: March 2026

## Purpose

This directory holds GitHub-specific configuration: CI/CD workflows, issue/PR templates,
Dependabot config, CODEOWNERS, Gemini AI command configs, and multi-agent infrastructure.
This document tells AI agents what they need to know to operate safely within this directory.

## Directory Contents

| Path | Purpose |
| --- | --- |
| `workflows/ci.yml` | Continuous integration: lint, `coverage-gate` (full tests, 40% cov), test matrix (slim for PRs), build |
| `workflows/pre-commit.yml` | Pre-commit hook validation and commit message checks (soft-fail for agents) |
| `workflows/security.yml` | Daily + push-triggered security scanning (6 scanners) |
| `workflows/release.yml` | Tag-triggered release: quality gate (40% pytest cov), build, PyPI publish |
| `workflows/documentation.yml` | Doc build and deploy on doc-file changes |
| `workflows/documentation-validation.yml` | Link checking, structure validation (PR + weekly) |
| `workflows/benchmarks.yml` | Performance regression tracking (push main + weekly) |
| `workflows/maintenance.yml` | Stale issue/PR handling (90d for PRs, jules-exempt), cleanup, metrics |
| `workflows/workflow-coordinator.yml` | Smart path-based selective workflow triggering |
| `workflows/workflow-status.yml` | Aggregated status dashboard after workflow completions |
| `workflows/code-health.yml` | Weekly code health dashboard with coverage trends |
| `workflows/auto-merge.yml` | Auto squash-merge for `jules`/`automated`/`auto-merge` labeled PRs |
| `workflows/cleanup-branches.yml` | Weekly cleanup of merged + stale branches |
| `workflows/pr-labeler.yml` | Auto-labels PRs by paths, branch name, size, and module |
| `workflows/pr-conflict-check.yml` | Scans open PRs for merge conflicts every 6 hours |
| `workflows/jules-dispatch.yml` | Batch dispatch Jules tasks as GitHub issues |
| `workflows/agent-welcome.yml` | Agent-specific PR welcome messages with checklists |
| `workflows/agent-metrics.yml` | Weekly agent PR/issue/workflow health dashboard |
| `workflows/lock-threads.yml` | Lock old closed issues (90d) and PRs (60d) |
| `workflows/gemini-*.yml` | Gemini AI-assisted review, triage, dispatch (5 workflows) |
| `ISSUE_TEMPLATE/` | Structured issue forms: bug, feature, docs, Jules task |
| `commands/` | Gemini AI command `.toml` configs for PR review and triage |
| `CODEOWNERS` | Code ownership mapping (`@docxology`) |
| `dependabot.yml` | Automated dependency update configuration (3 ecosystems) |
| `PULL_REQUEST_TEMPLATE.md` | Concise agent-friendly PR template (28 lines) |

## Agent-Specific Infrastructure

### Jules AI Agent

| Feature | Workflow | Details |
| --- | --- | --- |
| Auto-labeling | `pr-labeler.yml` | Labels by branch name, paths, size, module |
| Auto-merge | `auto-merge.yml` | Squash-merge when checks pass + `auto-merge` label |
| Welcome message | `agent-welcome.yml` | Posts checklist comment on new Jules PRs |
| Batch dispatch | `jules-dispatch.yml` | Creates issues for each module from templates |
| Issue template | `ISSUE_TEMPLATE/jules_task.yml` | Pre-configured with all 28+ modules |
| Stale exemption | `maintenance.yml` | Jules PRs exempt from stale closure |
| Conflict detection | `pr-conflict-check.yml` | Auto-labels conflicting PRs every 6h |
| Metrics | `agent-metrics.yml` | Weekly dashboard of Jules PR/issue counts |

### Gemini CLI Agent

| Feature | Workflow | Details |
| --- | --- | --- |
| PR review | `gemini-review.yml` | Automated code review on PR open |
| Issue triage | `gemini-triage.yml` | Auto-triage on issue open/reopen |
| Dispatch | `gemini-dispatch.yml` | Routes `@gemini-cli` commands |
| Scheduled triage | `gemini-scheduled-triage.yml` | Periodic batch triage |
| Invocation | `gemini-invoke.yml` | Manual Gemini invocation |

### Dependabot

| Feature | Details |
| --- | --- |
| Auto-labeling | `pr-labeler.yml` adds `dependencies` + `automated` + `auto-merge` |
| Auto-merge | `auto-merge.yml` merges when checks pass |

## Safe Operations

- Read any file in `.github/` to understand CI/CD structure and triggers
- Run `yamllint .github/workflows/*.yml` to validate YAML syntax
- Use `gh run list --workflow=<name>.yml` and `gh run view` to check status
- Use `gh pr list` and `gh issue list` to review open items
- Read `CODEOWNERS` to understand review assignment rules

## Caution Required

- **Workflow edits take effect immediately on the next trigger** — test on a branch
- **CODEOWNERS changes affect review requests** for every future PR
- **Never remove `permissions: {}` blocks** — they enforce least-privilege tokens
- **Never remove `concurrency:` blocks** — they prevent duplicate workflow runs

## Modifying Workflows — Checklist

1. Read the target workflow file fully before editing
2. Preserve all `permissions:` blocks (deny-all default + job-level grants)
3. Keep `concurrency:` groups intact
4. Pin action versions to stable tags (`@v4`, `@v5`)
5. Use `uv` (not pip/poetry) for Python dependency management
6. Test workflow changes on a feature branch before merging to main
7. Validate YAML: `python3 -c "import yaml; yaml.safe_load(open('file.yml'))"`

## CI Quick Commands

```bash
# List recent CI runs
gh run list --workflow=ci.yml --limit=5

# Check auto-merge status
gh run list --workflow=auto-merge.yml --limit=3

# List agent PRs
gh pr list --label=jules --state=open

# List conflicting PRs
gh pr list --label=conflict --state=open

# View agent metrics (latest run)
gh run list --workflow=agent-metrics.yml --limit=1

# Trigger Jules batch dispatch
gh workflow run jules-dispatch.yml -f modules=all -f task_template=docstrings-mcp-tests
```

## Operating Contracts

| Contract | Requirement |
| --- | --- |
| Workflow top-level permissions | Must be `permissions: {}` (deny-all) |
| Job-level permissions | Grant only what the job needs |
| Action pinning | Pin to specific tags, never `@main` or `@latest` |
| Concurrency | Every workflow must have a `concurrency:` block |
| Python tooling | Use `uv` for all dependency management |
| Test coverage | CI enforces **40%** minimum (`pyproject.toml`) |
| Security scanning | 6 independent scanners must remain active |
| Agent PR handling | Auto-label → CI → auto-merge pipeline |

## Navigation

- [PAI.md](PAI.md) | [SPEC.md](SPEC.md)
- [Root AGENTS](../AGENTS.md) | [Root PAI](../PAI.md)
