# PAI-Codomyrmex Python API Reference

**Version**: v1.0.3-dev | **Last Updated**: February 2026

## Module: `codomyrmex.agents.pai`

All public API is importable from the top-level package:

```python
from codomyrmex.agents.pai import PAIBridge, TrustLevel, call_tool, verify_capabilities
```

## PAIBridge Class

**Location**: `pai_bridge.py`

The main bridge client. Discovers, validates, and provides access to all PAI subsystems.

```python
from codomyrmex.agents.pai import PAIBridge

bridge = PAIBridge()
```

### Discovery Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `is_installed` | `() -> bool` | `bool` | Check if PAI SKILL.md exists |
| `get_status` | `() -> dict` | `dict` | Full installation status with all component counts |
| `get_components` | `() -> dict` | `dict` | Component-by-component enumeration |

### Algorithm Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `get_algorithm_phases` | `() -> list[dict[str, str]]` | `list` | 7 Algorithm phases (static) |
| `get_algorithm_version` | `() -> str \| None` | `str \| None` | Version parsed from SKILL.md |
| `get_principles` | `() -> list[dict[str, str]]` | `list` | 16 PAI Principles (static) |
| `get_response_depth_levels` | `() -> list[dict[str, str]]` | `list` | FULL, ITERATION, MINIMAL |

### Subsystem Access Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `list_skills` | `() -> list[PAISkillInfo]` | Skills list | All skill packs |
| `get_skill_info` | `(name: str) -> PAISkillInfo` | Skill info | Single skill details |
| `list_tools` | `() -> list[PAIToolInfo]` | Tools list | All TypeScript CLI tools |
| `get_tool_info` | `(name: str) -> PAIToolInfo` | Tool info | Single tool details |
| `list_hooks` | `() -> list[PAIHookInfo]` | Hooks list | All hooks (active + archived) |
| `list_active_hooks` | `() -> list[PAIHookInfo]` | Hooks list | Active hooks only |
| `get_hook_info` | `(name: str) -> PAIHookInfo` | Hook info | Single hook details |
| `list_agents` | `() -> list[PAIAgentInfo]` | Agents list | Agent personality definitions |
| `get_agent_info` | `(name: str) -> PAIAgentInfo` | Agent info | Single agent details |
| `list_memory_stores` | `() -> list[PAIMemoryStore]` | Stores list | Memory subdirectories |
| `get_memory_info` | `(store: str) -> PAIMemoryStore` | Store info | Single store details |

### Configuration Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `get_security_config` | `() -> dict` | `dict` | Security system status |
| `get_telos_files` | `() -> list[str]` | `list` | TELOS identity/goals files |
| `get_settings` | `() -> dict` | `dict` | Parsed settings.json |
| `get_pai_env` | `() -> dict[str, str]` | `dict` | PAI environment variables |
| `get_mcp_registration` | `() -> dict` | `dict` | MCP server config |
| `has_codomyrmex_mcp` | `() -> bool` | `bool` | Codomyrmex MCP registered |

## TrustRegistry Class

**Location**: `trust_gateway.py`

In-memory trust ledger for MCP tool access control. Persists to `~/.codomyrmex/trust_ledger.json`.

```python
from codomyrmex.agents.pai import TrustRegistry

registry = TrustRegistry()
```

### Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `level` | `(tool_name: str) -> TrustLevel` | Trust level | Current trust level |
| `verify_all_safe` | `() -> list[str]` | Promoted names | Promote safe tools to VERIFIED |
| `trust_tool` | `(tool_name: str) -> TrustLevel` | New level | Promote one tool to TRUSTED |
| `trust_all` | `() -> list[str]` | Promoted names | Promote all tools to TRUSTED |
| `is_at_least_verified` | `(tool_name: str) -> bool` | `bool` | VERIFIED or TRUSTED? |
| `is_trusted` | `(tool_name: str) -> bool` | `bool` | TRUSTED? |
| `get_report` | `() -> dict[str, Any]` | Report dict | Full trust state |
| `reset` | `() -> None` | `None` | Reset all to UNTRUSTED |

## TrustLevel Enum

```python
from codomyrmex.agents.pai import TrustLevel

TrustLevel.UNTRUSTED  # "untrusted"
TrustLevel.VERIFIED   # "verified"
TrustLevel.TRUSTED    # "trusted"
```

