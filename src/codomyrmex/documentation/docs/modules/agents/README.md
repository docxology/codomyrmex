<!-- readme: generated -->

# agents

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/agents/`

## Overview

Agents Module for Codomyrmex.

This module provides integration with 13 agentic frameworks:

- **API-based**: Claude, Codex, O1, DeepSeek, Qwen (extend ``APIAgentBase``)
- **CLI-based**: Jules, OpenCode, OpenClaw, OpenFang, Gemini, Mistral Vibe, Every Code, agenticSeek (extend ``CLIAgentBase``)
- **Local**: Ollama (via ``llm/ollama/``)

Integration:
- Uses ``logging_monitoring`` for all logging
- Integrates with ``ai_code_editing`` for code generation workflows
- Integrates with ``llm`` for LLM infrastructure
- Integrates with ``code`` for safe code execution

Available classes:
- AgentInterface: Abstract base class for all agents
- AgentRequest, AgentResponse: Request/response data structures
- AgentCapabilities: Enum of agent capabilities
- AgentConfig: Configuration management for all 13 agents

Available submodules:
- agent_setup: Agent discovery, YAML config, interactive setup wizard
- generic: Base agent classes (APIAgentBase, CLIAgentBase, AgentOrchestrator)
- theory: Theoretical foundations for agentic systems
- claude, codex, o1, deepseek, qwen: API-based agent clients
- jules, opencode, gemini, mistral_vibe, every_code, openclaw, openfang, agentic_seek: CLI-based agent clients
- pooling: Multi-agent load balancing and failover
- evaluation: Agent benchmarking and quality metrics
- history: Conversation and context persistence

## Public Exports

`agents` exports 57 public symbols via `__all__`:

`APIAgentBase`, `AgentCapabilities`, `AgentConfig`, `AgentConfigurationError`, `AgentError`, `AgentEvaluator`, `AgentIntegrationAdapter`, `AgentInterface`, `AgentOrchestrator`, `AgentPool`, `AgentRegistry`, `AgentRequest`, `AgentResponse`, `AgentSession`, `AgentTimeoutError`, `AgenticSeekClient`, `BaseAgent`, `CLIAgentBase`, `ClaudeClient`, `CodeBlock`, `CodeEditor`, `CodexClient`, `ContextError`, `ConversationHistory` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../agents/](../../../../agents/)
