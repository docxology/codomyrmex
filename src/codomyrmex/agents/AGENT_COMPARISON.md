# Agent Comparison Guide

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

This document provides a comprehensive comparison of all available agents in the Codomyrmex agents module, helping you choose the right agent for your specific use case.

## Agent Categories

### CLI-based Agents

These agents execute via command-line tools installed on your system:

| Agent | Command | Provider | Key Features |
|-------|---------|----------|--------------|
| **jules** | `jules` | Jules CLI | Command-based execution, simple interface |
| **gemini** | `gemini` | Google | OAuth/API key auth, slash commands, @ file operations |
| **opencode** | `opencode` | OpenCode | Open-source alternative, CLI-based |
| **mistral_vibe** | `vibe`, `vibe-acp` | Mistral AI | Mistral models, vibe CLI tool |
| **every_code** | `code`, `coder` | Every Code | Multi-agent orchestration, special commands (/plan, /solve, /code, /auto), browser integration |

### API-based Agents

These agents integrate directly with provider APIs:

| Agent | Provider | Key Features |
|-------|----------|--------------|
| **claude** | Anthropic | Advanced reasoning, high-quality responses, API-based |
| **codex** | OpenAI | Code-focused models, OpenAI API integration |

## Detailed Comparison

### Jules (`jules`)

**Type**: CLI-based  
**Best For**: Simple command-based code generation tasks

**Features**:
- Command-based execution
- Simple interface
- Fast execution
- No API keys required (uses installed CLI)

**Limitations**:
- Limited to Jules CLI capabilities
- No advanced reasoning features

**Configuration**:
```python
from codomyrmex.agents.jules import JulesClient

client = JulesClient()
```

### Claude (`claude`)

**Type**: API-based  
**Best For**: High-quality code generation, complex reasoning tasks, production use

**Features**:
- Advanced reasoning capabilities
- High-quality code generation
- Direct API integration
- Streaming support
- Multi-turn conversations

**Limitations**:
- Requires API key (`ANTHROPIC_API_KEY`)
- API rate limits apply
- Cost per request

**Configuration**:
```python
from codomyrmex.agents.claude import ClaudeClient

client = ClaudeClient(config={
    "claude_api_key": "your-api-key",
    "claude_model": "claude-3-opus-20240229"
})
```

### Codex (`codex`)

**Type**: API-based  
**Best For**: Code-focused tasks, OpenAI ecosystem integration

**Features**:
- Code-focused models
- OpenAI API integration
- Streaming support
- Temperature control

**Limitations**:
- Requires API key (`OPENAI_API_KEY`)
- API rate limits apply
- Cost per request

**Configuration**:
```python
from codomyrmex.agents.codex import CodexClient

client = CodexClient(config={
    "codex_api_key": "your-api-key",
    "codex_model": "code-davinci-002"
})
```

### OpenCode (`opencode`)

**Type**: CLI-based  
**Best For**: Open-source alternative, local execution

**Features**:
- Open-source
- No API keys required
- CLI-based execution
- Local processing

**Limitations**:
- Limited to OpenCode CLI capabilities
- May have fewer features than commercial alternatives

**Configuration**:
```python
from codomyrmex.agents.opencode import OpenCodeClient

client = OpenCodeClient()
```

### Gemini (`gemini`)

**Type**: CLI-based  
**Best For**: Google ecosystem integration, file operations

**Features**:
- Google models
- OAuth or API key authentication
- Slash commands (/model, /settings, /chat)
- @ file operations
- Session management (save/resume chats)

**Limitations**:
- Requires Gemini CLI installation
- Authentication setup required

**Configuration**:
```python
from codomyrmex.agents.gemini import GeminiClient

client = GeminiClient(config={
    "gemini_api_key": "your-api-key",
    "gemini_auth_method": "api_key"  # or "oauth"
})
```

### Mistral Vibe (`mistral_vibe`)

**Type**: CLI-based  
**Best For**: Mistral AI models, vibe CLI tool integration

**Features**:
- Mistral AI models
- Vibe CLI tool (`vibe`, `vibe-acp` executables)
- API key authentication
- Streaming support

