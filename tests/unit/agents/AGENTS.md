# Codomyrmex Agents — tests/unit/agents

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Purpose
Validation coverage, fixtures, and regression checks for Agents.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `agent_setup/` – Directory containing agent_setup components
- `agentic_seek/` – Directory containing agentic_seek components
- `ai_code_editing/` – Directory containing ai_code_editing components
- `claude/` – Directory containing claude components
- `cli/` – Directory containing cli components
- `conftest.py` – Project file
- `context/` – Directory containing context components
- `core/` – Directory containing core components
- `droid/` – Directory containing droid components
- `every_code/` – Directory containing every_code components
- `gemini/` – Directory containing gemini components
- `generic/` – Directory containing generic components
- `google_workspace/` – Directory containing google_workspace components
- `helpers.py` – Project file
- `jules/` – Directory containing jules components
- `learning/` – Directory containing learning components
- `meta/` – Directory containing meta components
- `mistral_vibe/` – Directory containing mistral_vibe components
- `openclaw/` – Directory containing openclaw components
- `openfang/` – Directory containing openfang components
- `pai/` – Directory containing pai components
- `planner/` – Directory containing planner components
- `pooling/` – Directory containing pooling components
- `py.typed` – Project file
- `qwen/` – Directory containing qwen components
- `specialized/` – Directory containing specialized components
- `test_agent_architectures.py` – Project file
- `test_agent_exceptions.py` – Project file
- `test_agent_lifecycle_zeromock.py` – Project file
- `test_agent_registry.py` – Project file
- `test_agent_setup_registry.py` – Project file
- `test_agents.py` – Project file
- `test_agents_core_config.py` – Project file
- `test_agents_core_orchestration.py` – Project file
- `test_agents_core_session.py` – Project file
- `test_agents_core_tools.py` – Project file
- `test_agents_hermes_client.py` – Project file
- `test_agents_perplexity_client.py` – Project file
- `test_claude_client.py` – Project file
- `test_claude_integration.py` – Project file
- `test_claude_mcp_tools.py` – Project file
- `test_cli_configurations.py` – Project file
- `test_cli_orchestration.py` – Project file
- `test_codex_mcp_tools.py` – Project file
- `test_configuration.py` – Project file
- `test_core_agents.py` – Project file
- `test_core_exceptions.py` – Project file
- `test_deepseek_mcp_tools.py` – Project file
- `test_droid_full.py` – Project file
- `test_editing_loop.py` – Project file
- `test_error_handling.py` – Project file
- `test_every_code_mcp_tools.py` – Project file
- `test_gemini_mcp_tools.py` – Project file
- `test_git_agent.py` – Project file
- `test_history_manager.py` – Project file
- `test_history_models.py` – Project file
- `test_history_stores.py` – Project file
- `test_infrastructure_agent.py` – Project file
- `test_integrations.py` – Project file
- `test_jules_integration.py` – Project file
- `test_llm_client.py` – Project file
- `test_mcp_bridge.py` – Project file
- `test_mcp_discovery.py` – Project file
- `test_mistral_vibe_mcp_tools.py` – Project file
- `test_modularity.py` – Project file
- `test_o1_mcp_tools.py` – Project file
- `test_ollama_agents_integration.py` – Project file
- `test_ollama_session.py` – Project file
- `test_openclaw_mcp_tools.py` – Project file
- `test_opencode_integration.py` – Project file
- `test_opencode_mcp_tools.py` – Project file
- `test_orchestration.py` – Project file
- `test_orchestration_advanced.py` – Project file
- `test_orchestrator.py` – Project file
- `test_pai_bridge.py` – Project file
- `test_react_agent.py` – Project file
- `test_real_world_scenarios.py` – Project file
- `test_run_todo_droid.py` – Project file
- `test_task_master.py` – Project file
- `test_task_planner.py` – Project file
- `test_trust_gateway.py` – Project file
- `test_trust_gateway_audit.py` – Project file
- `theory/` – Directory containing theory components
- `transport/` – Directory containing transport components

## Operating Contracts

- Tests that contact a live Ollama server are disabled by default. Set
  `RUN_LIVE_OLLAMA=1` explicitly for local service validation.
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `PAI.md`
- `README.md`
- `SPEC.md`
- `__init__.py`
- `conftest.py`
- `helpers.py`
- `py.typed`
- `test_agent_architectures.py`
- `test_agent_exceptions.py`
- `test_agent_lifecycle_zeromock.py`
- `test_agent_registry.py`
- `test_agent_setup_registry.py`
- `test_agents.py`
- `test_agents_core_config.py`
- `test_agents_core_orchestration.py`
- `test_agents_core_session.py`
- `test_agents_core_tools.py`
- `test_agents_hermes_client.py`
- `test_agents_perplexity_client.py`
- `test_claude_client.py`
- `test_claude_integration.py`
- `test_claude_mcp_tools.py`
- `test_cli_configurations.py`
- `test_cli_orchestration.py`
- `test_codex_mcp_tools.py`
- `test_configuration.py`
- `test_core_agents.py`
- `test_core_exceptions.py`
- `test_deepseek_mcp_tools.py`
- `test_droid_full.py`
- `test_editing_loop.py`
- `test_error_handling.py`
- `test_every_code_mcp_tools.py`
- `test_gemini_mcp_tools.py`
- `test_git_agent.py`
- `test_history_manager.py`
- `test_history_models.py`
- `test_history_stores.py`
- `test_infrastructure_agent.py`
- `test_integrations.py`
- `test_jules_integration.py`
- `test_llm_client.py`
- `test_mcp_bridge.py`
- `test_mcp_discovery.py`
- `test_mistral_vibe_mcp_tools.py`
- `test_modularity.py`
- `test_o1_mcp_tools.py`
- `test_ollama_agents_integration.py`
- `test_ollama_session.py`
- `test_openclaw_mcp_tools.py`
- `test_opencode_integration.py`
- `test_opencode_mcp_tools.py`
- `test_orchestration.py`
- `test_orchestration_advanced.py`
- `test_orchestrator.py`
- `test_pai_bridge.py`
- `test_react_agent.py`
- `test_real_world_scenarios.py`
- `test_run_todo_droid.py`
- `test_task_master.py`
- `test_task_planner.py`
- `test_trust_gateway.py`
- `test_trust_gateway_audit.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
