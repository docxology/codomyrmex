# Connecting PAI to Codomyrmex

**Difficulty**: Intermediate | **Time**: 30 min | **Last Updated**: February 2026

## Overview

This tutorial walks you through connecting the [PAI system](../../../PAI.md) (`~/.claude/skills/PAI/`) to codomyrmex via the Model Context Protocol (MCP). Once connected, PAI agents can use codomyrmex's 82 modules as tools during Algorithm execution.

## Prerequisites

Before starting:

- **PAI installed**: `~/.claude/skills/PAI/SKILL.md` exists
- **PAI configured**: `~/.claude/skills/PAI/settings.json` has your identity
- **Codomyrmex cloned**: This repository is on your machine
- **Python environment**: `uv sync` has been run in the codomyrmex directory
- **Claude Code**: Installed and working ([claude.ai/code](https://claude.ai/code))

Verify PAI is installed:

```bash
ls ~/.claude/skills/PAI/SKILL.md
# Should show the file
```

Verify codomyrmex is ready:

```bash
cd /path/to/codomyrmex
uv sync
uv run python -c "from codomyrmex.model_context_protocol import MCPServer; print('MCP module available')"
```

## Step 1: Start the Codomyrmex MCP Server

The MCP server exposes codomyrmex tools over a standardized protocol.

```bash
# List available tools first
python scripts/model_context_protocol/run_mcp_server.py --list-tools

# Start in stdio mode (required for Claude Desktop/Code integration)
python scripts/model_context_protocol/run_mcp_server.py --transport stdio
```

You should see tool categories: file operations, code analysis, shell execution, memory/knowledge, module info.

For development/debugging, use HTTP mode:

```bash
python scripts/model_context_protocol/run_mcp_server.py --transport http --port 8080
```

## Step 2: Register in Claude Desktop Config

Add the codomyrmex MCP server to your Claude Desktop configuration.

Edit `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "codomyrmex": {
      "command": "python",
      "args": [
        "/absolute/path/to/codomyrmex/scripts/model_context_protocol/run_mcp_server.py",
        "--transport", "stdio"
      ]
    }
  }
}
```

Replace `/absolute/path/to/codomyrmex/` with the actual path to your codomyrmex clone.

If you use `uv`, you may need:

```json
{
  "mcpServers": {
    "codomyrmex": {
      "command": "uv",
      "args": [
        "run", "--project", "/absolute/path/to/codomyrmex",
        "python", "scripts/model_context_protocol/run_mcp_server.py",
        "--transport", "stdio"
      ]
    }
  }
}
```

## Step 3: Verify the Bridge

Start a new Claude Code session in any project. If PAI is active (you see the `PAI ALGORITHM` header), the bridge is working when agents can access codomyrmex tools.

Quick verification:

1. Open Claude Code
2. Ask: "List all codomyrmex modules"
3. PAI should run the Algorithm and use `list_modules` from the MCP server
4. You should see the 82 module listing

If tools aren't appearing:

- Check `claude_desktop_config.json` syntax (valid JSON, correct paths)
- Verify the MCP server starts without errors: `python scripts/model_context_protocol/run_mcp_server.py --list-tools`
- Check server logs for connection attempts

## Step 4: Walk Through an Algorithm Cycle

With the bridge connected, try a task that exercises multiple Algorithm phases:

**Example prompt**: "Analyze the agents module for code quality issues"

Expected flow:

| Phase | What Happens | Codomyrmex Tools Used |
|-------|-------------|----------------------|
| **OBSERVE** | PAI reads your request, creates ISC criteria | `list_modules`, `search_files` |
| **THINK** | Selects capabilities (Engineer, static_analysis) | — (internal) |
| **PLAN** | Defines analysis approach | — (internal) |
| **BUILD** | Prepares analysis configuration | `read_file` |
| **EXECUTE** | Runs code analysis | `analyze_code`, `lint_check` |
| **VERIFY** | Checks ISC criteria against results | `security_scan` |
| **LEARN** | Captures patterns for future | `store_memory` |

## Step 5: Per-User Customization

### Your USER/ Directory

PAI stores personal configuration in `~/.claude/skills/PAI/USER/`. This is never committed to any repository. You can customize:

- `USER/AISTEERINGRULES.md` — Personal behavioral rules
- `USER/PROJECTS/PROJECTS.md` — Your project registry
- `USER/OPINIONS.md` — Preferences and relationship notes

### Skill Overrides

PAI skills in `~/.claude/skills/PAI/Skills/` can be customized. Each skill has its own `SKILL.md` defining triggers, workflows, and agents.

### Settings

Edit `~/.claude/skills/PAI/settings.json` to change:

```json
{
  "principal": {
    "name": "YourName",
    "timezone": "America/Los_Angeles"
  },
  "daidentity": {
    "name": "PAI",
    "displayName": "PAI",
    "voiceId": "your-preferred-voice"
  }
}
```

## Troubleshooting

| Issue | Solution |
|-------|---------|
| MCP server won't start | Run `uv sync` in codomyrmex directory, check Python version (3.10+) |
| Tools not appearing in Claude Code | Verify `claude_desktop_config.json` paths are absolute |
| "Module not found" errors | Ensure codomyrmex is installed: `uv sync --all-extras` |
| PAI Algorithm doesn't run | Check `~/.claude/skills/PAI/SKILL.md` exists and is loaded |
| Slow tool responses | Use stdio transport (not HTTP) for local sessions |

## What's Next

- **Explore modules**: Run `codomyrmex modules` to see all 82 modules
- **Read the bridge doc**: [`/PAI.md`](../../../PAI.md) maps Algorithm phases to modules
- **Agent integration**: [`src/codomyrmex/agents/PAI.md`](../../../src/codomyrmex/agents/PAI.md) details the three-tier agent mapping
- **MCP details**: [`src/codomyrmex/model_context_protocol/PAI.md`](../../../src/codomyrmex/model_context_protocol/PAI.md) covers the full MCP bridge architecture

## Navigation

- **Parent**: [Tutorials](README.md)
- **Root**: [Project Root](../../../README.md)
- **PAI Bridge**: [PAI.md](../../../PAI.md)
