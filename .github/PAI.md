# .github -- PAI Integration Guide

**Status**: Active | **Last Updated**: February 2026

## Purpose

This directory holds all GitHub-specific configuration for the Codomyrmex project.
The PAI Algorithm interacts with `.github/` primarily through read-only analysis and
workflow interpretation -- it does not modify workflows autonomously without explicit
authorization via the Trust Gateway (`VERIFIED` or `TRUSTED` state).

## Workflow Inventory

The repository contains 15 workflow files. The table below lists those relevant to
PAI's Algorithm phases:

| Workflow | Trigger | What It Does |
|----------|---------|-------------|
| `ci.yml` | push/PR to main, develop | Lint (ruff, black, mypy), test matrix (3 OS x 4 Python), security scan, complexity, build package |
| `pre-commit.yml` | push/PR | Pre-commit hooks and commit message validation |
| `security.yml` | daily 2 AM UTC + push pyproject/uv.lock | Dependency scan (pip-audit, Safety), Bandit SAST, Semgrep, CodeQL, license compliance, TruffleHog secrets |
| `release.yml` | tag push `v*.*.*` or manual | Quality gate, build sdist+wheel, GitHub Release, PyPI publish, verify install |
| `documentation.yml` | push to doc files | Build and deploy documentation site |
| `documentation-validation.yml` | PR + weekly Sunday | Link checking, structure validation, full doc quality gate |
| `benchmarks.yml` | push main + weekly Wednesday 3 AM UTC | Performance regression tracking (unit, integration, memory) |
| `maintenance.yml` | weekly Sunday 6 AM UTC | Stale issue/PR handling, artifact cleanup, repository metrics |
| `workflow-coordinator.yml` | push/PR to main | Smart path-based triggering -- detects changed files and selectively runs CI, docs, security, or benchmarks |
| `workflow-status.yml` | after other workflow completions + daily 9 AM UTC | Aggregates workflow results into a status dashboard |
| `gemini-review.yml` | PR events | Gemini AI-assisted code review |
| `gemini-triage.yml` | issue events | Gemini AI-assisted issue triage |
| `gemini-dispatch.yml` | repository dispatch | Gemini command dispatch |
| `gemini-scheduled-triage.yml` | scheduled | Periodic Gemini triage |
| `gemini-invoke.yml` | workflow dispatch | Manual Gemini invocation |

## PAI Algorithm Phase Mapping

### OBSERVE Phase

PAI reads CI/CD state to understand the current health of the codebase:

- **`gh run list --workflow=ci.yml`** -- check latest CI pass/fail status
- **`gh run view <id> --log`** -- read detailed job output for failures
- **`workflow-status.yml` artifacts** -- aggregated dashboard of all workflow health
- **`workflow-coordinator.yml` change detection** -- understand which subsystems were affected by recent pushes

### THINK Phase

PAI analyzes workflow outputs to identify coverage gaps and risks:

- **`ci.yml` coverage reports** -- test coverage per module (target: 70% unit, 80% release)
- **`security.yml` artifacts** -- Bandit findings, pip-audit vulnerabilities, license issues
- **`benchmarks.yml` results** -- performance regression data for informed decision-making
- **`complexity-analysis` artifacts** -- radon cyclomatic complexity and maintainability index

### PLAN Phase

PAI uses project templates when creating issues and PRs:

- **`ISSUE_TEMPLATE/`** -- structured forms for bugs, features, and documentation
- **`PULL_REQUEST_TEMPLATE.md`** -- standard PR description format
- **`CODEOWNERS`** -- determine who should review changes to specific paths

### BUILD Phase

Workflow modifications require a feature branch and human review:

- **Never modify workflows directly on `main`** -- always use a feature branch + PR
- **Pin action versions** to specific tags (e.g., `actions/checkout@v4`)
- **Declare `permissions: {}`** at workflow top level; grant per-job as needed

### EXECUTE Phase

PAI triggers or monitors execution workflows:

- **`workflow-coordinator.yml`** -- smart triggering logic based on changed paths
- **`release.yml`** -- manually dispatchable for version releases
- **`maintenance.yml`** -- manually dispatchable for cleanup tasks

### VERIFY Phase

PAI checks that all CI quality gates pass:

- **`ci.yml` final-status job** -- aggregates lint, security, test, build results
- **`security.yml` security-status job** -- aggregates all security scan results
- **`release.yml` quality-gate job** -- 80% coverage + clean lint + security before release
- **`documentation-validation.yml`** -- link checking and structure validation for docs

### LEARN Phase

PAI reads historical data for trend analysis:

- **`benchmarks.yml`** -- performance benchmark history (weekly + per-push)
- **`maintenance.yml` metrics** -- repository health metrics over time
- **`workflow-status.yml`** -- historical workflow pass/fail trends

## Security Model

All workflows declare `permissions: {}` at the top level (deny-all default). Individual
jobs that require write access declare their own `permissions:` block explicitly. This
follows the principle of least privilege for `GITHUB_TOKEN` usage.

Key security workflows:
- **Bandit** -- Python SAST scanning with SARIF upload to GitHub Security tab
- **Semgrep** -- Pattern-based vulnerability and secrets detection
- **CodeQL** -- GitHub-native deep code analysis
- **TruffleHog** -- Verified secret detection across git history
- **pip-audit + Safety** -- Known vulnerability scanning in dependencies
- **License scan** -- GPL/AGPL/copyleft detection in dependency tree

## Constraints

- **Never modify workflow files directly on `main`** -- all changes via feature branch + PR
- **Never disable security jobs** -- `continue-on-error: false` sections are intentional
- **Read CODEOWNERS** before adding reviewers to understand team ownership patterns
- Gemini command configs in `commands/` are read-only references for PR review behavior
- Workflow concurrency groups prevent duplicate runs -- do not remove `concurrency:` blocks

## Quick Reference: gh Commands for PAI Agents

```bash
# Check CI status for current branch
gh run list --workflow=ci.yml --branch=main --limit=5

# View a specific workflow run
gh run view <run-id>

# Check security scan status
gh run list --workflow=security.yml --limit=3

# View workflow artifacts
gh run download <run-id> --name=test-results-ubuntu-latest-3.11

# Create an issue using project templates
gh issue create --template=bug_report.yml --title="..."

# Create a PR following conventions
gh pr create --title="..." --body="..."
```

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
- [Root PAI Bridge](../PAI.md) | [Root AGENTS](../AGENTS.md)
