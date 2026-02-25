# .github -- Specification

**Status**: Active | **Last Updated**: February 2026

## Overview

The `.github/` directory provides GitHub platform integration for the Codomyrmex project.
It defines CI/CD automation, contribution workflows, security scanning, and AI-assisted
review processes. This specification documents the technical requirements and contracts
for all GitHub Actions workflows and configuration files.

## Directory Structure

```
.github/
  workflows/                       # 15 GitHub Actions workflow YAML files
    ci.yml                         # Continuous integration pipeline
    pre-commit.yml                 # Pre-commit hook validation
    security.yml                   # Security scanning (6 scanners)
    release.yml                    # Release and PyPI deployment
    documentation.yml              # Doc build and deploy
    documentation-validation.yml   # Doc quality gate
    benchmarks.yml                 # Performance regression tracking
    maintenance.yml                # Repository housekeeping
    workflow-coordinator.yml       # Smart path-based triggering
    workflow-status.yml            # Aggregated status dashboard
    gemini-review.yml              # Gemini AI code review
    gemini-triage.yml              # Gemini AI issue triage
    gemini-dispatch.yml            # Gemini command dispatch
    gemini-scheduled-triage.yml    # Periodic Gemini triage
    gemini-invoke.yml              # Manual Gemini invocation
  ISSUE_TEMPLATE/                  # Structured issue forms (bug, feature, docs)
  commands/                        # Gemini AI command .toml configs
  AGENTS.md                        # AI agent operational guide
  CODEOWNERS                       # Code ownership for automatic review requests
  dependabot.yml                   # Automated dependency updates (3 ecosystems)
  PULL_REQUEST_TEMPLATE.md         # Standard PR description template
  PAI.md                           # PAI Algorithm integration guide
  SPEC.md                          # This file
```

## CI Pipeline Specification (`ci.yml`)

**Trigger**: push/PR to `main` or `develop`, plus manual `workflow_dispatch`.

**Concurrency**: grouped by workflow + ref; cancels in-progress runs on the same ref.

### Jobs and Dependencies

```
lint-and-format
  |
  +-- security-scan (needs: lint-and-format)
  +-- complexity-analysis (needs: lint-and-format)
  +-- test-matrix (needs: lint-and-format)
       |
       +-- comprehensive-tests (needs: test-matrix; main only or labeled PRs)
       +-- build-package (needs: test-matrix, security-scan)
  |
  +-- validate-dependencies (runs independently)
  |
  +-- test-summary (needs: test-matrix, comprehensive-tests; always runs)
  +-- final-status (needs: all jobs; always runs; gates merge)
```

### Lint and Format Requirements

| Tool | Purpose | Failure Behavior |
|------|---------|-----------------|
| `ruff check` | Linting with GitHub output format | Blocks pipeline |
| `ruff format --check` | Formatting verification | Blocks pipeline |
| `black --check --diff` | Secondary format check | Blocks pipeline |
| `mypy src/` | Static type checking | Blocks pipeline |
| `pylint` | Comprehensive linting | Soft fail (`|| true`) |
| `flake8` | Style guide enforcement | Soft fail (`|| true`) |

### Test Matrix

| Dimension | Values |
|-----------|--------|
| OS | `ubuntu-latest`, `macos-latest`, `windows-latest` |
| Python | `3.10`, `3.11`, `3.12`, `3.13` |
| Exclusions | macOS + 3.10, Windows + 3.10 (reducing matrix size) |

Coverage requirements:
- **CI minimum**: 70% (`--cov-fail-under=70`)
- **Release quality gate**: 80% (`--cov-fail-under=80`)

### Comprehensive Tests

Run only on pushes to `main` or PRs labeled `comprehensive-tests`. Tests four critical
modules: `git_operations`, `static_analysis`, `code_execution_sandbox`, `environment_setup`.

## Security Pipeline Specification (`security.yml`)

**Trigger**: daily 2 AM UTC schedule, push/PR when `pyproject.toml`, `uv.lock`, or
`security.yml` changes, plus manual dispatch.

### Security Scanners

| Scanner | Job Name | What It Scans |
|---------|----------|---------------|
| pip-audit | `dependency-scan` | Known vulnerabilities in installed packages |
| Safety | `dependency-scan` | CVE database for Python dependencies |
| Bandit | `bandit-scan` | Python SAST -- dangerous function calls, SQL injection, etc. |
| Semgrep | `semgrep-scan` | Pattern-based security audit, secrets detection |
| CodeQL | `codeql-analysis` | GitHub-native deep semantic code analysis |
| TruffleHog | `secret-scan` | Verified secret detection across git history |

