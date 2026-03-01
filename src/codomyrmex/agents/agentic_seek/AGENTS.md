# AI Agent Guidelines - agenticSeek

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.agents.agentic_seek`
**Status**: Active

## Purpose

Integration with [agenticSeek](https://github.com/Fosowl/agenticSeek)—a fully-local autonomous agent system for web browsing, code execution, and task planning.

## Agent Instructions

When working with this sub-module:

### Key Patterns

1. **Import Convention**:

   ```python
   from codomyrmex.agents.agentic_seek import AgenticSeekClient
   from codomyrmex.agents.agentic_seek import AgenticSeekRouter
   from codomyrmex.agents.agentic_seek import AgenticSeekCodeExecutor
   ```

2. **Error Handling**: All external calls (subprocess, Docker) are wrapped; catch `AgentError` from `codomyrmex.agents.core.exceptions`.

3. **Configuration**: Use `AgenticSeekClient.parse_config_ini()` to read `config.ini` files. The `AgenticSeekConfig` dataclass is frozen.

### Common Operations

- **Route a query**: `AgenticSeekRouter().classify_query(prompt)` → `AgenticSeekAgentType`
- **Extract code blocks**: `AgenticSeekCodeExecutor().extract(text)` → `list[CodeBlock]`
- **Parse a plan**: `AgenticSeekTaskPlanner().parse(text)` → `list[AgenticSeekTaskStep]`
- **Extract links**: `extract_links(text)` → `list[str]`

### Integration Points

- Integrates with: `agents.generic.CLIAgentBase` (parent class)
- Integrates with: `agents.core` (AgentCapabilities, AgentRequest, AgentResponse)
- Uses: `logging_monitoring` for all logging

## File Reference

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `agentic_seek_client.py` | Main CLI client |
| `agent_router.py` | Query-to-agent classification |
| `agent_types.py` | Enums and dataclasses |
| `code_execution.py` | Code block extraction and execution |
| `task_planner.py` | Plan parsing and ordering |
| `browser_automation.py` | Browser helpers |

## Troubleshooting

1. **Issue**: `AgentError: agenticSeek CLI not found`
   **Solution**: Clone the repo and set `agentic_seek_path` in config.

2. **Issue**: `AgentError: agenticSeek timed out`
   **Solution**: Increase `agentic_seek_timeout` in config (default: 300s).

3. **Issue**: Router misclassifies queries
   **Solution**: Be explicit in queries (e.g. "search the web for…" instead of "find…").
