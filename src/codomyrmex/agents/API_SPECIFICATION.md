# Agents Module API Specification

**Version**: v0.2.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `agents` module is the core framework for AI agent integration in Codomyrmex. It provides abstract interfaces, concrete client implementations for 11 providers, response parsing utilities, multi-agent pooling, evaluation, and conversation history.

## 2. Core Components

### 2.1 Base Classes

- **`AgentInterface`**: The protocol that all agents must implement
- **`BaseAgent`**: Common functionality (execute, validate, test_connection)
- **`APIAgentBase`**: Base for HTTP API-based agents (error handling, token extraction, client init)
- **`CLIAgentBase`**: Base for CLI wrapper agents (subprocess execution, streaming, health checks)

### 2.2 Provider Clients

#### API-based (extend `APIAgentBase`)

| Client | Module | Provider | Default Model | Env Var |
| :--- | :--- | :--- | :--- | :--- |
| `ClaudeClient` | `claude/` | Anthropic | `claude-3-opus-20240229` | `ANTHROPIC_API_KEY` |
| `CodexClient` | `codex/` | OpenAI | `code-davinci-002` | `OPENAI_API_KEY` |
| `O1Client` | `o1/` | OpenAI | `o1` | `OPENAI_API_KEY` |
| `DeepSeekClient` | `deepseek/` | DeepSeek | `deepseek-coder` | `DEEPSEEK_API_KEY` |
| `QwenClient` | `qwen/` | Alibaba | `qwen-coder-plus` | `DASHSCOPE_API_KEY` |

#### CLI-based (extend `CLIAgentBase`)

| Client | Module | Binary | Features |
| :--- | :--- | :--- | :--- |
| `JulesClient` | `jules/` | `jules` | Command-based execution |
| `OpenCodeClient` | `opencode/` | `opencode` | Open-source CLI |
| `GeminiClient` | `gemini/` | `gemini` | OAuth/API key, slash commands, @ files |
| `MistralVibeClient` | `mistral_vibe/` | `vibe` | Mistral AI models |
| `EveryCodeClient` | `every_code/` | `code` | Multi-agent orchestration, browser |

#### Local

| Provider | Module | Access | Features |
| :--- | :--- | :--- | :--- |
| Ollama | `llm/ollama/` | HTTP to `localhost:11434` | Local model management, execution |

### 2.3 Infrastructure

- **`AgentPool`** (`pooling/`): Load balancing, circuit breakers, failover
- **`AgentBenchmark`** (`evaluation/`): Scoring, test cases, composite metrics
- **`ConversationManager`** (`history/`): In-memory, file, SQLite stores
- **`AgentRegistry`** (`agent_setup/`): Declarative catalog, live probes, YAML persistence

### 2.4 Utilities

- **`CodeEditor`**: AI-driven code modifications
- **`parse_json_response`**: Extracts JSON from LLM output
- **`parse_code_blocks`**: Extracts markdown code blocks
- **`parse_structured_output`**: Key-value field extraction
- **`clean_response`**: Sanitizes raw LLM text

### 2.5 Data Structures

- **`AgentRequest`**: Encapsulates input prompt, context, and parameters
- **`AgentResponse`**: Encapsulates output text, error, metadata, tokens, execution time
- **`AgentConfig`**: Configuration dataclass with env var fallbacks for all 11 agents
- **`AgentCapabilities`**: Enum (CODE_GENERATION, CODE_EDITING, CODE_ANALYSIS, TEXT_COMPLETION, STREAMING, MULTI_TURN)

## 3. Interface Contract

```python
class AgentInterface(ABC):
    def execute(self, request: AgentRequest) -> AgentResponse: ...
    def stream(self, request: AgentRequest) -> Iterator[str]: ...
    def setup(self) -> None: ...
    def test_connection(self) -> bool: ...
```

## 4. Usage Examples

### Basic execution

```python
from codomyrmex.agents import ClaudeClient, AgentRequest

client = ClaudeClient()
request = AgentRequest(prompt="Write a fibonacci function in Python")
response = client.execute(request)
print(response.content)
```

### Agent discovery

```python
from codomyrmex.agents.agent_setup import AgentRegistry

registry = AgentRegistry()
for result in registry.probe_all():
    print(f"{result.name}: {result.status}")
```

### Setup wizard

```bash
uv run python -m codomyrmex.agents.agent_setup
```

## 5. Exception Hierarchy

```text
AgentError (base)
├── AgentTimeoutError
├── AgentConfigurationError
├── ExecutionError
├── ToolError
├── ContextError
├── SessionError
├── JulesError
├── ClaudeError
├── CodexError
├── OpenCodeError
├── GeminiError
├── MistralVibeError
└── EveryCodeError
```

## 6. Navigation

- **README**: [README.md](README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **Comparison**: [AGENT_COMPARISON.md](AGENT_COMPARISON.md)