Additional scanning:
- **License compliance** (`license-scan`): pip-licenses + licensecheck for GPL/AGPL detection
- **Dependency updates** (`dependency-update`): runs on schedule/dispatch, creates automated PRs

### SARIF Integration

Bandit and CodeQL results are uploaded as SARIF files to the GitHub Security tab via
`github/codeql-action/upload-sarif@v3`.

## Release Pipeline Specification (`release.yml`)

**Trigger**: tag push matching `v*.*.*` or manual dispatch with version input.

**Concurrency**: grouped by workflow + ref; does NOT cancel in-progress (releases are
not interruptible).

### Release Flow

```
prepare-release (extract + validate version)
  |
  +-- quality-gate (80% coverage, clean lint, security, twine check)
       |
       +-- build-artifacts (sdist + wheel in parallel matrix)
            |
            +-- create-release (GitHub Release with auto-generated notes)
                 |
                 +-- publish-pypi (stable releases only; trusted publishing via OIDC)
                 +-- publish-test-pypi (pre-releases only)
                      |
                      +-- verify-release (install test on Python 3.10, 3.11, 3.12)
  |
  +-- update-documentation (non-prerelease only; triggers doc rebuild)
  +-- release-status (summary of all jobs; always runs)
```

### Version Validation

Accepted format: `MAJOR.MINOR.PATCH` or `MAJOR.MINOR.PATCH-PRERELEASE`.
Pre-release detection: versions containing `alpha`, `beta`, `rc`, or `dev` are marked
as pre-releases and published to Test PyPI instead of production PyPI.

## Benchmarks Specification (`benchmarks.yml`)

**Trigger**: push to `main`, PR to `main`, weekly Wednesday 3 AM UTC, manual dispatch.
**Types**: `all`, `unit`, `integration`, `memory` (selectable via dispatch input).

## Maintenance Specification (`maintenance.yml`)

**Trigger**: weekly Sunday 6 AM UTC, manual dispatch.
**Tasks**: `stale-issues` (close after inactivity), `cleanup` (artifact pruning),
`metrics` (repository health stats).

## Workflow Coordinator Specification (`workflow-coordinator.yml`)

**Trigger**: push/PR to `main`/`develop`.
Detects which files changed and selectively triggers the appropriate subset of CI, docs,
security, or benchmark workflows. Avoids running all pipelines on every push.

## Workflow Status Dashboard (`workflow-status.yml`)

**Trigger**: after completion of CI, pre-commit, security, docs, benchmarks, or
maintenance workflows, plus daily 9 AM UTC schedule.
Aggregates the latest status of all monitored workflows into a GitHub Step Summary.

## Permissions Model

All workflows follow the principle of least privilege:

1. **Workflow-level**: `permissions: {}` (deny all) -- declared at the top of every YAML
2. **Job-level**: Only the specific permissions needed (e.g., `contents: read`,
   `security-events: write`)
3. **Token scope**: `GITHUB_TOKEN` is the default; `CODECOV_TOKEN` and
   `SEMGREP_APP_TOKEN` are stored as repository secrets

## Dependabot Specification

Three ecosystems are monitored weekly (Mondays 09:00 UTC):

| Ecosystem | Scope | PR Limit | Major Version Policy |
|-----------|-------|----------|---------------------|
| `github-actions` | All action dependencies | 10 | Grouped into single PR |
| `pip` | Direct Python dependencies only | 5 | Major bumps ignored (manual review required) |
| `npm` | `/src/codomyrmex/documentation` | 5 | Standard update policy |

All PRs are labeled `dependencies` + `automated` and assigned to
`@docxology/codomyrmex-maintainers`.

## Branch and PR Policies

- **Protected branches**: `main`, `develop` (CI must pass before merge)
- **Required status checks**: `final-status` job from `ci.yml`
- **CODEOWNERS**: all paths default to `@docxology/codomyrmex-maintainers`
- **PR template**: standardized description format in `PULL_REQUEST_TEMPLATE.md`
- **Concurrency**: all workflows use `concurrency:` groups to prevent duplicate runs

## Navigation

- [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- [Root SPEC](../SPEC.md) | [Root README](../README.md)
