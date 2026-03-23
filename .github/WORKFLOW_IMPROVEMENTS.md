# 🚀 GitHub Actions Workflow Improvements

**Last Updated**: March 2026

## Current State: 36 Active Workflows

### Core CI/CD & Security (5)

| # | Workflow | File | Status |
| :---: | --- | --- | :---: |
| 1 | Continuous Integration | `ci.yml` | ✅ |
| 2 | Pre-commit Checks | `pre-commit.yml` | ✅ |
| 3 | Security Scanning | `security.yml` | ✅ |
| 4 | Dependency Review | `dependency-review.yml` | ✅ |
| 5 | Release & PyPI | `release.yml` | ✅ |

### PR Automation & Agent Infrastructure (12)

| # | Workflow | File | Status |
| :---: | --- | --- | :---: |
| 6 | Auto-Merge Agent PRs | `auto-merge.yml` | ✅ |
| 7 | PR Auto-Labeler | `pr-labeler.yml` | ✅ |
| 8 | PR Title Semantic Check | `pr-title-check.yml` | ✅ |
| 9 | PR Auto-Assigner | `auto-assign.yml` | ✅ |
| 10 | PR Conflict Checker | `pr-conflict-check.yml` | ✅ |
| 11 | Dependabot Auto-Approve | `dependabot-auto-approve.yml` | ✅ |
| 12 | Agent PR Welcome | `agent-welcome.yml` | ✅ |
| 13 | PR Linter Comments | `pr-linter-comments.yml` | ✅ |
| 14 | Post Coverage Comment | `pr-coverage-comment.yml` | ✅ |
| 15 | Agent Metrics Dashboard | `agent-metrics.yml` | ✅ |
| 16 | Jules Batch Dispatch | `jules-dispatch.yml` | ✅ |
| 17 | First Interaction Greeter | `first-interaction.yml` | ✅ |

### Documentation (2)

| # | Workflow | File | Status |
| :---: | --- | --- | :---: |
| 16 | Doc Build & Deploy | `documentation.yml` | ✅ |
| 17 | Doc Quality Gate | `documentation-validation.yml` | ✅ |

### Repository Health (5)

| # | Workflow | File | Status |
| :---: | --- | --- | :---: |
| 18 | Code Health Dashboard | `code-health.yml` | ✅ |
| 19 | Performance Benchmarks | `benchmarks.yml` | ✅ |
| 20 | Repository Maintenance | `maintenance.yml` | ✅ |
| 21 | Branch Cleanup | `cleanup-branches.yml` | ✅ |
| 22 | Lock Old Threads | `lock-threads.yml` | ✅ |

### Orchestration (2)

| # | Workflow | File | Status |
| :---: | --- | --- | :---: |
| 23 | Workflow Coordinator | `workflow-coordinator.yml` | ✅ |
| 24 | Workflow Status Dashboard | `workflow-status.yml` | ✅ |

### Gemini AI (5)

| # | Workflow | File | Status |
| :---: | --- | --- | :---: |
| 25 | Gemini Dispatch | `gemini-dispatch.yml` | ✅ |
| 26 | Gemini Review | `gemini-review.yml` | ✅ |
| 27 | Gemini Triage | `gemini-triage.yml` | ✅ |
| 28 | Gemini Scheduled Triage | `gemini-scheduled-triage.yml` | ✅ |
| 29 | Gemini Invoke | `gemini-invoke.yml` | ✅ |

---

## Agent PR Pipeline

```text
PR Opened (by Jules/Dependabot/Gemini/Human)
  │
  ├─ pr-labeler.yml ────────→ Auto-label (paths, branch, size, module)
  ├─ pr-title-check.yml ────→ Enforce semantic PR title
  ├─ auto-assign.yml ───────→ Assign PR to creator
  ├─ first-interaction.yml ─→ Welcome first-time contributors
  ├─ dependency-review.yml ─→ Security scan of lockfile changes
  ├─ agent-welcome.yml ─────→ Post agent-specific welcome + checklist
  ├─ pr-linter-comments.yml ─→ Runs Ruff and posts inline PR review comments
  ├─ ci.yml ────────────────→ Lint + Test (ubuntu/3.11 for PRs)
  │  └─ pr-coverage-comment.yml → Cross-run workflow that posts code coverage delta
  ├─ pre-commit.yml ───────→ Commit checks (soft-fail for agents)
  ├─ gemini-review.yml ─────→ AI code review comments
  │
  ├─ pr-conflict-check.yml → Labels 'conflict' if conflicting (every 6h)
  │
  └─ auto-merge.yml ────────→ Squash-merge execution when all gates clear
          ↑ (Approved instantly by `dependabot-auto-approve.yml` for bots)

PR Merged to `main`
  │
  ├─ first-pr-merged.yml ───→ Congratulatory comment if it's their 1st merged PR
  └─ release-drafter.yml ───→ Sort PR into Draft Release using `pr-labeler` tags
```

## Scheduled Tasks

| Schedule | Workflows |
| --- | --- |
| Daily 2 AM | Security scanning |
| Every 6h | PR conflict check |
| Daily 9 AM | Workflow status dashboard |
| Weekly Mon | Agent metrics dashboard |
| Weekly Wed | Performance benchmarks |
| Weekly Sun | Maintenance, code health, branch cleanup, lock threads |

## Key Configuration

| Setting | Value |
| --- | --- |
| Coverage gate (CI) | 25% |
| Coverage gate (release) | 25% |
| PR stale threshold | 90 days |
| Issue stale threshold | 60 days |
| Jules exempt from stale | ✅ |
| Agent PR auto-merge | ✅ (with `auto-merge` label) |
| Operations per maintenance run | 100 |
| Thread lock (issues) | 90 days after close |
| Thread lock (PRs) | 60 days after close |
| Branch cleanup (stale) | 14 days |

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [README.md](README.md)
