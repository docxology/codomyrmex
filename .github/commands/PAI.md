# .github/commands — PAI Integration Guide

**Status**: Active | **Last Updated**: February 2026

## Purpose

PAI reads Gemini command configs to understand the automated review/triage system.
PAI does not invoke these commands directly — they run via GitHub Actions.

## PAI Phase Mapping

| PAI Phase | Usage |
|-----------|-------|
| OBSERVE | Read TOML configs to understand what AI review is already providing |
| THINK | Assess if review coverage gaps exist (e.g., no security-focused review pass) |
| PLAN | Consider whether a new Gemini command config would fill a gap |
| VERIFY | Check if Gemini review comments on a PR align with PAI's own review findings |

## Understanding the Review System

The `gemini-review.toml` runs Gemini as a code reviewer on every PR. PAI should:
- **Complement** Gemini's review, not duplicate it
- **Focus** on architectural concerns Gemini may miss (cross-module impact, ISC coverage)
- **Escalate** to human review anything Gemini flags as `🔴` Critical

## Key Operational Notes

- Gemini reviews post as GitHub review comments (visible in PR Conversations tab)
- Commands run in isolated Actions environments with no access to repository secrets
- The `additional_context` env var in workflow steps customizes per-run focus areas
- `gemini-scheduled-triage.toml` runs weekly — check it when issues appear unlabeled

## Constraints

- Do not modify TOML prompts without testing on a fork — changes affect all future PRs
- Preserve all security constraints (input demarcation, scope limitation, tool exclusivity)
