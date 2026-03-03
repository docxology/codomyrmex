# aider -- Agent Capabilities

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## When to Use Aider vs Direct Code Editing

| Scenario | Use Aider | Use Direct Edit |
|----------|-----------|-----------------|
| Need every change as a git commit | Yes | |
| Audit trail required | Yes | |
| Complex multi-file refactor | Yes (architect mode) | |
| Simple one-off edit | | Yes |
| Explaining code without changing it | Yes (ask mode) | Yes |
| Fast single-file edit | | Yes |
| Debugging with test execution | Yes (--auto-test) | Yes |
| Working over SSH/remote | Yes | Yes |

**Rule of thumb**: Use aider when you want git-native change tracking or when the task benefits from a two-model architect/editor workflow. Use direct editing for simple, fast changes.

## Mode Selection Guide

| Task | Mode | Tool |
|------|------|------|
| Apply code changes | code (default) | `aider_edit` |
| Complex refactoring requiring planning | architect | `aider_architect` |
| Code analysis, explanation, review | ask | `aider_ask` |
| Pre-flight check | -- | `aider_check` |
| Configuration inspection | -- | `aider_config` |

## Agent Access Matrix

### Engineer Agent

**Access**: Full
**Trust Level**: TRUSTED

| Capability | Tool / Method |
|---|---|
| Edit files with instruction | `aider_edit` |
| Complex refactoring | `aider_architect` |
| Code analysis | `aider_ask` |
| Pre-flight check | `aider_check` |
| Configuration | `aider_config` |

**Use Cases**: Refactoring code, adding features, fixing bugs with git-tracked changes, applying type hints or docstrings across files.

---

### Architect Agent

**Access**: Read + Architect
**Trust Level**: TRUSTED

| Capability | Tool / Method |
|---|---|
| Plan complex refactors | `aider_architect` |
| Analyze code structure | `aider_ask` |
| Check installation | `aider_check` |
| Review configuration | `aider_config` |

**Use Cases**: Planning large-scale refactoring, evaluating architecture changes before execution, code analysis without modification.

---

### QATester Agent

**Access**: Read-only
**Trust Level**: OBSERVED

| Capability | Tool / Method |
|---|---|
| Code analysis | `aider_ask` |
| Installation verification | `aider_check` |
| Configuration check | `aider_config` |

**Use Cases**: Verifying aider is properly configured, asking about code quality, reviewing changes made by aider.

---

### Security Agent

**Access**: Read-only
**Trust Level**: OBSERVED

| Capability | Tool / Method |
|---|---|
| Security analysis | `aider_ask` |
| Check configuration | `aider_config` |

**Use Cases**: Asking aider to analyze code for vulnerabilities, verifying no API keys are leaked in configuration.

---

## Trust Level Definitions

| Level | Operations Permitted |
|---|---|
| UNTRUSTED | None |
| OBSERVED | `aider_check`, `aider_config`, `aider_ask` (read-only) |
| TRUSTED | Full access -- `aider_edit`, `aider_architect` (file-modifying) |

---

## Multi-Agent Coordination

Claude Code orchestrates, aider executes edits. The typical flow:

```
Claude Code (PLAN) --> decides what to change
    |
    v
aider_check() --> verify aider installed
    |
    v
aider_edit() or aider_architect() --> apply changes via subprocess
    |
    v
git diff HEAD~1 --> Claude Code reviews aider's commit
    |
    v
Claude Code (VERIFY) --> runs tests, confirms correctness
```

**Safety protocol**:
1. Always call `aider_check()` before `aider_edit()` or `aider_architect()`
2. Never pass untrusted user input directly as `instruction` -- sanitize first
3. Review `returncode` in response -- `"0"` means success
4. Check `stderr` for warnings or errors even on success

## Error Handling

| Error | Cause | Agent Action |
|---|---|---|
| `AiderNotInstalledError` | `aider` binary not in PATH | Report to user; suggest `uv tool install aider-chat` |
| `AiderTimeoutError` | Subprocess exceeded timeout | Retry with higher timeout or smaller file set |
| `AiderAPIKeyError` | Missing API key for selected model | Check `aider_config()` for key presence |
| `returncode != "0"` | aider process failed | Read `stderr` for root cause |

All MCP tools catch exceptions and return `{"status": "error", "message": "..."}` -- agents never see raw exceptions.

---

## PAI Algorithm Phase Mapping

| Phase | Tools | Agent |
|-------|-------|-------|
| OBSERVE | `aider_check`, `aider_config` | All |
| THINK | `aider_ask` | Architect, Engineer |
| PLAN | `aider_architect` (planning pass) | Architect |
| BUILD | `aider_edit`, `aider_architect` | Engineer |
| EXECUTE | `aider_edit` | Engineer |
| VERIFY | `aider_ask`, `aider_check` | QATester |
| LEARN | -- | (git history serves as audit trail) |

---

## Security Constraints

1. API keys are never passed to subprocess -- aider reads them from environment variables directly.
2. `--no-auto-commits` is always applied -- Claude Code controls when commits happen.
3. `--yes` prevents interactive prompts that would hang the subprocess.
4. File paths are passed as positional arguments, not interpolated into shell strings.
