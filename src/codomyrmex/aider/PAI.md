# Personal AI Infrastructure -- aider

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The aider module wraps the [aider](https://aider.chat) AI pair programming tool as codomyrmex MCP tools. Aider is git-native -- every AI-driven code change creates a reviewable commit -- making it ideal for the PAI BUILD and EXECUTE phases where code changes need audit trails.

## PAI Algorithm Phase Mapping

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Verify aider available; check configuration | `aider_check`, `aider_config` |
| **THINK** | Ask aider to explain code; no-edit analysis | `aider_ask` |
| **PLAN** | Architect mode planning for complex refactors | `aider_architect` (planning pass) |
| **BUILD** | Edit files per instruction | `aider_edit`, `aider_architect` |
| **EXECUTE** | Apply targeted code changes | `aider_edit` |
| **VERIFY** | Ask aider to review changes made; check results | `aider_ask`, `aider_check` |
| **LEARN** | -- | (aider stores git history as audit trail) |

## MCP Tools

| Tool | Category | Description |
|------|----------|-------------|
| `aider_check` | aider | Check installation status, version, model |
| `aider_edit` | aider | Edit files via code-mode instruction |
| `aider_ask` | aider | Ask questions without making changes |
| `aider_architect` | aider | Complex tasks via two-model architect mode |
| `aider_config` | aider | Return current environment configuration |

## Key Exports

- `AiderRunner` -- subprocess wrapper class
- `AiderConfig` -- environment-sourced config dataclass
- `HAS_AIDER` -- bool flag (True when aider binary in PATH)
- `get_aider_version()` -- returns installed version string
- Exception classes: `AiderError`, `AiderNotInstalledError`, `AiderTimeoutError`, `AiderAPIKeyError`

## Quick Start

```python
from codomyrmex.aider import HAS_AIDER, AiderRunner

if HAS_AIDER:
    runner = AiderRunner(model="claude-sonnet-4-6")
    result = runner.run_message(["app.py"], "Add type hints to all functions")
    print(result["stdout"])
```

## Directory Contents

- `core.py` -- AiderRunner class, get_aider_version()
- `config.py` -- AiderConfig dataclass, get_config()
- `exceptions.py` -- AiderError hierarchy
- `mcp_tools.py` -- 5 @mcp_tool functions (auto-discovered by PAI MCP bridge)

## Architecture Role

**Core Layer** -- Depends on `model_context_protocol` (Foundation). Provides AI pair programming capabilities that agent modules use during BUILD and EXECUTE phases. All interaction with aider is via subprocess -- no Python import of aider internals.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
