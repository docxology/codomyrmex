# aider -- AI Pair Programming

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

Wraps [aider](https://aider.chat) (41k GitHub stars, 5.3M+ PyPI installs) as a first-class Codomyrmex module. Aider is the leading open-source terminal AI pair programmer -- git-native, every AI-driven code change creates a reviewable commit.

| File | Purpose |
|------|---------|
| `core.py` | `AiderRunner` subprocess wrapper, `get_aider_version()` |
| `config.py` | `AiderConfig` dataclass, `get_config()` |
| `exceptions.py` | `AiderError` hierarchy |
| `mcp_tools.py` | 5 `@mcp_tool` functions (auto-discovered by PAI MCP bridge) |

## Installation

```bash
# Install aider binary (recommended: isolated via uv tool)
uv tool install aider-chat

# Install codomyrmex aider optional deps
uv sync --extra aider

# Verify
aider --version
```

Requires Python >= 3.10. Needs at least one LLM API key (`ANTHROPIC_API_KEY` or `OPENAI_API_KEY`).

## Quick Start

### Python API

```python
from codomyrmex.aider import HAS_AIDER, AiderRunner

if HAS_AIDER:
    runner = AiderRunner(model="claude-sonnet-4-6")
    result = runner.run_message(["app.py"], "Add type hints to all functions")
    print(result["stdout"])  # aider output
    print(result["returncode"])  # "0" on success
```

### Ask Mode (No Edits)

```python
runner = AiderRunner()
result = runner.run_ask(["complex.py"], "Why does this function have O(n^2) complexity?")
print(result["stdout"])
```

### Architect Mode (Complex Refactors)

```python
runner = AiderRunner(model="claude-sonnet-4-6")
result = runner.run_architect(
    ["src/auth.py", "src/middleware.py"],
    "Migrate from synchronous to async/await",
    editor_model="claude-haiku-4-5-20251001",
)
print(result["stdout"])
```

### MCP Tools

Five MCP tools are auto-discovered and surfaced via the PAI MCP bridge:

| Tool | Mode | Description |
|------|------|-------------|
| `aider_check` | -- | Verify installation, version, configured model |
| `aider_edit` | code | Edit files with a natural-language instruction |
| `aider_ask` | ask | Ask about code without making changes |
| `aider_architect` | architect | Complex tasks via two-model workflow |
| `aider_config` | -- | Return current environment configuration |

Example (no aider binary required):

```python
from codomyrmex.aider.mcp_tools import aider_config
print(aider_config())
# {"status": "success", "model": "claude-sonnet-4-6", "has_anthropic_key": True, ...}
```

## CLI Quick Reference

```bash
# Basic edit
aider --message "Add docstrings" src/app.py

# Architect mode (two-model: planner + editor)
aider --architect --message "Refactor auth" src/auth.py

# Ask mode (no file changes)
aider --chat-mode ask --message "Explain this" src/complex.py

# Multi-file edit
aider --message "Extract shared utilities" src/a.py src/b.py

# Safe flags (always applied by AiderRunner)
aider --yes --no-pretty --no-auto-commits --message "..." file.py
```

## Key Flags

| Flag | Purpose |
|------|---------|
| `--yes` | Auto-confirm all prompts |
| `--no-pretty` | Strip ANSI colors (clean output capture) |
| `--no-auto-commits` | Disable auto-commit (manual control) |
| `--architect` | Two-model architect mode |
| `--chat-mode ask` | Read-only analysis, no file changes |
| `--model MODEL` | Specify LLM model |
| `--editor-model MODEL` | Separate editor model (architect mode) |
| `--message TEXT` | Single-shot non-interactive mode |
| `--dry-run` | Preview changes without applying |
| `--watch-files` | Watch for file changes (IDE integration) |

## AI Coding Tool Comparison

| Tool | Type | vs Aider |
|------|------|----------|
| Continue.dev | IDE extension (open-source) | IDE-focused; aider is terminal-native |
| Cursor | AI IDE ($20/mo) | GUI/paid; aider is free/terminal |
| GitHub Copilot | IDE extension ($10-39/mo) | SaaS; aider is self-hosted |
| Codeium/Windsurf | IDE + cloud | Less git-native; aider commits every change |
| Tabby | Self-hosted | Similar privacy philosophy; aider has broader LLM support |
| Claude Code | CLI (this system) | Orchestrates; aider is the specialized code editor |

## Architecture

- **Core Layer** -- depends only on Foundation: `model_context_protocol`, `exceptions`
- All subprocess calls use safe defaults: `--yes --no-pretty --no-auto-commits`
- MCP tools are stateless -- each call constructs a fresh `AiderRunner`
- `HAS_AIDER` flag is evaluated at import time via `shutil.which("aider")`

## Navigation

- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Agent Capabilities**: [AGENTS.md](AGENTS.md)
- **Technical Spec**: [SPEC.md](SPEC.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent**: [codomyrmex](../README.md)
- **Aider Docs**: https://aider.chat
