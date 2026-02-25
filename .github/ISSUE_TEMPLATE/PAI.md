# .github/ISSUE_TEMPLATE — PAI Integration Guide

**Status**: Active | **Last Updated**: February 2026

## Purpose

PAI uses issue templates to file well-structured issues that meet project contribution standards.

## PAI Phase Mapping

| PAI Phase | Usage |
|-----------|-------|
| OBSERVE | Read existing issues via `gh issue list` to avoid duplicates |
| THINK | Select the correct template type based on the nature of the problem |
| PLAN | Draft issue content following the template structure |
| BUILD | Populate all required fields per the chosen template |
| EXECUTE | `gh issue create --title "..." --body "..." --label "..."` |
| VERIFY | Confirm issue created with correct labels and assignees |

## Template Quick Reference

```bash
# Bug report
gh issue create --title "[Bug]: <desc>" --label "bug,needs-triage"

# Feature request
gh issue create --title "[Feature]: <desc>" --label "enhancement,needs-triage"

# Documentation issue
gh issue create --title "[Docs]: <desc>" --label "documentation,needs-triage"
```

## Constraints

- Always check for duplicates before filing: `gh issue list --search "<keywords>"`
- Populate all required fields from the template (marked `required: true` in YAML)
- Do not create issues for problems that already have open PRs addressing them
