# Agent Guidelines - LLM

**Version**: v0.4.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Large Language Model integration: providers, chains, and prompts.

## Key Classes

- **LLMClient** — Multi-provider LLM client
- **ChatSession** — Stateful conversations
- **PromptTemplate** — Template-based prompts
- **LLMChain** — Chained LLM operations

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

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
