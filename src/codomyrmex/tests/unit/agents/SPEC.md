# Agents Test Suite — Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Core Concept

The agents test suite validates the multi-provider agent framework using the Zero-Mock policy. All tests use `ConcreteAgent`, `FailingAgent`, `AsyncAgent`, and `FakeLLMClient` (defined in `conftest.py`) instead of `unittest.mock.MagicMock`.

## Test Coverage

| File | Scope |
|------|-------|
| `test_core_agents.py` | `BaseAgent`, `AgentInterface`, capabilities, request/response |
| `test_agents_core_config.py` | `AgentConfig`, env var fallbacks, key masking |
| `test_agents_core_session.py` | `SessionManager`, `AgentSession`, multi-turn context |
| `test_agents_core_tools.py` | `ToolRegistry`, function registration, invocation |
| `test_agents_core_orchestration.py` | `AgentOrchestrator`, workflow execution |
| `test_orchestration.py` | Basic orchestration patterns |
| `test_orchestration_advanced.py` | Advanced multi-agent workflows |
| `test_configuration.py` | Full configuration matrix |
| `test_error_handling.py` | Exception hierarchy, `FailingAgent` paths |
| `test_modularity.py` | Module isolation, import boundaries |
| `test_real_world_scenarios.py` | End-to-end agent workflow scenarios |
| `test_integrations.py` | Cross-module integration tests |
| `test_claude_client.py` | `ClaudeClient` instantiation, tools, sessions, pricing |
| `test_infrastructure_agent.py` | `InfrastructureAgent` operations |
| `test_git_agent.py` | `GitAgent` operations |
| `test_cli_configurations.py` | CLI agent configurations |
| `test_cli_orchestration.py` | CLI orchestration patterns |
| `test_react_agent.py` | `ReActAgent` reasoning loop |
| `test_ollama_agents_integration.py` | Ollama agent integration |
| `test_jules_integration.py` | Jules CLI integration |
| `test_opencode_integration.py` | OpenCode CLI integration |

## Modularity & Interfaces

- **Inputs**: Agent classes, `AgentRequest`, `AgentConfig`, environment variables
- **Outputs**: Test assertions validating correct behavior, error handling, state
- **Dependencies**: `pytest`, `codomyrmex.agents.core`, `codomyrmex.agents.claude`

## Zero-Mock Policy

Tests use concrete test implementations from `conftest.py`:

- `ConcreteAgent(BaseAgent)` — configurable response, tracks execution
- `FailingAgent(BaseAgent)` — always raises `AgentError`
- `AsyncAgent(BaseAgent)` — configurable delay for async testing
- `FakeLLMClient` — records calls, returns configurable responses

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Directory**: [unit](../README.md)
- **Repository Root**: [../../../../../README.md](../../../../../README.md)
