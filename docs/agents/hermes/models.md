# Hermes Model Selection & OpenRouter

**Version**: v0.2.0 | **Last Updated**: March 2026

## Overview

Hermes is model-agnostic and routes LLM calls through configurable providers. OpenRouter is the recommended provider for access to many models through a single API key.

## Configuring the Model

```yaml
# config.yaml
model: nvidia/nemotron-3-super-120b-a12b:free
```

The model string follows OpenRouter's `provider/model-name` format.

## Providers

| Provider                  | Config Key              | Notes                               |
| :------------------------ | :---------------------- | :---------------------------------- |
| **OpenRouter**            | `OPENROUTER_API_KEY`    | Recommended — access to 100+ models |
| **Nous Portal**           | Auth via `hermes model` | Native Nous models                  |
| **OpenAI**                | `OPENAI_API_KEY`        | Direct OpenAI access                |
| **Any OpenAI-compatible** | Custom endpoint         | Ollama, vLLM, etc.                  |

### OpenRouter Setup

1. Get an API key at [openrouter.ai/keys](https://openrouter.ai/keys)
2. Add to `.env`:
    ```bash
    OPENROUTER_API_KEY=sk-or-v1-...
    ```
3. Set model in `config.yaml`:
    ```yaml
    model: nousresearch/hermes-3-llama-3.1-405b
    ```

### Listing Available Models

```bash
hermes model
```

## Model Categories

### Free Models (Good for Testing)

```yaml
model: nvidia/nemotron-3-super-120b-a12b:free
model: google/gemma-2-9b-it:free
model: meta-llama/llama-3.1-8b-instruct:free
```

### Recommended for Production

```yaml
# High quality reasoning
model: nousresearch/hermes-3-llama-3.1-405b

# Fast + capable
model: anthropic/claude-3.5-sonnet

# Cost-effective
model: google/gemini-2.0-flash
```

### Compression/Summary Models

For context compression, use a fast, inexpensive model:

```yaml
compression:
  summary_model: google/gemini-3-flash-preview
  # or
  summary_model: anthropic/claude-3-haiku
```

## Reasoning Effort

```yaml
agent:
    reasoning_effort: medium # low | medium | high
```

| Level      | Behavior                                             |
| :--------- | :--------------------------------------------------- |
| **low**    | Quick responses, minimal planning                    |
| **medium** | Balanced reasoning and tool use                      |
| **high**   | Deep reasoning with scratchpads and multi-step plans |

Higher reasoning effort adds structured thinking tags (`<SCRATCHPAD>`, `<PLAN>`) to the prompt, encouraging the model to think more carefully.

## Multi-Model Architecture

Hermes uses different models for different purposes:

```
Main Model (config.yaml: model)
  └── Primary conversation and tool use

Summary Model (compression.summary_model)
  └── Context compression and memory summarization

Vision Model (if configured)
  └── Image analysis and OCR
```

## Rate Limiting

OpenRouter has per-model rate limits. If you hit limits:

- Switch to a less popular model
- Add retry logic (Hermes handles this internally)
- Use multiple OpenRouter keys across instances

## Cost Optimization

1. **Use free models for testing** — `model:free` suffix models
2. **Use fast models for compression** — saves on token costs
3. **Lower max_turns** — reduce runaway conversations
4. **Enable compression** — reduces token usage in long conversations

## Related Documents

- [Configuration](configuration.md) — Full config reference
- [Sessions](sessions.md) — Compression and summary model usage
- [Personalities](personalities.md) — Custom personas
