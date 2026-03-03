# .github -- Specification

**Status**: Active | **Last Updated**: March 2026

## Overview

The `.github/` directory provides GitHub platform integration for the Codomyrmex project.
It defines CI/CD automation, multi-agent infrastructure, security scanning, and AI-assisted
review processes. This specification documents the technical requirements and contracts
for all 24 GitHub Actions workflows.

## Directory Structure

```
.github/
  workflows/                        # 24 GitHub Actions workflow YAML files
    # ─── Core CI/CD ───
    ci.yml                          # Continuous integration pipeline
    pre-commit.yml                  # Pre-commit hook validation
    security.yml                    # Security scanning (6 scanners)
    release.yml                     # Tag-triggered release and PyPI
    # ─── Documentation ───
    documentation.yml               # Doc build and deploy
    documentation-validation.yml    # Doc quality gate (links, structure)
    # ─── Agent Infrastructure ───
    auto-merge.yml                  # Auto squash-merge agent PRs
    pr-labeler.yml                  # Auto-label PRs by paths/branch/size
    pr-conflict-check.yml           # Conflict detection every 6h
    agent-welcome.yml               # Agent-specific PR welcome
    agent-metrics.yml               # Weekly agent health dashboard
    jules-dispatch.yml              # Batch dispatch Jules tasks
    # ─── Repository Health ───
    code-health.yml                 # Coverage trends dashboard
    benchmarks.yml                  # Performance regression tracking
    maintenance.yml                 # Stale issues, cleanup, metrics
    cleanup-branches.yml            # Merged/stale branch cleanup
    lock-threads.yml                # Lock old closed threads
    # ─── Orchestration ───
    workflow-coordinator.yml        # Smart path-based triggering
    workflow-status.yml             # Aggregated status dashboard
    # ─── Gemini AI ───
    gemini-dispatch.yml             # Gemini command dispatch
    gemini-review.yml               # Gemini AI code review
    gemini-triage.yml               # Gemini AI issue triage
    gemini-scheduled-triage.yml     # Periodic Gemini triage
    gemini-invoke.yml               # Manual Gemini invocation
  ISSUE_TEMPLATE/                   # 4 form templates: bug, feature, docs, jules
  commands/                         # 4 Gemini AI .toml configs
  AGENTS.md                         # AI agent operational guide
  CODEOWNERS                        # @docxology for all paths
  dependabot.yml                    # 3 ecosystems (actions, pip, npm)
  PULL_REQUEST_TEMPLATE.md          # 27-line agent-friendly template
  PAI.md / SPEC.md / README.md      # Integration docs
```

## CI Pipeline (`ci.yml`)

**Trigger**: push/PR to `main`/`develop`, `workflow_dispatch`.

### PR vs Main Matrix

| Context | OS | Python Versions |
|---------|-----|-----------------|
| Pull Requests | `ubuntu-latest` | `3.11` only |
| Push to `main` | `ubuntu-latest`, `macos-latest`, `windows-latest` | `3.10`, `3.11`, `3.12`, `3.13` |

### Lint & Format Requirements

| Tool | Failure Behavior |
|------|-----------------|
| `ruff check` | Blocks pipeline |
| `ruff format --check` | Blocks pipeline |
| `black --check` | Soft-fail (`continue-on-error`) |
| `mypy src/` | Soft-fail (`continue-on-error`) |
| `pylint`, `flake8` | Soft fail (`|| true`) |

### Coverage Gates

| Context | Threshold |
|---------|-----------|
| CI minimum | 25% |
| Release quality gate | 25% |
| `pytest.ini` default | 25% |

## Agent PR Pipeline

```
PR Opened
  ├─→ pr-labeler.yml      (adds labels: jules, source, module:X, size/M, etc.)
  ├─→ agent-welcome.yml   (posts welcome comment with checklist)
  ├─→ ci.yml               (runs lint + tests on ubuntu/3.11)
  ├─→ pre-commit.yml       (commit checks, soft-fail for agents)
  ├─→ gemini-review.yml    (AI code review)
  │
  ├─→ pr-conflict-check.yml (every 6h: adds/removes 'conflict' label)
  │
  └─→ auto-merge.yml       (squash-merge when all checks pass + auto-merge label)
```

## Maintenance Schedule

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `maintenance.yml` | Sunday 6 AM UTC | Stale issues (60d), stale PRs (90d), artifact cleanup |
| `cleanup-branches.yml` | Weekly | Delete merged + 14d stale branches |
| `lock-threads.yml` | Sunday 4 AM UTC | Lock 90d issues, 60d PRs |
| `agent-metrics.yml` | Monday 12 AM UTC | Agent PR/issue/workflow dashboard |
| `code-health.yml` | Sunday 8 AM UTC | Coverage trends, ruff stats |
| `security.yml` | Daily 2 AM UTC | 6-scanner security pipeline |
| `benchmarks.yml` | Wednesday 3 AM UTC | Performance regression tracking |

## Security Scanner Inventory

| Scanner | Job | What It Scans |
|---------|-----|-------------|
| pip-audit | `dependency-scan` | Known CVEs in packages |
| Safety | `dependency-scan` | CVE database for Python deps |
| Bandit | `bandit-scan` | Python SAST |
| Semgrep | `semgrep-scan` | Pattern-based security |
| CodeQL | `codeql-analysis` | Deep semantic analysis |
| TruffleHog | `secret-scan` | Secrets in git history |

## Permissions Model

1. **Workflow-level**: `permissions: {}` (deny all) on every YAML
2. **Job-level**: Only specific permissions needed
3. **Tokens**: `GITHUB_TOKEN` default; `CODECOV_TOKEN`, `SEMGREP_APP_TOKEN` as secrets

## Stale Management Policy

| Target | Days to Stale | Days to Close | Exempt Labels |
|--------|:---:|:---:|---|
| Issues | 60 | 7 | `keep-open`, `pinned`, `security`, `jules`, `agent-task` |
| PRs | 90 | 14 | `keep-open`, `pinned`, `security`, `wip`, `jules`, `agent-pr`, `auto-merge` |

Operations per run: 100. Jules and agent PRs are **never** auto-closed.

## Navigation

- [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- [Root SPEC](../SPEC.md) | [Root README](../README.md)
