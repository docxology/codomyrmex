# .github/ISSUE_TEMPLATE — AI Agent Guide

**Status**: Active | **Last Updated**: March 2026

## Purpose

Structured GitHub issue forms for bug reports, feature requests, documentation issues,
and Jules agent task dispatch.

## Template Inventory

| File | Type | Labels Applied |
|------|------|----------------|
| `bug_report.yml` | Bug report form | `bug`, `needs-triage` |
| `feature_request.yml` | Feature request form | `enhancement`, `needs-triage` |
| `documentation.yml` | Documentation issue form | `documentation`, `needs-triage` |
| `jules_task.yml` | Jules agent task dispatch | `jules`, `agent-task`, `automated` |

## AI Agent Guidelines

### When Creating Issues

- Use `gh issue create` with `--template` flag matching the appropriate template type
- Bug reports require: environment info, reproduction steps, expected vs actual behavior
- Feature requests require: problem statement, proposed solution, acceptance criteria
- Documentation issues require: affected doc file, description of inaccuracy or gap

### Jules Task Dispatch

- Use `jules_task.yml` for dispatching work to Jules AI agents
- Select target module(s) from the 28+ available options
- Choose task type: module improvement, bug fix, code health, tests, etc.
- Set priority (Low/Medium/High/Critical)
- Or use the batch dispatch: `gh workflow run jules-dispatch.yml`

### Naming Conventions

- Bug titles: `[Bug]: <brief description of unexpected behavior>`
- Feature titles: `[Feature]: <brief description of capability>`
- Docs titles: `[Docs]: <affected file or section> — <problem>`
- Jules titles: `[Jules]: <task type> — <module name>`
