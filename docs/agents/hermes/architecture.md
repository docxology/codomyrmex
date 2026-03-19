# Hermes Architecture

**Version**: v0.3.0 | **Last Updated**: March 2026 (73-commit update)

## Overview

Hermes employs a modular architecture centered on a core agent loop that integrates large language models with tools, memory, and multi-platform gateways. The system is designed around self-improvement: extracting skills from interactions, recalling context across sessions, and adapting to user patterns.

## Component Diagram

```mermaid
graph TD
    subgraph hermesAgent [Hermes agent]
        Gateway[Gateway<br/>gateway/]
        AgentLoop[Agent Loop<br/>run_agent.py]
        ToolRegistry[Tool Registry<br/>tools/]
        AuxClient[Auxiliary Client<br/>agent/auxiliary_client.py]
        SmartRoute[Smart Routing<br/>agent/smart_model_routing.py]

        Gateway <--> AgentLoop
        AgentLoop <--> ToolRegistry
        AgentLoop --> SmartRoute
        SmartRoute --> AuxClient

        Sessions[("Sessions<br/>state.db")]
        Skills[Skills<br/>skills/]
        Memory[("Memory<br/>memories/")]

        AgentLoop <--> Sessions
        AgentLoop <--> Skills
        AgentLoop <--> Memory
    end

    subgraph platforms [Platforms]
        TG([Telegram])
        WA([WhatsApp])
        DC([Discord])
        SL([Slack])
        HermesCLI([CLI])
    end

    subgraph llmProviders [LLM providers]
        OR([OpenRouter])
        NP([Nous Portal])
        CP([Copilot ACP])
        OA([OpenAI / BYOK])
    end

    TG --> Gateway
    WA --> Gateway
    DC --> Gateway
    SL --> Gateway
    HermesCLI --> Gateway
    AuxClient --> OR
    AuxClient --> NP
    AuxClient --> CP
    AuxClient --> OA
```

## Core Agent Loop

The agent loop in `run_agent.py` (`AIAgent._run_agent_loop()`) orchestrates the conversation cycle:

1. **Prompt Building** — `prompt_builder.py` assembles the system prompt from personality, skills, memory context, and session history
2. **LLM Inference** — Sends the assembled prompt to the configured model via OpenRouter or direct provider
3. **Tool Dispatch** — Parses tool calls from the model response and executes them via `registry.py`
4. **Result Integration** — Tool results are added back to the message history
5. **Compression Check** — If approaching context limits, `context_compressor.py` summarizes the conversation
6. **Persistence** — State saved to `state.db` and session JSON files

### Structured Reasoning

Hermes uses XML-tagged structured outputs for transparent reasoning:

- `<SCRATCHPAD>` — Working memory for multi-step reasoning
- `<INNER_MONOLOGUE>` — Internal reflection (not shown to user)
- `<PLAN>` — Step-labeled action plans
- `<tool_call>` / `<tool_response>` — Tool calling protocol

## Key Implementation Files

| File                              | Purpose                                       |
| :-------------------------------- | :-------------------------------------------- |
| `hermes_cli/config.py`            | HERMES_HOME resolution, config loading        |
| `hermes_cli/main.py`              | CLI entrypoint (+410 lines in v0.3.0)         |
| `gateway/run.py`                  | `GatewayRunner` — multi-platform daemon       |
| `gateway/session.py`              | Session routing and context management        |
| `run_agent.py`                    | Core `AIAgent` conversation loop              |
| `agent/prompt_builder.py`         | System prompt assembly                        |
| `agent/context_compressor.py`     | LLM-based context summarization               |
| `agent/auxiliary_client.py`       | Auxiliary LLM client (vision, compression)    |
| `agent/smart_model_routing.py`    | Automatic cheap/strong model routing          |
| `agent/model_metadata.py`         | Model capability/context/pricing metadata     |
| `agent/usage_pricing.py`          | Token cost tracking and budget management     |
| `agent/copilot_acp_client.py`     | GitHub Copilot ACP backend adapter (v0.3.0)   |
| `hermes_cli/copilot_auth.py`      | Copilot OAuth device-flow authentication      |
| `tools/registry.py`               | Central tool schema/handler registry          |
| `hermes_state.py`                 | SQLite + FTS5 state persistence               |

## HERMES_HOME Resolution

The critical path for config resolution is in `hermes_cli/config.py` line 37:

```python
return Path(os.getenv("HERMES_HOME", Path.home() / ".hermes"))
```

This single line determines where **all** data is read from: `.env`, `config.yaml`, `state.db`, `sessions/`, `skills/`, `memories/`, `logs/`, and `gateway.pid`.

## LLM Provider Backends (v0.3.0)

Hermes supports multiple LLM backends via a unified `auxiliary_client.py` facade:

| Backend | Config | Auth | Notes |
| :--- | :--- | :--- | :--- |
| **OpenRouter** | `OPENROUTER_API_KEY` | API key | Recommended; 200+ models |
| **Nous Portal** | OAuth | `hermes login` | Native Hermes models |
| **GitHub Copilot ACP** | `HERMES_COPILOT_ACP_COMMAND` | `hermes copilot login` | No structured tool calls |
| **OpenAI (BYOK)** | `OPENAI_API_KEY` | API key | Direct; full rate limits |
| **Anthropic (BYOK)** | `ANTHROPIC_API_KEY` | API key | Direct; full rate limits |
| **Z.AI / GLM** | `ZAI_API_KEY` | API key | — |
| **Kimi/Moonshot** | `KIMI_API_KEY` | API key | — |

### Smart Model Routing

The `smart_model_routing.py` module can automatically route short/simple messages to a cheaper model:

```yaml
smart_model_routing:
  enabled: true
  max_simple_chars: 160
  max_simple_words: 28
  cheap_model:
    provider: openrouter
    model: google/gemini-2.0-flash
```

## Deployment Backends

Hermes supports 6 execution backends for tool commands:

| Backend         | Use Case                            |
| :-------------- | :---------------------------------- |
| **local**       | Direct terminal execution (default) |
| **Docker**      | Isolated container execution        |
| **SSH**         | Remote server execution             |
| **Daytona**     | Serverless with hibernation         |
| **Singularity** | HPC/research environments           |
| **Modal**       | Cloud-native serverless             |

## Codomyrmex integration note

When Hermes is invoked via **Codomyrmex** (`HermesClient`), skill names for `hermes chat -s` can be supplied from a **project profile**, **client config**, **session metadata**, and **per-request MCP parameters** (merged in a fixed order). That layer is separate from the in-repo Hermes **tool** registry above. See [skills.md](skills.md) and [codomyrmex_integration.md](codomyrmex_integration.md).

## Related Documents

- [Gateway System](gateway.md) — Platform-specific routing
- [Sessions](sessions.md) — State persistence and compression
- [Tools](tools.md) — Tool registry and categories
- [Configuration](configuration.md) — `config.yaml` reference
- [Copilot ACP](copilot_acp.md) — GitHub Copilot backend
- [skills.md](skills.md) — Skill preload registry (Codomyrmex)
