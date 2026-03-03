# 🚀 GitHub Actions Workflow Improvements

**Last Updated**: March 2026

## Current State: 24 Active Workflows

### Core CI/CD (4)

| # | Workflow | File | Status |
|:-:|---------|------|:------:|
| 1 | Continuous Integration | `ci.yml` | ✅ |
| 2 | Pre-commit Checks | `pre-commit.yml` | ✅ |
| 3 | Security Scanning | `security.yml` | ✅ |
| 4 | Release & PyPI | `release.yml` | ✅ |

### Agent Infrastructure (6)

| # | Workflow | File | Status |
|:-:|---------|------|:------:|
| 5 | Auto-Merge Agent PRs | `auto-merge.yml` | ✅ |
| 6 | PR Auto-Labeler | `pr-labeler.yml` | ✅ |
| 7 | PR Conflict Checker | `pr-conflict-check.yml` | ✅ |
| 8 | Agent PR Welcome | `agent-welcome.yml` | ✅ |
| 9 | Agent Metrics Dashboard | `agent-metrics.yml` | ✅ |
| 10 | Jules Batch Dispatch | `jules-dispatch.yml` | ✅ |

### Documentation (2)

| # | Workflow | File | Status |
|:-:|---------|------|:------:|
| 11 | Doc Build & Deploy | `documentation.yml` | ✅ |
| 12 | Doc Quality Gate | `documentation-validation.yml` | ✅ |

### Repository Health (5)

| # | Workflow | File | Status |
|:-:|---------|------|:------:|
| 13 | Code Health Dashboard | `code-health.yml` | ✅ |
| 14 | Performance Benchmarks | `benchmarks.yml` | ✅ |
| 15 | Repository Maintenance | `maintenance.yml` | ✅ |
| 16 | Branch Cleanup | `cleanup-branches.yml` | ✅ |
| 17 | Lock Old Threads | `lock-threads.yml` | ✅ |

### Orchestration (2)

| # | Workflow | File | Status |
|:-:|---------|------|:------:|
| 18 | Workflow Coordinator | `workflow-coordinator.yml` | ✅ |
| 19 | Workflow Status Dashboard | `workflow-status.yml` | ✅ |

### Gemini AI (5)

| # | Workflow | File | Status |
|:-:|---------|------|:------:|
| 20 | Gemini Dispatch | `gemini-dispatch.yml` | ✅ |
| 21 | Gemini Review | `gemini-review.yml` | ✅ |
| 22 | Gemini Triage | `gemini-triage.yml` | ✅ |
| 23 | Gemini Scheduled Triage | `gemini-scheduled-triage.yml` | ✅ |
| 24 | Gemini Invoke | `gemini-invoke.yml` | ✅ |

---

## Agent PR Pipeline

```
PR Opened (by Jules/Dependabot/Gemini)
  │
  ├─ pr-labeler.yml ─────→ Auto-label (paths, branch, size, module)
  ├─ agent-welcome.yml ──→ Post agent-specific welcome + checklist
  ├─ ci.yml ──────────────→ Lint + Test (ubuntu/3.11 for PRs)
  ├─ pre-commit.yml ─────→ Commit checks (soft-fail for agents)
  ├─ gemini-review.yml ──→ AI code review comments
  │
  ├─ pr-conflict-check.yml → Labels 'conflict' if conflicting (every 6h)
  │
  └─ auto-merge.yml ─────→ Squash-merge when all checks pass
```

## Scheduled Tasks

| Schedule | Workflows |
|----------|-----------|
| Daily 2 AM | Security scanning |
| Every 6h | PR conflict check |
| Daily 9 AM | Workflow status dashboard |
| Weekly Mon | Agent metrics dashboard |
| Weekly Wed | Performance benchmarks |
| Weekly Sun | Maintenance, code health, branch cleanup, lock threads |

## Key Configuration

| Setting | Value |
|---------|-------|
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
