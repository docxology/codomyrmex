# aider -- Agent Capabilities (Docs Summary)

**Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Overview

The aider module wraps the [aider](https://aider.chat) AI pair programming CLI. Agents use it when git-native code changes with audit trails are needed.

## When to Use Aider

- Every code change needs a git commit trail
- Complex multi-file refactoring (architect mode)
- Code analysis without modification (ask mode)
- Two-model workflows (architect plans, editor applies)

## MCP Tools

| Tool | Mode | Description | Trust |
|------|------|-------------|-------|
| `aider_check` | -- | Verify installation + version | OBSERVED |
| `aider_edit` | code | Edit files with instruction | TRUSTED |
| `aider_ask` | ask | Analyze code, no changes | OBSERVED |
| `aider_architect` | architect | Two-model complex refactoring | TRUSTED |
| `aider_config` | -- | Return environment configuration | OBSERVED |

## Agent Access

| Agent | Access Level | Key Tools |
|-------|-------------|-----------|
| Engineer | Full (TRUSTED) | All 5 tools |
| Architect | Read + Architect (TRUSTED) | `aider_architect`, `aider_ask`, `aider_check` |
| QATester | Read-only (OBSERVED) | `aider_ask`, `aider_check`, `aider_config` |
| Security | Read-only (OBSERVED) | `aider_ask`, `aider_config` |

## Safety Protocol

1. Always call `aider_check()` before `aider_edit()` or `aider_architect()`
2. API keys are read from environment -- never passed via parameters
3. `--no-auto-commits` is always applied -- Claude Code controls commits
4. Check `returncode` in response -- `"0"` means success

## Full Documentation

- **Detailed AGENTS.md**: [src/codomyrmex/aider/AGENTS.md](../../../src/codomyrmex/aider/AGENTS.md)
- **README**: [src/codomyrmex/aider/README.md](../../../src/codomyrmex/aider/README.md)
- **PAI Integration**: [src/codomyrmex/aider/PAI.md](../../../src/codomyrmex/aider/PAI.md)
