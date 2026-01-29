# Codomyrmex Agents — scripts/agents

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Agent utility scripts for testing, orchestrating, and demonstrating the full capabilities of the Codomyrmex agent ecosystem.

## Active Components

| File | Lines | Description |
|------|-------|-------------|
| `agent_status.py` | 124 | System health and configuration discovery |
| `run_all_agents.py` | 112 | Execute all examples with results summary |
| `orchestrate.py` | 27 | Module-scoped script orchestration |
| `test_gemini_dispatch.py` | 129 | Gemini dispatch and orchestrator tests |
| `claude_code_demo.py` | ~100 | Claude Code methods demonstration |

## Method Inventory

### agent_status.py

| Function | Description |
|----------|-------------|
| `find_agents_configs()` | Discover AGENTS.md and config files |
| `parse_agents_md(path)` | Extract sections from AGENTS.md |
| `check_agent_health()` | Validate Python, codomyrmex, env vars |
| `main()` | CLI entry point with --list, --health flags |

### run_all_agents.py

| Function | Description |
|----------|-------------|
| `run_script(path)` | Execute script with timeout, capture output |
| `main()` | Run all examples, report pass/fail summary |

### test_gemini_dispatch.py

| Function | Description |
|----------|-------------|
| `test_gemini_client()` | Direct GeminiClient API test |
| `test_code_editor_gemini()` | CodeEditor generation and refactoring |
| `test_orchestrator_dispatch()` | Multi-agent parallel execution |

## Operating Contracts

1. **Graceful Degradation**: All scripts must exit with code 0 when API keys are missing
2. **Logging**: Use `codomyrmex.utils.cli_helpers` for consistent output
3. **Timeouts**: Default 120s per script execution
4. **Environment**: Respect `CODOMYRMEX_TEST_MODE=1` for light testing

## Navigation Links

- **📖 README**: [README.md](README.md)
- **📋 SPEC**: [SPEC.md](SPEC.md)
- **🤖 PAI**: [PAI.md](PAI.md)
- **📁 Parent**: [scripts](../README.md)
- **🏠 Root**: [../../README.md](../../README.md)
