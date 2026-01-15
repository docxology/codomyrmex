# Agents Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: January 2026

## 1. Overview
The `agents` module is the core framework for AI agent integration in Codomyrmex. It provides abstract interfaces, concrete client implementations for various LLM backends (Jules, Claude, OpenAI), and parsing utilities.

## 2. Core Components

### 2.1 Base Classes
- **`AgentInterface`**: The protocol that all agents must implement.
- **`BaseAgent`**: Common functionality for all agents.
- **`APIAgentBase`**: Base for HTTP API-based agents.
- **`CLIAgentBase`**: Base for CLI wrapper agents.

### 2.2 Concrete Implementations
- **`JulesClient`**: Interface for the Jules CLI.
- **`ClaudeClient`**: Interface for Anthropic's Claude.
- **`CodexClient`**: Interface for OpenAI Codex.
- **`MistralVibeClient`**: Interface for Mistral Vibe.

### 2.3 Utilities
- **`CodeEditor`**: Helper for AI-driven code modifications.
- **`parse_json_response`**: Extracts JSON from LLM output.
- **`parse_code_blocks`**: Extracts markdown code blocks.
- **`clean_response`**: Sanitizes raw LLM text.

### 2.4 Data Structures
- **`AgentRequest`**: Encapsulates input prompt and context.
- **`AgentResponse`**: Encapsulates output text and metadata.
- **`AgentConfig`**: Configuration settings.

## 3. Usage Example

```python
from codomyrmex.agents import JulesClient, AgentRequest

client = JulesClient()
request = AgentRequest(prompt="Write a fibonacci function in Python")
response = client.execute(request)

print(response.content)
```
