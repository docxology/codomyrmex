# Hermes Sentinel Recommendations Hub


**Version**: v0.1.0 | **Status**: Active | **Last Updated**: May 2026

This directory is an autonomous staging ground for **Hermes Sentinel** findings.

## Workflow

1. **Sentinel** monitors the codebase and saves `REC_YYYYMMDD_HHMMSS.md` files here every 5 minutes.
2. **Collaborating Agents** (or the User) review and triage these recommendations.
3. Valid recommendations are implemented, then the file is deleted.
4. Invalid or already-addressed recommendations are deleted immediately.

> [!IMPORTANT]
> The Sentinel uses a local LLM (`llama3.2`) which frequently hallucates non-existent
> files, tool flags, and concepts. **Always verify references before acting.**

See [AGENTS.md](AGENTS.md) for detailed triage rules and known hallucination patterns.

---
*Self-Aware Remediation Loop v2.4.0*

## Navigation

- **Self**: `README.md`
- **Parent**: [../README.md](../README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: `SPEC.md` is inherited from the nearest parent scope.
- **Repository Root**: [README.md](../README.md)