**Limitations**:
- Requires Mistral Vibe CLI installation
- Requires API key (`MISTRAL_API_KEY`)

**Configuration**:
```python
from codomyrmex.agents.mistral_vibe import MistralVibeClient

client = MistralVibeClient(config={
    "mistral_vibe_api_key": "your-api-key"
})
```

### Every Code (`every_code`)

**Type**: CLI-based  
**Best For**: Multi-agent orchestration, complex workflows, browser integration

**Features**:
- Multi-agent orchestration (can coordinate Claude, Gemini, GPT-5)
- Special commands:
  - `/plan`: Multi-agent consensus planning
  - `/solve`: Fastest agent problem solving
  - `/code`: Multi-agent code generation with worktrees
  - `/auto`: Auto Drive for multi-step tasks
  - `/chrome`: External browser integration
  - `/browser`: Internal headless browser
- Browser integration
- Theme system
- Enhanced reasoning controls

**Limitations**:
- Requires Every Code CLI installation
- More complex setup
- Requires API keys for underlying providers

**Configuration**:
```python
from codomyrmex.agents.every_code import EveryCodeClient

client = EveryCodeClient(config={
    "every_code_api_key": "your-api-key",
    "every_code_config_path": "~/.code"  # Optional
})
```

## Decision Matrix

### When to Use Each Agent

**Use Jules** when:
- You need simple, fast code generation
- You have Jules CLI installed
- You want minimal configuration

**Use Claude** when:
- You need high-quality code generation
- You have Anthropic API access
- You need advanced reasoning capabilities
- Production use cases

**Use Codex** when:
- You need code-focused models
- You have OpenAI API access
- You're already using OpenAI ecosystem

**Use OpenCode** when:
- You want an open-source solution
- You prefer local execution
- You don't want API dependencies

**Use Gemini** when:
- You need Google ecosystem integration
- You want file operations (@ commands)
- You need session management
- You have Gemini CLI installed

**Use Mistral Vibe** when:
- You need Mistral AI models
- You have Mistral Vibe CLI installed
- You want Mistral-specific features

**Use Every Code** when:
- You need multi-agent orchestration
- You want to coordinate multiple agents
- You need browser integration
- You want special commands (/plan, /solve, /code, /auto)
- You need complex workflow automation

## Capability Comparison

| Capability | Jules | Claude | Codex | OpenCode | Gemini | Mistral Vibe | Every Code |
|------------|-------|--------|-------|----------|--------|--------------|------------|
| Code Generation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Code Editing | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Code Analysis | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Text Completion | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Streaming | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Multi-turn | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Multi-agent | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Browser Integration | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| File Operations | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Session Management | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |

## Performance Considerations

- **CLI-based agents**: Generally faster for simple tasks, but require CLI installation
- **API-based agents**: More reliable, better for production, but subject to rate limits
- **Every Code**: Best for complex workflows but may be slower due to multi-agent coordination

## Cost Considerations

- **CLI-based (local)**: No API costs (jules, opencode)
- **CLI-based (with API)**: API costs apply (gemini, mistral_vibe, every_code)
- **API-based**: Direct API costs (claude, codex)

## Integration Examples

### Simple Code Generation
```python
# Use Jules for simple tasks
from codomyrmex.agents.jules import JulesClient
client = JulesClient()
response = client.execute(AgentRequest(prompt="Create a sort function"))
```

### High-Quality Code Generation
```python
# Use Claude for production-quality code
from codomyrmex.agents.claude import ClaudeClient
client = ClaudeClient(config={"claude_api_key": "key"})
response = client.execute(AgentRequest(prompt="Create a REST API"))
```

### Multi-Agent Orchestration
```python
# Use Every Code for complex workflows
from codomyrmex.agents.every_code import EveryCodeClient
client = EveryCodeClient()
response = client.execute(AgentRequest(prompt="/plan Refactor the authentication system"))
```

## Navigation

- **Parent**: [agents](README.md)
- **Agent Documentation**: See individual agent README files
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

