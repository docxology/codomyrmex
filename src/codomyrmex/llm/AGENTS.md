# Agent Guidelines - LLM

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Large Language Model integration: providers, chains, and prompts.

## Key Classes

- **LLMClient** — Multi-provider LLM client
- **ChatSession** — Stateful conversations
- **PromptTemplate** — Template-based prompts
- **LLMChain** — Chained LLM operations

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `generate_text` | Generate text using a specified LLM provider and model (OpenRouter, Ollama) | Safe |
| `list_local_models` | List available local models managed by Ollama | Safe |
| `query_fabric_metadata` | Query configuration metadata for Microsoft Fabric integration | Safe |

## Agent Instructions

1. **Use templates** — Structured, reusable prompts
2. **Handle streaming** — Stream for long responses
3. **Token awareness** — Track token usage
4. **Error handling** — Retry on transient failures
5. **Cache responses** — Cache where appropriate

## Common Patterns

```python
from codomyrmex.llm import LLMClient, ChatSession, PromptTemplate

# Initialize client
client = LLMClient(provider="openai", model="gpt-4")

# Simple completion
response = client.complete("Explain quantum computing")

# Chat session
session = ChatSession(client)
session.add_system("You are a helpful coding assistant")
response = session.chat("How do I implement a binary tree?")
response = session.chat("Now add a delete method")  # Has context

# Prompt templates
template = PromptTemplate(
    "Summarize {document} in {num_sentences} sentences."
)
prompt = template.format(document=text, num_sentences=3)
summary = client.complete(prompt)

# Streaming
async for chunk in client.stream("Long response needed"):
    print(chunk, end="")
```

## Testing Patterns

```python
# Verify client with real provider
import os
client = LLMClient(provider="openai", model="gpt-4")
if os.getenv("OPENAI_API_KEY"):
    response = client.complete("Test")
    assert response is not None

# Verify template
template = PromptTemplate("Hello {name}")
prompt = template.format(name="World")
assert prompt == "Hello World"
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full LLM access | `generate_text`, `list_local_models`, `query_fabric_metadata` | TRUSTED |
| **Architect** | Model inventory | `list_local_models`, `query_fabric_metadata` | OBSERVED |
| **QATester** | Inference testing | `generate_text`, `list_local_models` | OBSERVED |
| **Researcher** | Read-only | `list_local_models`, `query_fabric_metadata` | OBSERVED |

### Engineer Agent
**Access**: Full — text generation, model listing, and Fabric metadata queries.
**Use Cases**: Invoking LLM inference during BUILD phase, generating code/docs with local Ollama models, selecting the right model tier for cost-performance tradeoffs.

### Architect Agent
**Access**: Model inventory — list available models and Fabric integration specs without running inference.
**Use Cases**: Evaluating which local models are available before Algorithm capability selection, reviewing Fabric metadata for integration architecture, capacity planning.

### QATester Agent
**Access**: Inference testing — run `generate_text` with controlled inputs to verify LLM behavior.
**Use Cases**: Confirming local model availability and responsiveness, regression testing prompt templates, verifying response format consistency.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
