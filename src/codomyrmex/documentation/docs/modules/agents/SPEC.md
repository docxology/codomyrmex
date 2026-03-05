# Agents -- Technical Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Agent Interface

- All agents shall implement `AgentInterface` with an `execute(request: AgentRequest) -> AgentResponse` method.
- Agents shall support configurable timeouts, retry counts, and context parameters.

### FR-2: Provider Integration

- The system shall support 13 agent providers across API-based, CLI-based, and local deployment models.
- Provider clients shall be lazy-loaded to avoid import failures when optional dependencies are not installed.
- Each provider shall report its availability status via the `AgentRegistry`.

### FR-3: Session Management

- The system shall maintain conversation history within sessions via `SessionManager`.
- Sessions shall support message logging with role (user/assistant/system) and content.
- Session data shall be retrievable by session ID.

### FR-4: Response Parsing

- The system shall parse structured responses including JSON, code blocks, and structured output.
- `parse_code_blocks()` shall extract all fenced code blocks from agent responses.
- `parse_json_response()` shall extract and parse JSON from agent responses.

### FR-5: Multi-Agent Orchestration

- `AgentOrchestrator` shall support task decomposition and delegation across multiple agents.
- Orchestration shall support sequential and parallel execution strategies.

### FR-6: Agent Registry

- `AgentRegistry` shall provide declarative agent catalog with live health probes.
- Registry shall support agent discovery, configuration, and instantiation.

## Interface Contracts

### AgentRequest

```python
@dataclass
class AgentRequest:
    prompt: str
    context: dict[str, Any] | None = None
    parameters: dict[str, Any] | None = None
```

### AgentResponse

```python
@dataclass
class AgentResponse:
    content: str
    error: str | None = None
    tokens_used: int = 0
    metadata: dict[str, Any] | None = None
```

### MCP Tool Signatures

```python
def execute_agent(agent_name: str, prompt: str) -> dict
def list_agents() -> dict
def get_agent_memory(session_id: str) -> dict
```

## Non-Functional Requirements

### NFR-1: Availability

- Provider unavailability shall be handled gracefully with status reporting, not exceptions.
- Lazy-loaded providers shall set their export to `None` when dependencies are missing.

### NFR-2: Extensibility

- New providers shall be addable by extending `APIAgentBase` or `CLIAgentBase`.
- No modifications to core framework required for new providers.

### NFR-3: Performance

- Agent listing shall complete within 1 second for all 13 providers.
- Session history retrieval shall return the last 50 messages for any session.

## Testing Requirements

- All tests follow the Zero-Mock policy.
- Tests use `InMemoryLLMClient` and real `BaseAgent` implementations (`ConcreteAgent`, `FailingAgent`).
- Provider-specific tests use `@pytest.mark.skipif` when provider dependencies are not installed.
- 350+ tests across the agent test suite.

## Navigation

- **Source**: [src/codomyrmex/agents/](../../../../src/codomyrmex/agents/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
