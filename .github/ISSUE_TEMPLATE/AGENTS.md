# .github/ISSUE_TEMPLATE — AI Agent Guide

**Status**: Active | **Last Updated**: February 2026

## Purpose

Structured GitHub issue forms for bug reports, feature requests, and documentation issues.

## Template Inventory

| File | Type | Labels Applied |
|------|------|----------------|
| `bug_report.yml` | Bug report form | `bug`, `needs-triage` |
| `feature_request.yml` | Feature request form | `enhancement`, `needs-triage` |
| `documentation.yml` | Documentation issue form | `documentation`, `needs-triage` |

## AI Agent Guidelines

### When Creating Issues

- Use `gh issue create` with `--template` flag matching the appropriate template type
- Bug reports require: environment info, reproduction steps, expected vs actual behavior
- Feature requests require: problem statement, proposed solution, acceptance criteria
- Documentation issues require: affected doc file, description of inaccuracy or gap

### Safe Operations

- Read template files to understand required fields before creating issues
- Use `gh issue list --label bug` to check for existing similar issues
- Reference templates when drafting issue content via `gh issue create --web`

### Naming Conventions

- Bug titles: `[Bug]: <brief description of unexpected behavior>`
- Feature titles: `[Feature]: <brief description of capability>`
- Docs titles: `[Docs]: <affected file or section> — <problem>`
