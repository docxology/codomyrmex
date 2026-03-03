# Agents -- Agent Integration Guide

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Agent Capabilities

The Agents module provides the core framework for AI agent integration. It supports 13 provider clients, multi-agent orchestration, session management, and response parsing. Agents can execute tasks through any configured provider, list available agents, and retrieve session history.

## Available MCP Tools

### execute_agent

Execute an agent conversation with a given prompt through a named provider.

**Parameters:**
- `agent_name` (str, required) -- The name of the agent to execute (e.g., "claude", "gemini", "codex")
- `prompt` (str, required) -- The user input or instruction for the agent

**Returns:** Dictionary with status and the agent's response content.

**Agent Usage Pattern:**
```
Delegate a code generation task to a specific provider:
  execute_agent(agent_name="claude", prompt="Write a Python function to validate email addresses")
```

### list_agents

Return a list of all available AI agents with their descriptions and capabilities.

**Parameters:** None

**Returns:** Dictionary mapping agent IDs to their descriptions, capabilities, and availability status.

### get_agent_memory

Retrieve interaction logs and memory for a specific agent session.

**Parameters:**
- `session_id` (str, required) -- The ID of the session to retrieve

**Returns:** Dictionary containing the last 50 message logs for the session, with role and content for each message.

## Agent Interaction Patterns

### Provider Selection
When multiple agents are available, use `list_agents` to discover capabilities and select the appropriate provider based on task requirements (e.g., reasoning tasks to o1, code generation to claude or codex).

### Multi-Agent Orchestration
The `AgentOrchestrator` enables task decomposition across multiple agents. Each subtask can be routed to the most appropriate provider.

### Session Continuity
Use `get_agent_memory` to maintain context across interactions. Session history enables follow-up questions and iterative refinement.

## Trust Level

All three MCP tools are classified as **Safe** -- they do not modify files or execute arbitrary code on the host system.

## Supported Providers

| Provider | Type | Status |
|----------|------|--------|
| Claude | API | Active |
| Codex | API | Active |
| O1 | API | Lazy-loaded |
| DeepSeek | API | Lazy-loaded |
| Qwen | API | Lazy-loaded |
| Jules | CLI | Active |
| OpenCode | CLI | Active |
| OpenClaw | CLI | Active |
| Gemini | CLI | Active |
| Mistral Vibe | CLI | Active |
| Every Code | CLI | Active |
| agenticSeek | CLI | Lazy-loaded |
| Ollama | Local | Via llm module |

## Navigation

- **Source**: [src/codomyrmex/agents/](../../../../src/codomyrmex/agents/)
- **Extended README**: [README.md](readme.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Parent**: [All Modules](../README.md)
