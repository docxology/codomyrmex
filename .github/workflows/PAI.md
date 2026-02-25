# .github/workflows — PAI Integration Guide

**Status**: Active | **Last Updated**: February 2026

## Purpose

GitHub Actions workflow definitions. PAI reads these to understand CI/CD state but
never modifies them autonomously on `main`.

## PAI Phase Mapping

| PAI Phase | Workflow | How PAI Uses It |
|-----------|----------|-----------------|
| OBSERVE | `ci.yml` | Determine if lint/tests currently pass; read matrix config |
| OBSERVE | `security.yml` | Check if security scanning is active and gates properly |
| THINK | `workflow-coordinator.yml` | Understand which paths trigger which workflows |
| PLAN | `release.yml` | Review versioning and publishing steps before release work |
| VERIFY | `ci.yml`, `security.yml` | Confirm gates pass after code changes |
| LEARN | `benchmarks.yml` | Parse performance regression artifacts |

## Key Behaviors

- All 10 workflows have `permissions: {}` top-level (deny-all default)
- `astral-sh/setup-uv@v5` is the standard across all workflows
- Cache restore step precedes `uv sync` in every job for maximum hit rate
- Windows matrix steps with bash syntax include `shell: bash`
- Security scans use `continue-on-error: true` to prevent blocking on external service issues

## Safe Operations for PAI

- Read any workflow YAML to understand triggers and job structure
- Use `gh workflow list` and `gh run list` to check current run status
- Use `gh run view <id>` to inspect specific workflow run logs

## Prohibited Operations

- Never push workflow changes directly to `main` or `develop`
- Never disable `permissions: {}` blocks or job-level `permissions:` grants
- Never change `if: always()` guards on summary/status jobs
- Never modify TruffleHog base/head refs without understanding push vs PR context