## Module-Level Functions

### MCP Bridge Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `create_codomyrmex_mcp_server` | `(*, name="codomyrmex-mcp-server", transport="stdio") -> MCPServer` | Create MCP server with all tools |
| `get_tool_registry` | `() -> MCPToolRegistry` | Pre-populated tool registry (static + dynamic) |
| `get_skill_manifest` | `() -> dict[str, Any]` | PAI-compatible skill manifest |
| `call_tool` | `(name: str, **kwargs) -> dict[str, Any]` | Direct Python tool invocation |

### Trust Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `verify_capabilities` | `() -> dict[str, Any]` | Full audit, promotes safe tools to VERIFIED |
| `trust_tool` | `(tool_name: str) -> dict[str, Any]` | Promote single tool to TRUSTED |
| `trust_all` | `() -> dict[str, Any]` | Promote all tools to TRUSTED |
| `trusted_call_tool` | `(name: str, **kwargs) -> dict[str, Any]` | Trust-gated tool execution |
| `get_trust_report` | `() -> dict[str, Any]` | Current trust state |
| `is_trusted` | `(tool_name: str) -> bool` | Check trust status |
| `reset_trust` | `() -> None` | Reset all to UNTRUSTED |

## Dataclasses

### PAIConfig

Filesystem path layout for the PAI installation.

| Property | Type | Path |
|----------|------|------|
| `pai_root` | `Path` | `~/.claude/skills/PAI` |
| `skill_md` | `Path` | Algorithm SKILL.md |
| `skills_dir` | `Path` | `~/.claude/skills/` |
| `tools_dir` | `Path` | `~/.claude/skills/PAI/Tools/` |
| `agents_dir` | `Path` | `~/.claude/agents/` |
| `memory_dir` | `Path` | `~/.claude/MEMORY/` |
| `hooks_dir` | `Path` | `~/.claude/hooks/` |
| `security_dir` | `Path` | `~/.claude/skills/PAI/PAISECURITYSYSTEM/` |
| `telos_dir` | `Path` | `~/.claude/USER/` |
| `components_dir` | `Path` | `~/.claude/skills/PAI/Components/` |

### PAISkillInfo

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Skill pack name |
| `path` | `str` | Skill directory path |
| `has_skill_md` | `bool` | SKILL.md exists |
| `has_tools` | `bool` | Tools/ directory exists |
| `has_workflows` | `bool` | Workflows/ directory exists |
| `file_count` | `int` | Number of files in skill |

### PAIToolInfo

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Tool filename |
| `path` | `str` | Full file path |
| `size_bytes` | `int` | File size in bytes |

### PAIHookInfo

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Hook filename |
| `path` | `str` | Full file path |
| `size_bytes` | `int` | File size in bytes |
| `is_archived` | `bool` | In archive directory |

### PAIAgentInfo

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Agent name (from filename) |
| `path` | `str` | Full file path |
| `size_bytes` | `int` | File size in bytes |

### PAIMemoryStore

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Store directory name |
| `path` | `str` | Full directory path |
| `item_count` | `int` | Number of items in store |

## Constants

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `ALGORITHM_PHASES` | `list[dict[str, str]]` | 7 phases | OBSERVE through LEARN |
| `RESPONSE_DEPTH_LEVELS` | `list[dict[str, str]]` | 3 levels | FULL, ITERATION, MINIMAL |
| `PAI_PRINCIPLES` | `list[dict[str, str]]` | 16 principles | Core PAI principles |
| `PAI_UPSTREAM_URL` | `str` | GitHub URL | Upstream repository |
| `TOOL_COUNT` | `int` | 18 | Static tool count |
| `RESOURCE_COUNT` | `int` | 2 | Resource count |
| `PROMPT_COUNT` | `int` | 10 | Prompt count |
| `DESTRUCTIVE_TOOLS` | `frozenset[str]` | 4 tools | Tools requiring TRUSTED |

## Navigation

- **Index**: [README.md](README.md)
- **Architecture**: [architecture.md](architecture.md)
- **Tools**: [tools-reference.md](tools-reference.md)
- **Workflows**: [workflows.md](workflows.md)
