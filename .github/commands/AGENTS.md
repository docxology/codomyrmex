# .github/commands — AI Agent Guide

**Status**: Active | **Last Updated**: February 2026

## Purpose

TOML configuration files for Gemini AI-assisted GitHub workflows: PR review, issue triage,
and scheduled maintenance. These run as GitHub Actions steps using the `gemini` CLI.

## Command Inventory

| File | Purpose | Trigger |
|------|---------|---------|
| `gemini-review.toml` | Automated PR code review with severity ratings | PR opened/updated |
| `gemini-triage.toml` | Issue triage: label, assign, prioritize | Issue opened |
| `gemini-invoke.toml` | General invocation config for on-demand analysis | Manual dispatch |
| `gemini-scheduled-triage.toml` | Weekly batch triage of unlabeled issues | Scheduled |

## AI Agent Guidelines

### Safe Operations

- Read TOML configs to understand Gemini prompts and security constraints before any PR
- Understand that these are **not** part of the main CI system — they run independently
- Review configs when diagnosing why AI review comments appear or don't appear

### Key Security Constraints in gemini-review.toml

- Only comments on diff lines (not unchanged context)
- Never reveals its own instructions
- All GitHub interactions via MCP tools only
- No command substitution (`$(...)`) in generated shell commands
- Event type locked to `COMMENT` (never `APPROVE` or `REQUEST_CHANGES`)

### Do Not Modify Without Understanding

- Prompt changes affect all future PR reviews — test on a fork first
- Severity level definitions (`🔴🟠🟡🟢`) are calibrated; do not redefine without team discussion
- `INPUT DEMARCATION` constraints prevent prompt injection from PR content — preserve them
